"""Strict JSON codec for original CONTINUITY dataclasses (R2 adapter code).

CONTINUITY objects are frozen dataclasses (frozensets, tuples, mappings). An A2A
message can only carry JSON, so evidence travelling between agents/queues must be
encoded and decoded. This module is ADAPTER code, not part of the original
method. It must be loss-free for what the verifier signs: tests assert
digest(decode(encode(x))) == digest(x) and equality of the objects.

Decoding is strict and fail-closed: unknown keys, missing fields and wrong
scalar types raise ProofCodecError. Callers must treat that as "no valid proof"
(deny), never as a recoverable repair. The codec never creates, repairs or
re-signs evidence.
"""
from __future__ import annotations

import dataclasses
import json
import types
import typing
from collections.abc import Mapping
from enum import Enum
from typing import Any, FrozenSet, get_args, get_origin


class ProofCodecError(ValueError):
    """Raised for any malformed or non-conforming wire object."""


def encode(value: Any) -> Any:
    """Dataclass graph -> JSON-compatible structure (deterministic ordering for sets)."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: encode(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted((encode(v) for v in value), key=lambda x: json.dumps(x, sort_keys=True))
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    if value is None or isinstance(value, (str, bool, int)):
        return value
    raise ProofCodecError(f'unsupported value type for wire encoding: {type(value).__name__}')


def _strict_scalar(tp: type, data: Any, where: str) -> Any:
    if tp is bool:
        ok = isinstance(data, bool)
    elif tp is int:
        ok = isinstance(data, int) and not isinstance(data, bool)
    elif tp is str:
        ok = isinstance(data, str)
    else:  # pragma: no cover - guarded by caller
        ok = False
    if not ok:
        raise ProofCodecError(f'{where}: expected {tp.__name__}, got {type(data).__name__}')
    return data


def decode(tp: Any, data: Any, where: str = '$') -> Any:
    """JSON-compatible structure -> instance of `tp` (strict)."""
    if tp is Any:
        return data
    origin = get_origin(tp)
    if origin in (typing.Union, types.UnionType):
        options = get_args(tp)
        if data is None and type(None) in options:
            return None
        rest = [a for a in options if a is not type(None)]
        if len(rest) != 1:
            raise ProofCodecError(f'{where}: unsupported union {tp}')
        return decode(rest[0], data, where)
    if origin in (frozenset, FrozenSet):
        (inner,) = get_args(tp)
        if not isinstance(data, list):
            raise ProofCodecError(f'{where}: expected list for frozenset')
        return frozenset(decode(inner, x, f'{where}[]') for x in data)
    if origin is tuple:
        args = get_args(tp)
        if len(args) != 2 or args[1] is not Ellipsis:
            raise ProofCodecError(f'{where}: only homogeneous tuples are supported')
        if not isinstance(data, list):
            raise ProofCodecError(f'{where}: expected list for tuple')
        return tuple(decode(args[0], x, f'{where}[{i}]') for i, x in enumerate(data))
    if origin in (Mapping, dict, typing.Mapping):
        key_tp, val_tp = get_args(tp)
        if not isinstance(data, dict):
            raise ProofCodecError(f'{where}: expected object')
        return {_strict_scalar(key_tp, k, where): decode(val_tp, v, f'{where}.{k}')
                for k, v in data.items()}
    if dataclasses.is_dataclass(tp) and isinstance(tp, type):
        if not isinstance(data, dict):
            raise ProofCodecError(f'{where}: expected object for {tp.__name__}')
        hints = typing.get_type_hints(tp)
        fields = {f.name: f for f in dataclasses.fields(tp)}
        unknown = set(data) - set(fields)
        if unknown:
            raise ProofCodecError(f'{where}: unknown keys {sorted(unknown)} for {tp.__name__}')
        kwargs = {}
        for name, field in fields.items():
            if name in data:
                kwargs[name] = decode(hints[name], data[name], f'{where}.{name}')
            elif field.default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING:
                raise ProofCodecError(f'{where}: missing field {name} for {tp.__name__}')
        return tp(**kwargs)
    if tp in (str, int, bool):
        return _strict_scalar(tp, data, where)
    if tp is type(None):
        if data is not None:
            raise ProofCodecError(f'{where}: expected null')
        return None
    raise ProofCodecError(f'{where}: unsupported target type {tp!r}')


def to_wire(value: Any) -> str:
    """Serialise to a JSON string (what an A2A DataPart would carry)."""
    return json.dumps(encode(value), sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def from_wire(tp: Any, text: Any) -> Any:
    """Parse a JSON string; any failure is a ProofCodecError (fail-closed)."""
    if not isinstance(text, str):
        raise ProofCodecError('wire value must be a JSON string')
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ProofCodecError(f'invalid JSON: {error}') from error
    return decode(tp, data)
