"""
MentalHealthClassifier — trained model component.

A small feed-forward network trained on top of frozen MiniLM sentence
embeddings (384-dim) to predict a mental-health category for a user message.

This is intentionally small: two linear layers, ~28K trainable parameters.
It is not meant to replace the embedding model (still frozen, still MiniLM) —
it replaces pure cosine-similarity lookup with an actual trained decision.
"""

import torch
import torch.nn as nn

# Fixed category order — must stay consistent between training and inference.
# Saved alongside the weights in label_map.json so this never has to be
# guessed at load time.
CATEGORIES = [
    "anxiety",
    "depression",
    "stress",
    "sleep",
    "loneliness",
    "self_esteem",
    "grief",
    "anger",
    "relationships",
    "crisis",
]

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output size
HIDDEN_DIM = 64
NUM_CLASSES = len(CATEGORIES)
DROPOUT_P = 0.5


class MentalHealthClassifier(nn.Module):
    """
    384 (MiniLM embedding)
      -> Linear(384, 64) -> ReLU -> Dropout(0.5)
      -> Linear(64, 10)  -> (softmax applied outside, via CrossEntropyLoss during
                             training and torch.softmax at inference)
    """

    def __init__(self, input_dim: int = EMBEDDING_DIM,
                 hidden_dim: int = HIDDEN_DIM,
                 num_classes: int = NUM_CLASSES,
                 dropout_p: float = DROPOUT_P):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_p)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns raw logits (unnormalized scores), shape (batch, num_classes)."""
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

    def predict_with_confidence(self, x: torch.Tensor, mc_passes: int = 1):
        """
        Inference helper.

        mc_passes=1  -> standard single forward pass (dropout OFF), returns
                        (predicted_category_index, confidence_float)
        mc_passes>1  -> MC Dropout: run `mc_passes` forward passes WITH dropout
                        active, average the softmax outputs, and return the
                        mean confidence plus its variance (a measure of the
                        model's uncertainty — used in Phase 4/5).
        """
        if mc_passes <= 1:
            self.eval()
            with torch.no_grad():
                logits = self.forward(x)
                probs = torch.softmax(logits, dim=-1)
            conf, pred = torch.max(probs, dim=-1)
            return pred.item(), conf.item(), 0.0

        # MC Dropout: keep dropout ACTIVE during inference on purpose
        self.train()
        all_probs = []
        with torch.no_grad():
            for _ in range(mc_passes):
                logits = self.forward(x)
                probs = torch.softmax(logits, dim=-1)
                all_probs.append(probs)
        stacked = torch.stack(all_probs, dim=0)  # (mc_passes, batch, num_classes)
        mean_probs = stacked.mean(dim=0)
        var_probs = stacked.var(dim=0)
        conf, pred = torch.max(mean_probs, dim=-1)
        uncertainty = var_probs.gather(-1, pred.unsqueeze(-1)).squeeze(-1)
        self.eval()
        return pred.item(), conf.item(), uncertainty.item()
