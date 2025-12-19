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


PROVIDER = "gemini"   # "openai" | "gemini" | "deepseek"
MODEL = "deepseek-chat" 
K = 5

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
    logger = lg.new_run_logger( out_dir="logs", prefix=f"{PROVIDER}_{MODEL}", meta={"provider": PROVIDER, "model": MODEL, "k": K},)

    csv = ipt.parse_csv("data/r1/seeds.csv")
    csv = ipt.parse_message_sequence(csv)

    row = csv.iloc[0]
    variants = fm.fuzz_r1(row, k=K)

    params = {
        "system_prompt": "You are a helpful assistant.",
        "deepseek": {},
        "openai": {},
        "gemini": {},
    }

    for _, variant in enumerate(variants, start=1):
        logger.write("variant_start", {
            "seed_id": variant.get("seed_id"),
            "variant_id": variant.get("variant_id"),
            "meta": variant.get("meta", {}),
            "messages": variant.get("messages", []),
        })

        try:
            payload, result = execute_one(variant, PROVIDER, MODEL, params)

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

        except Exception as e:
            logger.write("variant_error", {
                "seed_id": variant.get("seed_id"),
                "variant_id": variant.get("variant_id"),
                "status": "error",
                "error_msg": str(e),
            })

        time.sleep(0.6)

    logger.write("run_end", {"status": "done"})
        


if __name__ == "__main__":
    main()



