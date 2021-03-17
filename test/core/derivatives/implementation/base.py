class DerivativesImplementation:
    """Base class for autograd and BackPACK implementations."""

    def __init__(self, problem):
        self.problem = problem

    def jac_mat_prod(self, mat):
        raise NotImplementedError

    def jac_t_mat_prod(self, mat, subsampling=None):
        """Apply transposed output-input Jacobian to a matrix."""
        raise NotImplementedError

    def weight_jac_t_mat_prod(self, mat, sum_batch, subsampling=None):
        raise NotImplementedError

    def bias_jac_t_mat_prod(self, mat, sum_batch, subsampling=None):
        raise NotImplementedError

    def weight_jac_mat_prod(self, mat):
        raise NotImplementedError

    def bias_jac_mat_prod(self, mat):
        raise NotImplementedError
