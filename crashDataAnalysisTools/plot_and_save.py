import os
import pandas as pd

from matplotlib.backends.backend_pdf import PdfPages


def plot_x_vs_y(df, colname_x, colname_y):
    """
    scatter plot of attribute x against y
    Parameters:
    @df {dataframe} datasource
    @colname_x {string} column name for attribute x
    @colname_y {string} column name for attribute y
    Return:
    the produced figure
    """
    plt.scatter(df[colname_x], df[colname_y])
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
    the produced figure
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    support = np.linspace(-6, 6, 1000)
    ax.plot(support, rmodel.model.cdf(support), 'r-', label=modelname)
    ax.legend()
    return fig


def save_to_pdf(fig, filename):
    """
    Save fig to PDF
    Parameters:
    @fig the figure to be saved
    @filename {string} file name, without suffix
    Return:
    the file path
    """
    pp = PdfPages(filename + '.pdf')
    pp.savefig(fig)
    pp.close()
    return filename + '.pdf'
