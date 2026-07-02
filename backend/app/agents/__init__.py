"""Multi-agent AI engine (design doc Section 8.1 / 8.2.1).

Specialized agents handle each step of the ticket lifecycle:
  OCR Agent, Vision Agent, Intent Agent, Priority Agent, Duplicate Agent,
  Embedding Agent, RAG/Resolution Agent, Routing Agent, Audit Agent.
The Orchestrator runs them in the exact 12-step order of Section 9.1.
"""
