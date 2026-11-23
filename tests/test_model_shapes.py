"""Testes de forma, campo recetivo, sigmoid, lote e contagem de parâmetros da CNN.

Todos os dados são sintéticos (tensores gerados em memória). Nada é lido de data/.
"""

import pytest
import torch
from torch import nn

from ais.phase1.model import FullTripCNN, build_cnn, count_parameters, receptive_field

C = 7


@pytest.fixture(autouse=True)
def _restore_determinism():
    previous = torch.are_deterministic_algorithms_enabled()
    yield
    torch.use_deterministic_algorithms(previous)


@pytest.mark.parametrize("n", [1, 2, 13, 50, 500])
@pytest.mark.parametrize("b", [1, 3])
def test_output_shape_is_b_1_n(n, b):
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).eval()
    x = torch.randn(b, C, n)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (b, 1, n)
    assert out.dtype == torch.float32


def test_same_instance_accepts_different_lengths():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).eval()
    with torch.no_grad():
        for n in (40, 1, 7, 113):
            assert model(torch.randn(1, C, n)).shape == (1, 1, n)


def test_receptive_field_default_is_13():
    assert receptive_field() == 13
    assert receptive_field({"hidden_channels": [4, 4], "kernel_sizes": [3, 3]}) == 5


def test_default_model_has_receptive_field_13():
    model = build_cnn(n_channels=C)
    assert isinstance(model, FullTripCNN)
    assert receptive_field(model.model_config) == 13


@pytest.mark.parametrize("j", [0, 20, 39])
def test_perturbing_input_changes_only_receptive_field(j):
    """Empírico: alterar a entrada no ponto j só altera a saída em |i - j| <= 6."""
    N = 40
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).eval()
    torch.manual_seed(1)
    x = torch.randn(1, C, N)
    x_perturbed = x.clone()
    x_perturbed[0, :, j] += 1.0

    with torch.no_grad():
        y1 = model(x)
        y2 = model(x_perturbed)

    changed = ((y1 - y2).abs().reshape(-1) > 1e-6).nonzero().flatten().tolist()
    allowed = {i for i in range(N) if abs(i - j) <= 6}

    assert j in changed, "a própria posição j deve influenciar a sua saída"
    assert set(changed) <= allowed, f"pontos fora do campo recetivo alterados: {sorted(set(changed) - allowed)}"


def test_model_has_no_sigmoid_and_outputs_logits_outside_unit_interval():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).eval()
    assert not any(isinstance(m, nn.Sigmoid) for m in model.modules())

    # Valores negativos só podem vir de logits: uma Sigmoid nunca os produziria.
    x = torch.randn(4, C, 60) * 10.0
    with torch.no_grad():
        out = model(x)
    assert bool((out < 0).any())

    # Sem recorte em 1: deslocando o bias final, as saídas ficam acima de 1.
    with torch.no_grad():
        model.net[-1].bias.fill_(5.0)
        shifted = model(x)
    assert bool((shifted > 1).all())


def test_no_mixing_between_batch_samples():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).eval()
    x = torch.randn(2, C, 30)
    x_alt = x.clone()
    x_alt[0] = torch.randn(C, 30)

    with torch.no_grad():
        out1 = model(x)
        out2 = model(x_alt)

    assert torch.allclose(out1[1], out2[1], atol=1e-6, rtol=0.0)
    assert not torch.allclose(out1[0], out2[0])


def test_parameter_count_matches_hand_calculation():
    # Conv1d(C->32,k5): 7*32*5 pesos + 32 bias = 1152
    # Conv1d(32->64,k5): 32*64*5 + 64 = 10304
    # Conv1d(64->32,k5): 64*32*5 + 32 = 10272
    # Conv1d(32->1,k1): 32*1*1 + 1 = 33
    expected = (7 * 32 * 5 + 32) + (32 * 64 * 5 + 64) + (64 * 32 * 5 + 32) + (32 * 1 * 1 + 1)
    assert expected == 21761
    assert count_parameters(build_cnn(n_channels=7)) == expected


def test_wrong_channel_count_is_rejected():
    model = build_cnn(n_channels=7)
    with pytest.raises(ValueError):
        model(torch.randn(1, 3, 10))


def test_even_kernel_is_rejected():
    with pytest.raises(ValueError):
        build_cnn({"kernel_sizes": (4, 5, 5)})
