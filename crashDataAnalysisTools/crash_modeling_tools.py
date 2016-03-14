import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


def show_summary_stats(data, cat_var_indices=[9999]):
    """
    Parameters:
    @data {pd dataframe} dataset for which to compute summary statistics
    @cat_var_indices {list} list of indices of catergorical variables
    Return:
    @summary_stats {pd dataframe} summary statistics for variables
    Compute the summary statistics for the variables in a given dataframe.
    By default, we assume no categorical variables, since the summary
    statistics are defined differently for them as opposed to continuous
    variables (e.g., there is no mean etc.). If the user wants to see
    the summary stats for the categorical variables, they must specify
    a list of indices in the dataframe to which the categorical variables
    correspond.
    """
    # use [9999] as default for no categorical vars
    # return the summary stats of the continuous variables
    if cat_var_indices == [9999]:
        summary_stats = data.describe()
        return summary_stats
    # return the summary stats of the categorical variables
    else:
        summary_stats = data[cat_var_indices].describe()
        return summary_stats


def compute_spf(nb_model, predictors):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @predictors {pd dataframe} set of predictor variables
    Return:
    @spf {numpy array} values of the spf
    Compute the values of the safety performance function (spf)
    using a negative binomial regression model computed via
    the statsmodels package and a given set of predictors
    """
    spf = nb_model.predict(predictors)

    return spf


def compute_eb_weights(nb_model, predictors, segment_lengths):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @predictors {pd dataframe} set of predictor variables
    @segment_lengths {pd series} vector of segment lengths
    Return:
    @w {numpy array} weight parameter values
    Compute the weights to be used in the empirical bayes (eb) method.
    The weights (w) are calculated based upon a negative binomial
    regression model, a set of predictors, and the lengths of each
    segment/study site.
    """
    # the nb variance is mu+alpha*mu^2 where alpha=1/scale param of the
    # nb distr extract the scale param and get alpha
    alpha = 1/nb_model.scale

    # compute the safety performance function
    spf = compute_spf(nb_model, predictors)
    # spf = nb_model.predict(predictors)

    # compute the weight factor
    # w_i 1/(1+spf_i/(alpha*L_i^gamma)), take gamma=1
    w = 1/(1+(spf/(alpha*segment_lengths)))

    # return the weights
    return w


def estimate_empirical_bayes(nb_model, predictors, segment_lengths,
                             observed_crash_ct):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @predictors {pd dataframe} set of predictor variables
    @segment_lengths {pd series} vector of segment lengths
    @observed_crash_ct {pd series} vector of observed crash counts
    Return:
    @pi {pd dataframe} vector of eb estimtes (safety values)
    Compute and return the estimates from the empirical bayes method.
    The estimates (pi) are a weighted combination of the predicted
    number of crashes and observed number of crashes at each site.
    """
    # compute the vector of weights
    w = compute_eb_weights(nb_model, predictors, segment_lengths)

    # compute the safety performance function
    spf = compute_spf(nb_model, predictors)

    # compute the safety (i.e., expected crash count at each site as weighted
    # sum of predicted and observed crash count)
    pi = (w*spf) + (1-w)*observed_crash_ct

    # convert to a data frame
    pi = pd.DataFrame(pi, columns=['Safety'])

    # return the vector of safety values
    return pi


def calc_accid_reduc_potential(nb_model, predictors, segment_lengths,
                               observed_crash_ct):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @predictors {pd dataframe} set of predictor variables
    @segment_lengths {pd series} vector of segment lengths
    @observed_crash_ct {pd series} vector of observed crash counts
    Return:
    @arp {pd dataframe} vector of arp values
    Caluclates and returns the value of accident reduction potential (arp)
    at each site. arp is a measure used to rank sites for prioritizing
    safety treatments.
    """
    # compute the vector of weights
    w = compute_eb_weights(nb_model, predictors, segment_lengths)

    # compute the safety performance function
    spf = compute_spf(nb_model, predictors)

    # compute the accident reduction potential
    arp = (1-w)*(observed_crash_ct-spf)

    # convert to a dataframe
    arp = pd.DataFrame(arp, columns=['ARP'])

    return arp


def calc_var_eta_hat(model, data):
    """
    Parameters:
    @model {statsmodels genmod} negative binomial (nb) regression model
    @data {pd dataframe} set of predictor variables (design matrix)
    Return:
    @var_eta_hat {pd dataframe} vector of variance values for the
    linear predictor
    This function is used to compute the variance of the linear predictor
    eta_hat, which is used later in calculation of various confidence
    intervals.
    """
    # make a vector of zeros to store the output
    var_eta_hat = np.zeros([data.shape[0], 1])

    # get the variance-covariance matrix, convert from pd dataframe
    # to numpy matrix
    cov_mat = model.normalized_cov_params.as_matrix()

    # add a column of 1's to the design matrix for beta_0
    data.insert(0, 'intercept', 1)

    # loop through the upper right half of the cov mat
    for i in range(0, len(model.params)):
        for j in range(0, i+1):
            # variance term
            if (i == j):
                var_eta_hat = var_eta_hat + cov_mat[i, j]
                *(data[[i]].as_matrix()**2)
            # covariance term
            else:
                var_eta_hat = var_eta_hat + cov_mat[i, j]*2
                *data[[i]].as_matrix()*data[[j]].as_matrix()

    return var_eta_hat


def calc_ci_mu:
    return


def calc_pi_m:
    return


def calc_pi_y:
    return


def plot_all_intervals:
    return
