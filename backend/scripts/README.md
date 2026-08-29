# Developer Scripts

These scripts are used for model training and corpus management. They are not part of the production runtime.

---

## `train_classifier.py`

Trains the `MentalHealthClassifier` on top of frozen `all-MiniLM-L6-v2` embeddings.

**When to run**: After modifying the corpus or when improving classification accuracy.

```bash
cd backend
python scripts/train_classifier.py
```

**Output:**
- `app/models/classifier_weights.pt` — PyTorch state dict (committed to the repository)
- `app/models/label_map.json` — Category index ↔ name mapping

**After running:** Restart the FastAPI server to load the new weights. Verify with `GET /health` that `classifier_loaded: true`.

---

## Notes

- The embedding model (`all-MiniLM-L6-v2`) is **not fine-tuned** — only the 2-layer head is trained.
- Embeddings are computed once and cached in memory across all epochs, so training is fast (~seconds on CPU).
- The trained weights file is small (~103 KB) and is versioned in the repository deliberately — contributors should not need to retrain the model just to run the app.
