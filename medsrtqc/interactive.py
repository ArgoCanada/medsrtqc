
"""
When developing QC code interactively it is often useful to generate
plots. This module is a thin wrapper around the ``matplotlib.pyplot``
module that generates the plot that you probably want as a glimpse
of a :class:`medsrtqc.core.Profile` or :class:`medsrtqc.core.Trace`.
These functions are most usefully invoked in a Jupyter Notebook
or similar environment. These functions require
`matplotlib <https://matplotlib.org/>` to be installed.
"""

import matplotlib.pyplot as plt
import numpy as np
from .core import Trace, Profile


def plot_trace(x, ax=None, trace_attrs=None):
    """
    Plot a :class:`medsrtqc.core.Trace` object.

    :param x: A :class:`medsrtqc.core.Trace` object
    :param ax: An existing set of matplotlib ``Axes``
    :param trace_attrs: A subset tuple of ``'value'``, ``'adjusted'``
        and/or ``'ajusted_error'``. Plotting QC flags is not
        implemented yet.
    """

    ax_none = ax is None
    if ax_none:
        ax = plt.axes()

    if trace_attrs is None:
        trace_attrs = ('value', 'adjusted')

    if 'value' in trace_attrs:
        ax.plot(x.value, x.pres)

    if np.any(~x.adjusted.mask):
        adj = x.adjusted.copy()
        adj[adj.mask] = np.nan
        err = x.adjusted_error.copy()
        err[err.mask] = 0

        if 'adjusted' in trace_attrs:
            ax.plot(adj, x.pres)

        if 'adjusted_error' in trace_attrs:
            ax.errorbar(adj, x.pres, xerr=err)

    if ax_none:
        ax.invert_yaxis()

    return ax


def plot_profile(x, fig=None, ax=None, vars=None, trace_attrs=None):
    """
    Plot a :class:`medsrtqc.core.Profile` object.

    :param x: A :class:`medsrtqc.core.Profile` object
    :param fig: An existing matplotlib ``Figure`` such as that returned
        by ``matplotlib.pyplot.subplots()``.
    :param ax: An existing set of matplotlib ``Axes`` or array of these
        as returned by ``matplotlib.pyplot.subplots()``.
    :param vars: An iterable of variables to plot or ``None`` to plot
        them all.
    :param trace_attrs: Passed to :func:`plot_trace`.
    """

    if vars is None:
        vars = list(x.keys())

    if not vars:
        return plt.subplots(1, 1)

    ncol = int(np.ceil(np.sqrt(len(vars))))
    nrow = (len(vars) - 1) // ncol + 1

    fig_none = fig is None
    if fig_none:
        fig, axs = plt.subplots(nrow, ncol, sharey=True)
    else:
        axs = ax

    for i, var in enumerate(vars):
        ax = plt.subplot(nrow, ncol, i + 1)
        plot(x[var], fig=fig, ax=ax, trace_attrs=trace_attrs)
        ax.set_xlabel(var)
        if i == 0:
            ax.invert_yaxis()

    if fig_none:
        fig.tight_layout()

    return fig, axs


def plot(x, fig=None, ax=None, vars=None, trace_attrs=None):
    """
    A convenience method that either calls :func:`plot_profile` or
    :func:`plot_trace` depending on the class of ``x``.

    >>> from medsrtqc.core import Trace, Profile
    >>> from medsrtqc.interactive import plot
    >>> trace = Trace([1, 2, 4], adjusted=[2, 3, 5], pres=[0, 1, 2])
    >>> plot(trace)
    >>> plot(Profile({'param1': trace}))
    """

    if isinstance(x, Trace):
        return plot_trace(x, ax=ax, trace_attrs=trace_attrs)
    elif isinstance(x, Profile):
        return plot_profile(x, fig=fig, ax=ax, vars=vars, trace_attrs=trace_attrs)
    else:
        raise TypeError(f"Don't know how to plot() object of type '{type(x).__name__}'")
