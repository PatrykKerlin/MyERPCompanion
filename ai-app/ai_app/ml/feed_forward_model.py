from __future__ import annotations

from typing import Literal, Sequence

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
