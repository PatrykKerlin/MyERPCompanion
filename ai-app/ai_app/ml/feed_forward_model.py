from __future__ import annotations

from typing import Literal, Sequence

import torch
from torch import nn

ActivationName = Literal["relu", "gelu", "tanh", "leaky_relu"]
OutputActivationName = Literal["none", "sigmoid", "softmax"]


class FeedForwardModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dims: Sequence[int],
        output_dim: int,
        activation: ActivationName = "relu",
        dropout: float = 0.0,
        output_activation: OutputActivationName = "none",
    ) -> None:
        super().__init__()
        activation_layer = {
            "relu": nn.ReLU,
            "gelu": nn.GELU,
            "tanh": nn.Tanh,
            "leaky_relu": nn.LeakyReLU,
        }.get(activation, nn.ReLU)
        layers: list[nn.Module] = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(activation_layer())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        layers.append(nn.Linear(prev_dim, output_dim))
        if output_activation == "sigmoid":
            layers.append(nn.Sigmoid())
        elif output_activation == "softmax":
            layers.append(nn.Softmax(dim=1))

        self._model = nn.Sequential(*layers)

    def forward(self, x):  # noqa: ANN001,ANN201
        return self._model(x)

    @classmethod
    def for_prediction(
        cls,
        input_dim: int,
        hidden_dims: Sequence[int] = (128, 64, 32),
        activation: ActivationName = "gelu",
        dropout: float = 0.10,
    ) -> "FeedForwardModel":
        return cls(
            input_dim=input_dim,
            hidden_dims=hidden_dims,
            output_dim=1,
            activation=activation,
            dropout=dropout,
            output_activation="none",
        )


class EmbeddedFeedForwardModel(nn.Module):
    def __init__(
        self,
        item_vocab_size: int,
        customer_vocab_size: int,
        category_vocab_size: int,
        currency_vocab_size: int,
        numerical_dim: int,
        hidden_dims: Sequence[int],
        output_dim: int,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        item_dim = EmbeddedFeedForwardModel._embedding_dim(item_vocab_size)
        customer_dim = EmbeddedFeedForwardModel._embedding_dim(customer_vocab_size)
        category_dim = EmbeddedFeedForwardModel._embedding_dim(category_vocab_size)
        currency_dim = EmbeddedFeedForwardModel._embedding_dim(currency_vocab_size)

        self._item_embedding = nn.Embedding(item_vocab_size + 1, item_dim)
        self._customer_embedding = nn.Embedding(customer_vocab_size + 1, customer_dim)
        self._category_embedding = nn.Embedding(category_vocab_size + 1, category_dim)
        self._currency_embedding = nn.Embedding(currency_vocab_size + 1, currency_dim)

        input_dim = item_dim + customer_dim + category_dim + currency_dim + numerical_dim
        layers: list[nn.Module] = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.GELU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        layers.append(nn.Linear(prev_dim, output_dim))
        self._head = nn.Sequential(*layers)

    def forward(self, categorical_x: torch.Tensor, numerical_x: torch.Tensor) -> torch.Tensor:
        item_emb = self._item_embedding(categorical_x[:, 0])
        customer_emb = self._customer_embedding(categorical_x[:, 1])
        category_emb = self._category_embedding(categorical_x[:, 2])
        currency_emb = self._currency_embedding(categorical_x[:, 3])
        features = torch.cat(
            [item_emb, customer_emb, category_emb, currency_emb, numerical_x],
            dim=1,
        )
        return self._head(features)

    @staticmethod
    def _embedding_dim(vocab_size: int) -> int:
        return min(32, max(4, int((max(vocab_size, 1) ** 0.25) * 4)))
