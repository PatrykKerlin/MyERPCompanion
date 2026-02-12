from __future__ import annotations

from torch import Tensor, nn


class FeedForwardModel(nn.Module):
    _dropout_rate = 0.10
    _hidden_dims = (256, 128, 64, 32, 16, 8)

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev_dim = input_dim
        for hidden_dim in FeedForwardModel._hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(FeedForwardModel._dropout_rate))
            prev_dim = hidden_dim
        layers.append(nn.Linear(prev_dim, output_dim))

        self._model = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        return self._model(x)
