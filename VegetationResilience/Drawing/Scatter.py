import os

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

def scatter(x, y, function_format=None, ee=False, ci=95):
    # plot scatter
    fig, ax = plt.subplots(figsize=(15, 15))
    ax: plt.Axes
    if ee:
        data = pd.DataFrame({"Reference": x, "True": y})
        sns.regplot(data=data, x="Reference",y="True", ax=ax, ci=ci,
                    color="k",
                    scatter_kws={'s': 1, 'alpha': 0.5},
                    line_kws={'linewidth': 2})
    else:
        ax.scatter(x, y, edgecolors=None, c='k', s=3, alpha=0.5)
        x_2 = sm.add_constant(x)
        # fit line
        x1 = np.linspace(x.min(), x.max(), 100)
        y1 = np.linspace(y.min(), y.max(), 100)
        # a, b = curve_fit(function_format, x, y)[0]
        # y2 = a * x + b
        model = sm.OLS(y, x_2).fit()
        _ci = 95
        if ci is not None:
            _ci = ci
        # re = model.get_prediction(x_2).conf_int(alpha=(1-_ci/100))
        re = model.get_prediction(x_2).conf_int(alpha=0.999)
        iv_l = re[:, 0]
        iv_u = re[:, 1]
        ax.plot(x1, y1, color='k', linestyle='--')
        y2 = model.predict(x_2)
        ax.plot(x, y2, color='r', linestyle='--')
        x = x[::50]
        iv_l = iv_l[::50]
        iv_u = iv_u[::50]
        ax.plot(x, iv_l, color="blue", linestyle='-')
        ax.plot(x, iv_u, color="blue", linestyle='-')
        ax.fill_between(x, iv_l, iv_u, color='grey', alpha=0.5)
    # ax.legend()
    ax.set_xlim(0)
    ax.set_ylim(0)
    plt.savefig(os.path.join(".\\", "VerifyPlot.png"))
    print("done")


if __name__ == "__main__":
    pass
