"""
RAG (Retrieval-Augmented Generation) module for GoldenPath governance documents.

This module implements Phase 0 of the Agentic Graph RAG pipeline (PRD-0008):
- Document loading with frontmatter extraction
- Markdown header chunking (ADR-0184)
- ChromaDB vector indexing
- Query and retrieval interface

References:
- PRD-0008: Agentic Graph RAG Pipeline
- ADR-0184: RAG Markdown Header Chunking Strategy
- ADR-0185: Graphiti Agent Memory Framework (Phase 1)
- GOV-0017: TDD and Determinism Policy
"""

__version__ = "0.1.0"
