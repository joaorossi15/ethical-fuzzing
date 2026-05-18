import os
import sys
from dotenv import load_dotenv
import time
load_dotenv()
sys.path.append(os.path.abspath("ethical_fuzzing/src/"))
import src.formatter as fmt
import src.exec_module as exe
import src.logger as lg
import src.evaluator as ev

RISK = os.environ.get("RISK", "r1") 
K = 1
# PROVIDER_MODEL = {"gemini": "gemini-3-flash-preview", "openai": "gpt-5.2", "deepseek": "deepseek-chat"}   # "openai" | "gemini" | "deepseek"enai" | "gemini" | "deepseek"
PROVIDER_MODEL = {"openai": "gpt-5.2"}   # "openai" | "gemini" | "deepseek"


def canary_output_row(result, variant):
    meta = variant.get("meta", {})
    return [
        result.get("provider"),
        result.get("model"),
        variant.get("seed_id"),
        variant.get("variant_id"),
        meta.get("canary_type"),
        meta.get("canary_id"),
        meta.get("canary_surface"),
        variant.get("messages"),
        result.get("text"),
        "-",
        "0",
    ]


def reid_output_row(result, variant):
    meta = variant.get("meta", {})
    return [
        result.get("provider"),
        result.get("model"),
        variant.get("seed_id"),
        variant.get("variant_id"),
        meta.get("profile_id"),
        meta.get("hidden_identity"),
        meta.get("protected_identifiers"),
        meta.get("metamorphic_relation"),
        meta.get("probe_style"),
        variant.get("messages"),
        result.get("text"),
        "-",
        "0",
    ]

def load_risk_config(risk: str):
    if risk == "r1":
        import src.fuzzer_modules.canary.input_gen_canary as ipt_can
        import src.fuzzer_modules.canary.r1 as fm

        csv = ipt_can.parse_csv("data/r1/seeds.csv")
        csv = ipt_can.parse_message_sequence(csv)

        return {
            "risk_id": "r1",
            "rows": list(csv.itertuples()),
            "fuzz": lambda row: fm.fuzz_r1(row, k=K),
            "output_csv": ev.CanaryOutputCsv,
            "to_output_row": canary_output_row,
        }

    if risk == "reid":
        import src.fuzzer_modules.reid.input_gen_reid as ipt_reid
        import src.fuzzer_modules.reid.r_reid as fr

        rows = ipt_reid.load_reid_seeds("data/reid/profiles.yaml")

        return {
            "risk_id": "reid",
            "rows": rows,
            "fuzz": lambda row: fr.fuzz_reid(row, k=K),
            "output_csv": ev.ReidOutputCsv,
            "to_output_row": reid_output_row,
        }

    raise ValueError(f"Unknown risk: {risk}")

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
    risk_cfg = load_risk_config(RISK)
    rows = risk_cfg["rows"]

    variant_cache = {}

    for row in rows:
        variant_cache[row.seed_id] = risk_cfg["fuzz"](row)
        print(f"finished writing variants for {row.seed_id}")

    params = {
        "system_prompt": "You are a helpful assistant.",
        "deepseek": {},
        "openai": {},
        "gemini": {},
    }

    for provider, model in PROVIDER_MODEL.items():
        output_csv = risk_cfg["output_csv"]()
        logger = lg.new_run_logger(
            out_dir="logs",
            prefix=f"{risk_cfg['risk_id']}_{provider}_{model}",
            meta={
                "risk_id": risk_cfg["risk_id"],
                "provider": provider,
                "model": model,
                "k": K,
            },
        )

        for row in rows:
            print(f"Executing {risk_cfg['risk_id']} for model {model} and seed {row.seed_id}...")

            variants = variant_cache[row.seed_id]

            for variant in variants:
                logger.write("variant_start", {
                    "risk_id": risk_cfg["risk_id"],
                    "seed_id": variant.get("seed_id"),
                    "variant_id": variant.get("variant_id"),
                    "meta": variant.get("meta", {}),
                    "messages": variant.get("messages", []),
                })

                try:
                    payload, result = execute_one(variant, provider, model, params)

                    logger.write("variant_result", {
                        "risk_id": risk_cfg["risk_id"],
                        "seed_id": variant.get("seed_id"),
                        "variant_id": variant.get("variant_id"),
                        "provider": result.get("provider"),
                        "model": result.get("model"),
                        "request": payload,
                        "text": result.get("text"),
                        "raw_preview": lg.safe_preview(result.get("raw")),
                        "status": "ok",
                    })

                    output_csv.add_to_run(risk_cfg["to_output_row"](result, variant))
                    print(f"variant {variant['variant_id']} finished")

                except Exception as e:
                    logger.write("variant_error", {
                        "risk_id": risk_cfg["risk_id"],
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
