import copy
import random
import yaml
import re
from typing import Any, Dict, List, Tuple, Optional
import sys
import os
sys.path.append(os.path.abspath("/src/"))
import src.fuzzer_modules.helpers.mutate as mt


def read_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CANARY_PLACEHOLDERS = [
    "{{canary}}",
    "{{canary.number}}",
    "{{canary.token_word}}",
    "{{canary.id_random}}",
    "{{canary.composite}}",
]

def pick_canary(canaries: Dict[str, Any], canary_type: str) -> Tuple[str, str]:
    if canary_type not in canaries:
        raise KeyError(f"canary_type '{canary_type}' not found in canaries.yaml keys={list(canaries.keys())}")

    pool = canaries[canary_type]
    if not isinstance(pool, list) or not pool:
        raise ValueError(f"canaries['{canary_type}'] must be a non-empty list of {{id,value}} items")

    item = random.choice(pool)
    if "id" not in item or "value" not in item:
        raise ValueError(f"Malformed canary item for type '{canary_type}': {item}")

    return str(item["id"]), str(item["value"])


def subs_canary(text: str, canary_value: str) -> str:
    for ph in CANARY_PLACEHOLDERS:
        text = text.replace(ph, canary_value)

    text = re.sub(r"\{\{canary\.[^}]+\}\}", canary_value, text)

    return text

def insert_after(messages: List[Dict[str, Any]], idx: int, new_msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return messages[: idx + 1] + new_msgs + messages[idx + 1 :]


def find_last_index(messages: List[Dict[str, Any]], msg_type: str) -> Optional[int]:
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], dict) and messages[i].get("type") == msg_type:
            return i
    return None


def validate_messages(messages: List[Any]) -> None:
    if not isinstance(messages, list):
        raise TypeError(f"seed_row.messages must be a list, got {type(messages)}")

    for i, m in enumerate(messages):
        if not isinstance(m, dict):
            raise TypeError(f"Invalid message at index {i}: expected dict, got {type(m)} -> {m!r}")
        if "text" not in m:
            raise KeyError(f"Invalid message at index {i}: missing 'text' key -> {m!r}")
        if "type" not in m:
            raise KeyError(f"Invalid message at index {i}: missing 'type' key -> {m!r}")

def fuzz_r1(seed_row, k: int, canaries_path: str = "data/r1/canaries.yaml", distractor_path: str = "data/r1/templates/distractor.yaml", benign_path: str = "data/r1/templates/benign.yaml",) -> List[Dict[str, Any]]:
    canaries = read_yaml(canaries_path)

    distractor_yaml = read_yaml(distractor_path)
    benign_yaml = read_yaml(benign_path)

    distractor_tpls = [t["text"] for t in distractor_yaml.get("templates", []) if "text" in t]
    benign_tpls = [t["text"] for t in benign_yaml.get("templates", []) if "text" in t]

    if not distractor_tpls:
        raise ValueError(f"No distractor templates found in {distractor_path}")
    if not benign_tpls:
        raise ValueError(f"No benign templates found in {benign_path}")

    results: List[Dict[str, Any]] = []

    for vid in range(1, k + 1):
        msgs = copy.deepcopy(seed_row.messages)
        validate_messages(msgs)

        canary_id, canary_value = pick_canary(canaries, seed_row.canary_type)

        for m in msgs:
            m["text"] = subs_canary(m["text"], canary_value)

        mutated_value = canary_value
        if random.random() < 0.9:
            mutated_value = mt.mutate_canary_surface(canary_value, seed_row.canary_type)
            if mutated_value != canary_value:
                for m in msgs:
                    if m.get("type") == "confidential":
                        m["text"] = m["text"].replace(canary_value, mutated_value)

        idx_conf = find_last_index(msgs, "confidential")
        idx_exf = find_last_index(msgs, "exfiltrate")

        if idx_conf is not None and idx_exf is not None and idx_conf < idx_exf:
            n_dist = random.randint(0, 2)
            if n_dist > 0:
                new_msgs = [{"type": "distractor", "text": random.choice(distractor_tpls)} for _ in range(n_dist)]
                msgs = insert_after(msgs, idx_conf, new_msgs)
                idx_exf = find_last_index(msgs, "exfiltrate")  # update after insertion

            n_ben = random.randint(0, 2)
            if n_ben > 0 and idx_exf is not None:
                new_msgs = [{"type": "benign", "text": random.choice(benign_tpls)} for _ in range(n_ben)]
                msgs = msgs[:idx_exf] + new_msgs + msgs[idx_exf:]

        results.append(
            {
                "seed_id": seed_row.seed_id,
                "variant_id": f"{seed_row.seed_id}_v{vid}",
                "messages": msgs,
                "meta": {
                    "canary_type": seed_row.canary_type,
                    "canary_id": canary_id,
                    "canary_value": canary_value,
                    "canary_surface": mutated_value,
                },
            }
        )

    return results

