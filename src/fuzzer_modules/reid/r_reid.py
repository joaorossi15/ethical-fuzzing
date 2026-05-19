from __future__ import annotations

import copy
import os
import sys
from typing import Any, Dict, List

sys.path.append(os.path.abspath("/src/"))

from src.fuzzer_modules.reid.metamorphic import apply_metamorphic_transformation


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


def fuzz_reid(seed_row, k: int) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for vid in range(1, k + 1):
        msgs = copy.deepcopy(seed_row.messages)
        validate_messages(msgs)

        mutated_msgs, transform_meta = apply_metamorphic_transformation(
            messages=msgs,
            deidentified_candidates=seed_row.deidentified_candidates,
            quasi_identifiers=seed_row.quasi_identifiers,
        )

        results.append(
            {
                "seed_id": seed_row.seed_id,
                "variant_id": f"{seed_row.seed_id}_v{vid}",
                "messages": mutated_msgs,
                "meta": {
                    "risk_id": "reid",
                    "case_id": seed_row.case_id,
                    "target_identity": seed_row.target_identity,
                    "boundary_strength": seed_row.boundary_strength,
                    "deidentification_level": seed_row.deidentification_level,
                    "overlap_level": seed_row.overlap_level,
                    "prior_context": seed_row.prior_context,
                    "deidentified_candidates": seed_row.deidentified_candidates,
                    "protected_candidates": seed_row.protected_candidates,
                    **transform_meta,
                },
            }
        )

    return results
