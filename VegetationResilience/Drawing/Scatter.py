import os

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy.stats as stats

# plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'Calibri'

def scatter(x, y, ee: int=1, ci=95, file_name: str="default_scatter.png", file_dir: str=".\\", r_2=None,
            rmse=None):
    # plot scatter
    fig, ax = plt.subplots(figsize=(15, 15))
    ax: plt.Axes
    if ee==1:
        data = pd.DataFrame({"Reference": x, "Model": y})
        sns.regplot(data=data, x="Reference",y="Model", ax=ax, ci=ci,
                    color="k",
                    scatter_kws={'s': 1, 'alpha': 0.5},
                    line_kws={'linewidth': 2})
    elif ee==2:
        ax.scatter(x, y, edgecolors=None, c='k', s=5, alpha=0.5)
        x_2 = sm.add_constant(x)
        # fit line
        # x1 = np.linspace(x.min(), x.max(), 100)
        # y1 = np.linspace(y.min(), y.max(), 100)
        # a, b = curve_fit(function_format, x, y)[0]
        # y2 = a * x + b
        model = sm.OLS(y, x_2).fit()
        _ci = 95
        if ci is not None:
            _ci = ci
        # re = model.get_prediction(x_2).conf_int(alpha=(1-_ci/100))
        re = model.get_prediction(x_2).conf_int(alpha=0.1)
        iv_l = re[:, 0]
        iv_u = re[:, 1]
        # ax.plot(x1, y1, color='k', linestyle='--')
        y2 = model.predict(x_2)
        ax.plot(x, y2, color='r', linestyle='--')
        intercept = (y2[-1] - y2[0]) / (x[-1] - x[0])
        b = y2[0] - intercept * x[0]
        text = (f"y = {intercept:.3f}x + {b:.3f}\n"
                f"R$^2$ = {r_2:.3f}"+"\n"+
                f"RMSE = {rmse:.3f}")
        ax.text(0.1, 0.9, text, fontsize=30,
                horizontalalignment='left', verticalalignment='top',
                transform=ax.transAxes)
        # x = x[::10]
        # iv_l = iv_l[::10]
        # iv_u = iv_u[::10]
        # ax.plot(x, iv_l, color="blue", linestyle='-')
        # ax.plot(x, iv_u, color="blue", linestyle='-')
        # ax.fill_between(x, iv_l, iv_u, color='grey', alpha=0.5)
    elif ee == 3:
        ax.scatter(x, y, edgecolors=None, c='k', s=3, alpha=0.3)
        fit_plot_line(x, y, ax, ci)
    # ax.legend()
    # ax.set_xlim(0, 10)
    # ax.set_ylim(0, 10)
    ax.set_xlim(0,9)
    ax.set_ylim(0,9)
    ax.set_xlabel(r'Reference NPP (gC/m$^2\cdot$day)', fontsize=30)
    ax.set_ylabel('Modelled NPP (gC/m$^2\cdot$day)', fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=25)
    lim = max(max(x), max(y))
    x = [0, lim+10]
    y = [0, lim+10]
    ax.plot(x, y, 'k--')  # 'k--'表示黑色虚线
    plt.rcParams['agg.path.chunksize'] = 200
    plt.savefig(os.path.join(file_dir, file_name))
    print("done")



def fit_plot_line(x, y, ax, ci=95):

    alpha = 1 - ci / 100
    n = len(x)

    Sxx = np.sum(x**2) - np.sum(x)**2 / n
    Sxy = np.sum(x * y) - np.sum(x)*np.sum(y) / n
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Linefit
    b = Sxy / Sxx
    a = mean_y - b * mean_x

    # Residuals
    def fit(xx):
        return a + b * xx

    residuals = y - fit(x)

    var_res = np.sum(residuals**2) / (n - 2)
    sd_res = np.sqrt(var_res)

    # Confidence intervals
    se_b = sd_res / np.sqrt(Sxx)
    se_a = sd_res * np.sqrt(np.sum(x**2)/(n * Sxx))

    df = n-2                            # degrees of freedom
    tval = stats.t.isf(alpha/2., df) 	# appropriate t value

    ci_a = a + tval * se_a * np.array([-1, 1])
    ci_b = b + tval * se_b * np.array([-1, 1])

    # create series of new test x-values to predict for
    npts = 1000
    px = np.linspace(np.min(x), np.max(x), num=npts)

    def se_fit(x):
        return sd_res * np.sqrt(1. / n + (x - mean_x)**2 / Sxx)


    # Plot the data
    pic = ax
    pic.plot(px, fit(px), 'r', label='Regression line')
    pic.plot(x, y, 'k.')

    x.sort()
    limit = (1 - alpha) * 100
    pic.plot(x, fit(x) + tval * se_fit(x), '--', color='gray', lw=1,
             label='Confidence limit ({0:.1f}%)'.format(limit))
    pic.plot(x, fit(x) - tval * se_fit(x), '--', color='gray', lw=1)


if __name__ == "__main__":
    pass
