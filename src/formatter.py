from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

OpenAIRole = Literal["system", "user", "assistant"]

TYPE_TO_OPENAI_ROLE: Dict[str, OpenAIRole] = {
    "authority": "system",
    "confidential": "user",
    "benign": "user",
    "distractor": "user",
    "task": "user",
    "social_eng": "user",
    "exfiltrate": "user",
}

@dataclass
class ChatTurn:
    role: OpenAIRole
    content: str
    msg_type: str

def normalize_to_turns( messages: List[Dict[str, Any]], system_prompt: Optional[str] = None,) -> List[ChatTurn]:
    turns: List[ChatTurn] = []
    if system_prompt:
        turns.append(ChatTurn(role="system", content=system_prompt, msg_type="system_prompt"))

    for m in messages:
        if not isinstance(m, dict) or "text" not in m or "type" not in m:
            raise TypeError(f"Expected dict with 'type' and 'text', got: {m}")

        msg_type = str(m["type"])
        role = TYPE_TO_OPENAI_ROLE.get(msg_type, "user")
        turns.append(ChatTurn(role=role, content=str(m["text"]), msg_type=msg_type))

    return turns

def format_openai(model: str, turns: List[ChatTurn], **params) -> Dict[str, Any]:
    payload = {
        "model": model,
        "input": [
            {"role": t.role, "content": [{"type": "input_text", "text": t.content}]}
            for t in turns
        ],
    }
    payload.update(params)
    return payload

def format_deepseek(model: str, turns: List[ChatTurn], **params) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": t.role, "content": t.content} for t in turns],
    }
    payload.update(params)
    return payload


def format_gemini(model: str, turns: List[ChatTurn], **params) -> Dict[str, Any]:
    system_parts = [t.content for t in turns if t.role == "system"]
    system_instruction = "\n".join(system_parts).strip() if system_parts else None

    contents = []
    for t in turns:
        if t.role == "system":
            continue

        contents.append({
            "role": "user",
            "parts": [{"text": t.content}],
        })

    config = dict(params) if params else {}
    if system_instruction:
        config["system_instruction"] = system_instruction

    payload: Dict[str, Any] = {
        "model": model,
        "contents": contents,
    }
    if config:
        payload["config"] = config

    return payload
