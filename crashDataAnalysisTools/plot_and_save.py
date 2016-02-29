import os
import pandas as pd
import numpy as np

from matplotlib.backends.backend_pdf import PdfPages


def plot_x_vs_y(df, colname_x, colname_y):
    """
    scatter plot of attribute x against y
    Parameters:
    @df {dataframe} datasource
    @colname_x {string} column name for attribute x
    @colname_y {string} column name for attribute y
    Return:
    @fig {matplotlib.figure} the produced figure
    """
    plt.scatter(df[colname_x], df[colname_y])
    plt.title(colname_x+' vs. '+colname_x)
    plt.xlabel(colname_x)
    plt.ylabel(colname_y)
    plt.show()
    return plt.figure()


def plot_model_cdf(rmodel, lowerb, upperb, modelname):
    """
    plot of model CDF
    Parameters:
    @model a regression model, e.g. Logit model or Probit model
    @lowerb {float} the lower bound of the dataset
    @upperb {float} the upper bound of the dataset
    @modelname {float} the name of the model, e.g. Probit or Logit
    Return:
    @fig {matplotlib.figure} the produced figure
    """

    # specify the figure size
    fig = plt.figure(figsize=(12, 8))

    # specify the grid parameters encoded as a single integer.
    # For example, "111" means "1x1 grid, first subplot"
    # and "234" means "2x3 grid, 4th subplot".
    ax = fig.add_subplot(111)

    # Return 1000 evenly spaced numbers over the specified interval
    # as the sample points
    support = np.linspace(lowerb, upperb, 1000)

    # plot the figure, title, labels and legend
    ax.plot(support, rmodel.model.cdf(support), 'r-', label=modelname)
    ax.title('CDF of' + modelname)
    ax.xlabel('x')
    ax.ylabel('CDF')
    ax.legend()
    return fig
