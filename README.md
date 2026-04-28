```
                ┌──────────────────────┐
                │   User Upload (PDF)  │
                └─────────┬────────────┘
                          ↓
                ┌──────────────────────┐
                │  Ingestion Pipeline  │
                │ (chunk + embed)      │
                └─────────┬────────────┘
                          ↓
                ┌──────────────────────┐
                │ Hybrid Index         │
                │ FAISS + BM25         │
                └─────────┬────────────┘


User Query ───────────────→ Planner Node
                             ↓
        ┌────────────────────┼────────────────────┐
        ↓                                         ↓
Direct Answer Path                    Retrieval Path
(no docs needed)                      (docs needed)
        ↓                                         ↓
        └──────────────→ Generator Node ←─────────┘
                                ↓
                         Critic Node
                                ↓
                    (loop if needed)
                                ↓
                             FINAL

```