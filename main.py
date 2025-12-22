import os
import sys
from dotenv import load_dotenv
import time
load_dotenv()
sys.path.append(os.path.abspath("ethical_fuzzing/src/"))
import src.input_gen as ipt
import src.formatter as fmt
import src.exec_module as exe
import src.fuzzer_modules.r1 as fm
import src.logger as lg
import src.evaluator as ev


PROVIDER_MODEL = {"gemini": "gemini-3-flash-preview", "openai": "gpt-5.2", "deepseek": "deepseek-chat"}   # "openai" | "gemini" | "deepseek"
K = 20

def execute_one(variant, provider: str, model: str, params: dict):
    turns = fmt.normalize_to_turns(variant["messages"], system_prompt=params.get("system_prompt"))

    if provider == "openai":
        payload = fmt.format_openai(model, turns, **params.get("openai", {}))
        return payload, exe.run_openai(model, payload["input"], **params.get("openai", {}))

    if provider == "deepseek":
        payload = fmt.format_deepseek(model, turns, **params.get("deepseek", {}))
        return payload, exe.run_deepseek(model, payload["messages"], **params.get("deepseek", {}))

    if provider == "gemini":
        payload = fmt.format_gemini(model, turns, **params.get("gemini", {}))
        return payload, exe.run_gemini(model, payload["contents"], **params.get("gemini", {}))

    raise ValueError(f"Unknown provider: {provider}")


def main(): 
    csv = ipt.parse_csv("data/r1/seeds.csv")
    csv = ipt.parse_message_sequence(csv)
    variant_cache = {}

    for row in csv.itertuples():
        variant_cache[row.seed_id] = fm.fuzz_r1(row, k=K)
        print(f"finished writing variants for {row.seed_id}")

    params = {
                "system_prompt": "You are a helpful assistant.",
                "deepseek": {},
                "openai": {},
                "gemini": {},
            }
        

    for provider, model in PROVIDER_MODEL.items():
        output_csv = ev.OutputCsv()
        logger = lg.new_run_logger( out_dir="logs", prefix=f"{provider}_{model}", meta={"provider": provider, "model": model, "k": K},)

        for row in csv.itertuples():
            print(f"Executing fuzzing module for model {model} and seed {row.seed_id}...")

            variants = variant_cache[row.seed_id]

            for _, variant in enumerate(variants, start=1):
                logger.write("variant_start", {
                    "seed_id": variant.get("seed_id"),
                    "variant_id": variant.get("variant_id"),
                    "meta": variant.get("meta", {}),
                    "messages": variant.get("messages", []),
                })

                try:
                    payload, result = execute_one(variant, provider, model, params)

                    logger.write("variant_result", {
                        "seed_id": variant.get("seed_id"),
                        "variant_id": variant.get("variant_id"),
                        "provider": result.get("provider"),
                        "model": result.get("model"),
                        "request": payload,
                        "text": result.get("text"),
                        "raw_preview": lg.safe_preview(result.get("raw")),
                        "status": "ok",
                    })

                    output_csv.add_to_run([result.get("provider"), result.get("model"), variant.get("seed_id"), variant.get("variant_id"), variant.get("meta", {}).get("canary_type"), variant.get("meta", {}).get("canary_id"), variant.get("meta", {}).get("canary_surface"), variant.get("messages"), result.get("text"), "-", "0"])
                    print(f"variant {variant["variant_id"]} finished")

                except Exception as e:
                    logger.write("variant_error", {
                        "seed_id": variant.get("seed_id"),
                        "variant_id": variant.get("variant_id"),
                        "status": "error",
                        "error_msg": str(e),
                    })
                    print(f"error: {str(e)}")
                
                time.sleep(0.6)
            print(f"Finished fuzzing for seed {row.seed_id}")
        logger.write("run_end", {"status": "done"})
        output_csv.persist(logger.run_id)


if __name__ == "__main__":
    main()



