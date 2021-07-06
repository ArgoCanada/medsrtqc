
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.fromnumeric import trace
from .core import Trace, Profile

def _iter_axs(axs):
    if isinstance(axs, plt.Axes):
        yield axs
    else:
        for ax in axs:
            yield ax

def plot(x, fig=None, ax=None, vars=None, trace_attrs=None):

    if isinstance(x, Trace):
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

    elif isinstance(x, Profile):
        if vars is None:
            vars = list(x.keys())
        else:
            vars = list(vars)

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
    else:
        raise TypeError(f"Don't know how to plot() object of type '{type(x).__name__}'")
