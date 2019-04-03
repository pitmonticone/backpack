"""Test Hessian backpropagation of view and batch-wise view layer."""

from torch import (tensor, randn)
from .view import HBPView, HBPViewBatchFlat

from .loss import batch_summed_hessian
from ..utils import torch_allclose, set_seeds
from ..hessian.exact import exact_hessian


def test_shape_view():
    """Test for the correct output shape of view."""
    x = randn(10, 20, 3)
    layer = HBPView((-1, 5, 2))
    out = layer(x)
    assert tuple(out.size()) == (60, 5, 2)

    # invalid shapes
    x = randn(5, 4)
    layer = HBPView((10, 3))
    try:
        out = layer(x)
    except RuntimeError:
        return
    raise Exception("The operation should have failed, but passed.")


def test_shape_view_batch_flat():
    """Test for the correct output shape of batch-wise flat view."""
    x = randn(10, 20, 3)
    layer = HBPViewBatchFlat()
    out = layer(x)
    assert tuple(out.size()) == (10, 60)


def example_input(shape, seed=0):
    """Example input for the view layer."""
    set_seeds(seed)
    x = randn(*shape)
    x.requires_grad = True
    return x


def test_forward_pass_view():
    """Check forward pass for view."""
    shape = (1, 8, 4, 5)
    target_shape = (1, 2, 80)

    # forward pass in PyTorch
    x_1 = example_input(shape)
    out_1 = x_1.view(*target_shape)

    # forward pass in HBP
    x_2 = example_input(shape)
    assert torch_allclose(x_1, x_2)
    layer = HBPView(target_shape)
    out_2 = layer(x_2)
    assert torch_allclose(out_1, out_2)


def test_forward_pass_view_batch_flat():
    """Check forward pass for batch-wise flat view."""
    shape = (1, 8, 4, 5)
    target_shape = (1, 160)

    # forward pass in PyTorch
    x_1 = example_input(shape)
    out_1 = x_1.view(*target_shape)

    # forward pass in HBP
    x_2 = example_input(shape)
    assert torch_allclose(x_1, x_2)
    layer = HBPViewBatchFlat()
    out_2 = layer(x_2)
    assert torch_allclose(out_1, out_2)


def example_loss(tensor):
    """Sum all square entries of a tensor."""
    return (tensor**2).view(-1).sum(0)


def test_input_hessian_view():
    """Check HBP procedure."""
    shape = (1, 8, 4, 5)
    target_shape = (1, 2, 80)
    # Hessian in PyTorch
    x_1 = example_input(shape)
    out_1 = x_1.view(target_shape)
    loss_1 = example_loss(out_1)
    # autodiff to compute the Hessian
    hessian_x_1 = exact_hessian(loss_1, [x_1])

    # Hessian in HBP
    x_2 = example_input(shape)
    layer = HBPView(target_shape)
    out_2 = layer(x_2)
    loss_2 = example_loss(out_2)
    assert torch_allclose(loss_1, loss_2)
    # feed Hessian back
    hessian_out_2 = batch_summed_hessian(loss_2, out_2)
    hessian_x_2 = layer.backward_hessian(hessian_out_2)
    assert torch_allclose(hessian_x_1, hessian_x_2)


def test_input_hessian_view_batch_flat():
    """Check HBP procedure."""
    shape = (1, 8, 4, 5)
    target_shape = (1, 160)
    # Hessian in PyTorch
    x_1 = example_input(shape)
    out_1 = x_1.view(target_shape)
    loss_1 = example_loss(out_1)
    # autodiff to compute the Hessian
    hessian_x_1 = exact_hessian(loss_1, [x_1])

    # Hessian in HBP
    x_2 = example_input(shape)
    layer = HBPViewBatchFlat()
    out_2 = layer(x_2)
    loss_2 = example_loss(out_2)
    assert torch_allclose(loss_1, loss_2)
    # feed Hessian back
    hessian_out_2 = batch_summed_hessian(loss_2, out_2)
    hessian_x_2 = layer.backward_hessian(hessian_out_2)
    assert torch_allclose(hessian_x_1, hessian_x_2)
