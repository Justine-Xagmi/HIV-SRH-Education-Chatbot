
from app.knowledge.registry import KnowledgeRegistry

# Shared in-memory registry for the development application.
# This data is not persistent and will be lost when the app restarts.
knowledge_registry = KnowledgeRegistry()
