# observability/langfuse_client.py

import os
from contextlib import nullcontext
from dotenv import load_dotenv

load_dotenv()

_LANGFUSE_ENABLED = False
_langfuse = None
_observe = None
_propagate_attributes = None


def init_langfuse():
    global _LANGFUSE_ENABLED
    global _langfuse
    global _observe
    global _propagate_attributes

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST")

    if not all([public_key, secret_key, host]):
        return False

    try:
        from langfuse import (
            Langfuse,
            observe as langfuse_observe,
            propagate_attributes as langfuse_propagate_attributes,
        )

        _langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )

        _observe = langfuse_observe
        _propagate_attributes = langfuse_propagate_attributes

        _LANGFUSE_ENABLED = True

        print("[Langfuse] enabled")

        return True

    except Exception as e:
        print(f"[Langfuse] disabled: {e}")
        return False


def enabled():
    return _LANGFUSE_ENABLED


def flush():
    if _langfuse:
        try:
            _langfuse.flush()
        except Exception:
            pass


def span(*args, **kwargs):
    if not _LANGFUSE_ENABLED:
        return nullcontext()

    return _langfuse.start_as_current_span(*args, **kwargs)


def generation(*args, **kwargs):
    if not _LANGFUSE_ENABLED:
        return nullcontext()

    return _langfuse.start_as_current_generation(*args, **kwargs)


def observe(*args, **kwargs):
    if not _LANGFUSE_ENABLED or _observe is None:

        def decorator(func):
            return func

        return decorator

    return _observe(*args, **kwargs)


def propagate_attributes(**kwargs):
    if not _LANGFUSE_ENABLED or _propagate_attributes is None:
        return nullcontext()

    return _propagate_attributes(**kwargs)