"""Experiment-only OpenAI API adapter; original AutoCedar source stays pinned.

The author package sends unsupported reasoning with gpt-4.1-mini, and its
PropertyAtomsResponse contains a free-form dict rejected by strict parse.
This adapter requests plain JSON text and validates it locally with the
original Pydantic output type. Results are *not* a native author run.
"""

import json
from pathlib import Path

import autocedar.providers.openai_api as api


HERE = Path(__file__).resolve().parent
SPEND_LIMIT_USD = 0.50
spend_usd = 0.0
original_kwargs = api._responses_kwargs
original_text = api.OpenAIAPIBackend.generate_text


def request_kwargs(**kwargs):
    result = original_kwargs(**kwargs)
    result.pop("reasoning", None)
    return result


def charge(response, operation):
    global spend_usd
    usage = api._openai_usage(getattr(response, "usage", None))
    cost = (usage.input_tokens * 0.40 + usage.output_tokens * 1.60) / 1_000_000
    spend_usd += cost
    with (HERE / "adapter_usage.jsonl").open("a") as handle:
        handle.write(json.dumps({
            "operation": operation, "request_id": api._string_field(response, "id"),
            "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens,
            "estimated_usd": round(cost, 8), "cumulative_estimated_usd": round(spend_usd, 8),
        }) + "\n")
    return usage


def budget_guard():
    if spend_usd >= SPEND_LIMIT_USD:
        raise RuntimeError("C1c API estimated cost cap reached")


def generate_text(self, **kwargs):
    budget_guard()
    result = original_text(self, **kwargs)
    # Original method returns usage but not the raw response.
    global spend_usd
    cost = (result.usage.input_tokens * 0.40 + result.usage.output_tokens * 1.60) / 1_000_000
    spend_usd += cost
    with (HERE / "adapter_usage.jsonl").open("a") as handle:
        handle.write(json.dumps({
            "operation": "text", "request_id": result.request_id,
            "input_tokens": result.usage.input_tokens, "output_tokens": result.usage.output_tokens,
            "estimated_usd": round(cost, 8), "cumulative_estimated_usd": round(spend_usd, 8),
        }) + "\n")
    return result


def generate_structured(self, *, model, messages, output_type, system=None,
                        max_tokens=8192, temperature=None, reasoning_effort=None):
    budget_guard()
    kwargs = request_kwargs(model=model, messages=messages, system=system,
                            max_tokens=max_tokens, temperature=temperature,
                            reasoning_effort=reasoning_effort)
    schema = json.dumps(output_type.model_json_schema(), separators=(",", ":"))
    kwargs["instructions"] = (kwargs.get("instructions", "") +
        "\nReturn exactly one JSON object satisfying this schema. No markdown: " + schema)
    response = self._client.responses.create(**kwargs)
    usage = charge(response, output_type.__name__)
    raw = api._response_text(response)
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    value = output_type.model_validate_json(raw)
    return api.StructuredResult(
        parsed=value, usage=usage,
        model=api._string_field(response, "model") or model,
        request_id=api._string_field(response, "id"),
    )


api._responses_kwargs = request_kwargs
api.OpenAIAPIBackend.generate_text = generate_text
api.OpenAIAPIBackend.generate_structured = generate_structured
