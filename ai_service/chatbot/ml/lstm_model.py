try:
    import torch
    from torch import nn
except ImportError:
    torch = None
    nn = None


class CartLSTMRecommender(nn.Module if nn else object):
    def __init__(self, product_count, event_count, embedding_dim=64, hidden_dim=96, dropout=0.2):
        if nn is None:
            raise ImportError("PyTorch is required for CartLSTMRecommender.")
        super().__init__()
        self.product_embedding = nn.Embedding(product_count, embedding_dim, padding_idx=0)
        self.event_embedding = nn.Embedding(event_count, 12, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embedding_dim + 12,
            hidden_size=hidden_dim,
            batch_first=True,
            dropout=0,
        )
        self.dropout = nn.Dropout(dropout)
        self.output = nn.Linear(hidden_dim, product_count)

    def forward(self, product_sequence, event_sequence):
        product_features = self.product_embedding(product_sequence)
        event_features = self.event_embedding(event_sequence)
        features = torch.cat([product_features, event_features], dim=-1)
        output, _ = self.lstm(features)
        last_hidden = output[:, -1, :]
        return self.output(self.dropout(last_hidden))
