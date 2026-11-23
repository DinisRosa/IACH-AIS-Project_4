"""Testes de perda, gradientes, otimizador, smoke test, treino e avaliação de diagnóstico.

Todos os dados são sintéticos (gerados em memória). Nada é lido de data/.
O teste de sobreajuste é DIAGNÓSTICO de capacidade de ajuste numa única sequência
sintética. NÃO é prova de generalização.
"""

import math

import pytest
import torch
from torch import nn

from phase1.checks import run_training_smoke_test
from phase1.model import build_cnn
from phase1.training import (
    build_loss,
    build_optimizer,
    evaluate_training_subset,
    train_one_epoch,
)
from phase1.utils import select_device, set_reproducibility

C = 7
CPU = torch.device("cpu")


@pytest.fixture(autouse=True)
def _restore_determinism():
    previous = torch.are_deterministic_algorithms_enabled()
    yield
    torch.use_deterministic_algorithms(previous)


def _synthetic_sequence(n, seed=0):
    gen = torch.Generator().manual_seed(seed)
    X = torch.randn(1, C, n, generator=gen)
    y = (torch.rand(1, 1, n, generator=gen) > 0.5).float()
    return X, y


def _bce_point(z, y):
    """BCE com logits, ponto a ponto, em forma estável: max(z,0) - z*y + log(1+exp(-|z|))."""
    return max(z, 0.0) - z * y + math.log1p(math.exp(-abs(z)))


# --------------------------------------------------------------------------- perda e gradientes


def test_loss_is_finite():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).train()
    X, y = _synthetic_sequence(40)
    loss = build_loss()(model(X), y)
    assert torch.isfinite(loss)


def test_gradients_exist_and_are_finite_and_nonzero():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).train()
    X, y = _synthetic_sequence(40)
    loss = build_loss()(model(X), y)
    loss.backward()
    for name, p in model.named_parameters():
        assert p.grad is not None, name
        assert torch.isfinite(p.grad).all(), name
        assert float(p.grad.abs().max()) > 0.0, name


def test_one_optimizer_step_changes_weights():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C).train()
    X, y = _synthetic_sequence(40)
    optimizer = build_optimizer(model)
    before = [p.detach().clone() for p in model.parameters()]

    optimizer.zero_grad()
    build_loss()(model(X), y).backward()
    optimizer.step()

    for b, p in zip(before, model.parameters()):
        assert not torch.equal(b, p.detach())


def test_bce_with_logits_matches_hand_value_and_expects_logits():
    z = torch.tensor([[[0.0, 2.0, -1.0]]])
    y = torch.tensor([[[0.0, 1.0, 0.0]]])
    # Valores à mão, ponto a ponto:
    #   z=0,  y=0 -> log(1+e^0)   = log 2
    #   z=2,  y=1 -> log(1+e^-2)
    #   z=-1, y=0 -> log(1+e^-1)
    expected = (math.log(1 + math.exp(0.0)) + math.log(1 + math.exp(-2.0)) + math.log(1 + math.exp(-1.0))) / 3

    loss_fn = build_loss()
    assert isinstance(loss_fn, nn.BCEWithLogitsLoss)
    assert loss_fn.reduction == "mean"
    got = float(loss_fn(z, y))
    assert got == pytest.approx(expected, rel=1e-6)

    # Se se aplicasse sigmoid antes da BCEWithLogits, o valor seria diferente.
    with_sigmoid_applied = float(loss_fn(torch.sigmoid(z), y))
    assert abs(with_sigmoid_applied - got) > 1e-2


def test_smoke_test_returns_report_and_does_not_change_original():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C)
    X, y = _synthetic_sequence(40)
    snapshot = {k: v.clone() for k, v in model.state_dict().items()}

    report = run_training_smoke_test(model, (X, y), build_loss(), CPU)

    assert report["all_checks_passed"] is True
    assert report["forward_shape_ok"] is True
    assert report["output_shape"] == [1, 1, 40]
    assert report["loss_finite"] is True
    assert report["grads_all_present_and_finite"] is True
    assert report["grads_all_nonzero"] is True
    assert report["optimizer_step_changed_all_tensors"] is True
    assert report["original_unchanged"] is True
    for k, v in model.state_dict().items():
        assert torch.equal(v, snapshot[k]), k


class _WrongLengthModel(nn.Module):
    """Modelo de propósito errado: devolve N-1 pontos. O smoke test tem de falhar."""

    def __init__(self):
        super().__init__()
        self.conv = nn.Conv1d(C, 1, 1)

    def forward(self, x):
        return self.conv(x)[..., :-1]


def test_smoke_test_fails_on_wrong_output_length():
    torch.manual_seed(0)
    X, y = _synthetic_sequence(20)
    with pytest.raises(AssertionError):
        run_training_smoke_test(_WrongLengthModel(), (X, y), build_loss(), CPU)


# --------------------------------------------------------------------------- treino e avaliação


class _RecordingLoss:
    """Envolve a perda e regista o valor de cada chamada, para verificar a agregação."""

    def __init__(self, inner):
        self.inner = inner
        self.values = []

    def __call__(self, logits, y):
        loss = self.inner(logits, y)
        self.values.append(float(loss.item()))
        return loss


def _mini_loader(lengths, seed=0):
    items = []
    for i, n in enumerate(lengths):
        X, y = _synthetic_sequence(n, seed=seed + i)
        items.append((X, y, {"sequence_id": f"sintetica_{i}"}))
    return items


def test_train_one_epoch_fields_counts_and_weighting():
    torch.manual_seed(0)
    lengths = [5, 12, 30]
    loader = _mini_loader(lengths)
    model = build_cnn(n_channels=C)
    optimizer = build_optimizer(model)
    loss_fn = _RecordingLoss(build_loss())

    result = train_one_epoch(model, loader, optimizer, loss_fn, CPU)

    assert set(result) == {"mean_loss_per_step", "mean_loss_per_point", "n_steps", "n_points", "seconds"}
    assert result["n_steps"] == 3
    assert result["n_points"] == sum(lengths) == 47
    assert result["seconds"] >= 0.0

    values = loss_fn.values
    assert len(values) == 3
    assert result["mean_loss_per_step"] == pytest.approx(sum(values) / 3, rel=1e-9)
    weighted = sum(v * n for v, n in zip(values, lengths)) / sum(lengths)
    assert result["mean_loss_per_point"] == pytest.approx(weighted, rel=1e-9)


def test_evaluate_metrics_match_hand_values():
    # Dois passos com logits fixos (ordem de chamada do modelo):
    #   seq 1: logits [2, -2], y [1, 1] -> pred [1, 0] -> TP 1, FN 1
    #   seq 2: logits [-1, 0.5, 3], y [0, 0, 1] -> pred [0, 1, 1] -> TN 1, FP 1, TP 1
    # Totais: TP=2, FP=1, FN=1, TN=1
    #   precisão = 2/3, sensibilidade = 2/3, F1 = 4/6 = 2/3, IoU = 2/4 = 0.5
    class _FixedLogits(nn.Module):
        def __init__(self, outputs):
            super().__init__()
            self.outputs = list(outputs)
            self.anchor = nn.Parameter(torch.zeros(1))

        def forward(self, x):
            return self.outputs.pop(0)

    logits = [
        torch.tensor([[[2.0, -2.0]]]),
        torch.tensor([[[-1.0, 0.5, 3.0]]]),
    ]
    loader = [
        (torch.zeros(1, C, 2), torch.tensor([[[1.0, 1.0]]]), {"sequence_id": "a"}),
        (torch.zeros(1, C, 3), torch.tensor([[[0.0, 0.0, 1.0]]]), {"sequence_id": "b"}),
    ]
    model = _FixedLogits(logits)
    loss_fn = build_loss()

    result = evaluate_training_subset(model, loader, loss_fn, CPU, threshold=0.5)

    assert result["result_kind"] == "train_or_internal_monitor"
    assert "validation" not in result["result_kind"]
    assert result["counts"] == {"TP": 2, "FP": 1, "FN": 1, "TN": 1}
    assert result["metrics"]["precision"] == pytest.approx(2 / 3)
    assert result["metrics"]["sensitivity"] == pytest.approx(2 / 3)
    assert result["metrics"]["f1"] == pytest.approx(2 / 3)
    assert result["metrics"]["iou"] == pytest.approx(0.5)
    assert not any(result["zero_division_flags"].values())
    assert result["n_steps"] == 2
    assert result["n_points"] == 5

    # Perda por ponto e por passo, calculadas à mão com a BCE estável.
    seq1 = [_bce_point(2.0, 1.0), _bce_point(-2.0, 1.0)]
    seq2 = [_bce_point(-1.0, 0.0), _bce_point(0.5, 0.0), _bce_point(3.0, 1.0)]
    expected_per_step = (sum(seq1) / 2 + sum(seq2) / 3) / 2
    expected_per_point = (sum(seq1) + sum(seq2)) / 5
    assert result["mean_loss_per_step"] == pytest.approx(expected_per_step, rel=1e-6)
    assert result["mean_loss_per_point"] == pytest.approx(expected_per_point, rel=1e-6)


def test_evaluate_zero_division_gives_zero_and_flags():
    class _Constant(nn.Module):
        def __init__(self):
            super().__init__()
            self.anchor = nn.Parameter(torch.zeros(1))

        def forward(self, x):
            return torch.full((1, 1, x.shape[2]), -5.0)

    loader = [(torch.zeros(1, C, 4), torch.zeros(1, 1, 4), {"sequence_id": "neg"})]
    result = evaluate_training_subset(_Constant(), loader, build_loss(), CPU)

    assert result["counts"] == {"TP": 0, "FP": 0, "FN": 0, "TN": 4}
    assert result["metrics"] == {"precision": 0.0, "sensitivity": 0.0, "f1": 0.0, "iou": 0.0}
    assert result["zero_division_flags"] == {
        "precision": True,
        "sensitivity": True,
        "f1": True,
        "iou": True,
    }


def test_evaluate_leaves_model_in_eval_mode_and_train_sets_train_mode():
    model = build_cnn(n_channels=C)
    loader = _mini_loader([8])
    evaluate_training_subset(model, loader, build_loss(), CPU)
    assert model.training is False

    train_one_epoch(model, loader, build_optimizer(model), build_loss(), CPU)
    assert model.training is True


def test_train_one_epoch_and_evaluate_run_on_real_model_with_mixed_lengths():
    torch.manual_seed(0)
    model = build_cnn(n_channels=C)
    loader = _mini_loader([5, 12, 30])
    train_res = train_one_epoch(model, loader, build_optimizer(model), build_loss(), CPU)
    eval_res = evaluate_training_subset(model, loader, build_loss(), CPU)
    assert train_res["n_steps"] == eval_res["n_steps"] == 3
    assert eval_res["n_points"] == 47
    assert sum(eval_res["counts"].values()) == 47
    assert all(math.isfinite(v) for v in eval_res["metrics"].values())


# --------------------------------------------------------------------------- sobreajuste diagnóstico


def test_overfit_single_synthetic_sequence_reduces_loss():
    """DIAGNÓSTICO de capacidade de ajuste: NÃO é generalização.

    Uma sequência sintética minúscula (N=40, 7 canais), alvo y = (canal 0 > 0).
    Taxa de aprendizagem 1e-2 definida explicitamente no teste (não é o placeholder 1e-3).
    """
    N_STEPS = 300
    X, y = _synthetic_sequence(40, seed=0)
    y = (X[:, 0:1, :] > 0).float()  # alvo: função simples do canal 0

    set_reproducibility(42, deterministic=True)
    model = build_cnn(n_channels=C)
    optimizer = build_optimizer(model, {"lr": 1e-2})
    loss_fn = build_loss()

    model.eval()
    with torch.no_grad():
        initial = float(loss_fn(model(X), y))

    model.train()
    for _ in range(N_STEPS):
        optimizer.zero_grad()
        loss = loss_fn(model(X), y)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        final = float(loss_fn(model(X), y))
        pred = (torch.sigmoid(model(X)) >= 0.5).float()
    accuracy = float((pred == y).float().mean())

    assert math.isfinite(final)
    assert final < 0.5 * initial, f"perda inicial {initial:.4f}, final {final:.4f}"
    assert accuracy >= 0.9, f"acerto no próprio exemplo sintético: {accuracy:.3f}"


# --------------------------------------------------------------------------- reprodutibilidade e dispositivo


def test_same_seed_gives_same_initial_loss_and_metadata_is_reported():
    X, y = _synthetic_sequence(25, seed=5)
    loss_fn = build_loss()

    def initial_loss(seed):
        meta = set_reproducibility(seed, deterministic=True)
        model = build_cnn(n_channels=C)
        with torch.no_grad():
            value = float(loss_fn(model(X), y))
        return value, meta

    first, meta = initial_loss(123)
    second, _ = initial_loss(123)
    other, _ = initial_loss(124)

    assert first == second
    assert other != first
    assert {"seed", "python_version", "torch_version", "numpy_version", "deterministic", "num_threads"} <= set(meta)
    assert meta["seed"] == 123
    assert meta["deterministic"] is True


def test_select_device_cpu_and_invalid_values():
    assert select_device("cpu") == torch.device("cpu")
    assert select_device() == torch.device("cpu")
    with pytest.raises(ValueError):
        select_device("tpu")
    if not torch.cuda.is_available():
        with pytest.raises(RuntimeError):
            select_device("cuda")
