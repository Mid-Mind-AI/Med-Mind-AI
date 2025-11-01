from typing import Dict, List


class ConversationStore:
    """In-memory conversation store keyed by session_id.

    This is intentionally simple and ephemeral. For production, replace with a
    persistent/session-aware store (Redis, DB, etc.).
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[dict]] = {}

    def get(self, session_id: str) -> List[dict]:
        return self._store.get(session_id, [])

    def set(self, session_id: str, messages: List[dict]) -> None:
        self._store[session_id] = messages

    def append(self, session_id: str, message: dict) -> List[dict]:
        existing = self._store.get(session_id, [])
        existing.append(message)
        self._store[session_id] = existing
        return existing


conversation_store = ConversationStore()


