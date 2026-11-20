"""The model connector now lives in the shared harness (shared/harness/model.py)."""
from harness.model import KEY_FILE_VARIABLE, Claude, ModelError, Scripted, _post

__all__ = ["KEY_FILE_VARIABLE", "Claude", "ModelError", "Scripted"]
