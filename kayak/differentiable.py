import numpy as np

class Differentiable(object):

    def __init__(self, parents=[]):
        self._value = None
        self._grad  = {}
        for parent_index, parent in enumerate(parents):
            parent._add_child(self, parent_index)

        self._parents = parents
        self._children = []

    @property
    def value(self):
        """Compute the value of the function.  This walks up the
        dependency graph and finds all of the Kayak objects with known
        values (such as Inputs and Targets, perhaps modulated by a
        Batcher) and then propagates their values forward through the
        modular computations of Differentiable subclasses.  There are
        some subtleties to this behavior, which are determined by the
        method arguments.
        """
        # If the value is not yet cached, compute it.
        if self._value is None:
            self._value = self._compute_value()

        return self._value

    @value.setter
    def value(self, new_value):
        self._clear_value_cache()
        self._value = new_value

    def _clear_value_cache(self):
        """
        Sets the new value and clears the values of any dependencies. We
        maintain the invariant that cached values are never wrong relative
        to their parents' values.
        """
        if self._value is not None:
            [child._clear_value_cache() for child, _ in self._children]
            self._clear_grad_cache()
            self._value = None

    def _clear_grad_cache(self):
        if self._grad:
            [parent._clear_grad_cache() for parent in self._parents]
            self._grad = {}
        
    def grad(self, other):
        """Compute the gradient of this module in terms of another
        module.  One of the main points of the Kayak setup is to
        easily compute gradients in terms of parameters.  This is the
        interface for doing so.  You call the grad() method on
        something that produces a scalar, providing as an argument
        some other object that appears deeper in the graph.  You get
        out an array of the same shape as the deeper object, but which
        is the gradient.

        Arguments:

          other: (Kayak object) The other object, in terms of which
                 you'd like to take this thing's gradient.
        """
        return other._d_out_d_self(self)

    @property
    def shape(self):
        return self.value.shape

    def _d_out_d_self(self, out):
        if out not in self._grad:
            if self is out:
                grad = np.ones(self.shape)
            else:
                grad = np.zeros(self.shape)
                for child, parent_index in self._children:
                    grad += child._d_out_d_parent(out, parent_index)

            self._grad[out] = grad

        return self._grad[out]

    def _d_out_d_parent(self, out, parent):
        return self._local_grad(parent, self._d_out_d_self(out))

    def _add_child(self, child, parent_index):
        """Parent_index is an int that tells out child which parent we are."""
        self._children.append((child, parent_index))

    def _local_grad(self, parent, d_out_d_self):
        """Return d_out_d_self * d_self_d_parent"""
        raise Exception("Class 'Differentiable' is abstract.")

    def _compute_value(self):
        raise Exception("Class 'Differentiable' is abstract.")