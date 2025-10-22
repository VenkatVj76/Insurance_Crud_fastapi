from typing import Any, Dict, Iterable, List, Optional


def serialize_doc(document: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return a shallow-copied document with MongoDB ObjectId converted to str.

    This ensures FastAPI/Pydantic response models expecting `_id` as a string
    validate correctly.
    """
    if document is None:
        return None
    serialized = dict(document)
    _id = serialized.get("_id")
    if _id is not None and not isinstance(_id, str):
        serialized["_id"] = str(_id)
    return serialized


def serialize_docs(documents: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serialize an iterable of documents, converting ObjectIds to strings."""
    return [serialize_doc(doc) for doc in documents]


