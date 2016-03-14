import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
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
    @spf {numpy y} values of the spf
    Compute the values of the safety performance function (spf)
    using a negative binomial regression model computed via
    the statsmodels package and a given set of predictors
    """
    spf = nb_model.predict(predictors)

    return spf


def compute_alpha(nb_model):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    Return:
    @alpha {float} inverse of nb scale paramter
    This function computes and returns the value of alpha, a parameter used in
    calculation of the nb variance and also in various procedures relying on
    an nb model, such as implementation of the eb method.
    """
    alpha = 1/nb_model.scale
    return alpha


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
    alpha = compute_alpha(nb_model)

    # compute the safety performance function
    spf = compute_spf(nb_model, predictors)

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
                var_eta_hat = var_eta_hat + cov_mat[i, j] * \
                    (data[[i]].as_matrix()**2)
            # covariance term
            else:
                var_eta_hat = var_eta_hat + cov_mat[i, j] * 2 * \
                    data[[i]].as_matrix()*data[[j]].as_matrix()

    return var_eta_hat


def calc_mu_hat_nb(nb_model, data):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @data {pd dataframe} set of predictor variables (design matrix)
    Return:
    @mu_hat_nb {numpy array} vector of values of mu (aka the poisson mean)
    This function is used to compute the value of the Poisson mean at
    varying values of predictors in a given set.
    """
    # make a vector to store the output
    mu_hat_nb = np.zeros([data.shape[0], 1])

    # loop over the model coefficients and multiply each one by
    # the corresponding row in the data frame, add the value
    # to the running sum
    for i in range(0, len(nb_model.params)):
        mu_hat_nb = mu_hat_nb + data[[i]].as_matrix()*nb_model.params[i]

    # since the nb regression model uses a log link function, we must
    # exponentiate the final output
    mu_hat_nb = np.exp(mu_hat_nb)

    return mu_hat_nb


def calc_ci_mu_nb(mu_hat_nb, var_eta_hat):
    """
    Parameters:
    @mu_hat_nb {numpy array} vector of values of mu (aka the poisson mean)
    @var_eta_hat {pd dataframe} vector of variance values for the
    linear predictor
    Return:
    @mu_hat_nb_ci {pd dataframe} dataframe containing the lower and upper
    bounds for the 95% confidence interval (CI) for mu, the Poisson mean
    This function is used to compute the lower and upper bounds of the
    95% confidence interval for the Poisson mean as calcuated based on a
    given predictor set.
    """
    # calcuate the lower bound for the confidence interval for mu
    lb_ci_mu_nb = mu_hat_nb/np.exp(norm.ppf(0.975)*np.sqrt(var_eta_hat))

    # calcuate the upper bound for the confidence interval for mu
    ub_ci_mu_nb = mu_hat_nb*np.exp(norm.ppf(0.975)*np.sqrt(var_eta_hat))

    # combine the columns into a two-dimensional matrix
    mu_ci_matrix = np.column_stack((lb_ci_mu_nb, ub_ci_mu_nb))

    # return the result (i.e., LB and UB as a dataframe)
    mu_hat_nb_ci = pd.DataFrame(mu_ci_matrix, columns=['LB CI mu', 'UB CI mu'])
    return mu_hat_nb_ci


def calc_pi_m_nb(nb_model, mu_hat, var_eta_hat):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @mu_hat_nb {numpy array} vector of values of mu (aka the poisson mean)
    @var_eta_hat {pd dataframe} vector of variance values for the
    linear predictor
    Return:
    @m_nb_pi {pd dataframe} dataframe containing the lower and upper
    bounds for the 95% prediction interval (PI) for m, the Poisson parameter
    (Here, the Poisson mean does not equal the Poisson parameter as the
    parameter includes an error term assumed to follow the gamma distribution)
    This function is used to compute the lower and upper bounds of the
    95% prediction interval for the Poisson parameter as calcuated based on a
    given predictor set. Alternately, m is known as the safety.
    """
    # compute alpha (the nb dispersion parameter)
    alpha = compute_alpha(nb_model)

    # calcuate the lower bound for the prediction interval for m
    lb_pi_m_nb = np.maximum(0, mu_hat-norm.ppf(0.975)*np.sqrt(mu_hat**2 *
                            (alpha*(var_eta_hat+1)+var_eta_hat)))

    # calcuate the lower bound for the prediction interval for m
    ub_pi_m_nb = mu_hat+norm.ppf(0.975)*np.sqrt(mu_hat**2*(alpha *
                                                (var_eta_hat+1)+var_eta_hat))

    # combine the columns into a two-dimensional matrix
    m_pi_matrix = np.column_stack((lb_pi_m_nb, ub_pi_m_nb))

    # return the result (i.e., LB and UB as a dataframe)
    m_nb_pi = pd.DataFrame(m_pi_matrix, columns=['LB PI m', 'UB PI m'])
    return m_nb_pi


def calc_pi_y_nb(nb_model, mu_hat, var_eta_hat):
    """
    Parameters:
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @mu_hat_nb {numpy array} vector of values of mu (aka the poisson mean)
    @var_eta_hat {pd dataframe} vector of variance values for the
    linear predictor
    Return:
    @y_nb_pi {pd dataframe} dataframe containing the lower and upper
    bounds for the 95% prediction interval (PI) for y, the predicted response
    (i.e., crash count at site i) which follows a Poisson distribution when
    conditioned on the safety m.
    This function is used to compute the lower and upper bounds of the
    95% prediction interval for the predicted response as calcuated based on a
    given predictor set.
    """
    # compute alpha (the nb dispersion parameter)
    alpha = compute_alpha(nb_model)

    # calcuate the lower bound for the prediction interval for y
    lb_pi_y_nb = np.zeros(mu_hat.shape[0])

    # calcuate the lower bound for the prediction interval for m
    ub_pi_y_nb = np.floor(mu_hat+np.sqrt(19)*np.sqrt(mu_hat**2 *
                          (alpha*(var_eta_hat+1)+var_eta_hat)))

    # combine the columns into a two-dimensional matrix
    y_pi_matrix = np.column_stack((lb_pi_y_nb, ub_pi_y_nb))

    # return the result (i.e., LB and UB as a dataframe)
    y_nb_pi = pd.DataFrame(y_pi_matrix, columns=['LB PI y', 'UB PI y'])
    return y_nb_pi


def plot_and_save_nb_cis_and_pis(data_design, nb_model, mu_hat,
                                 var_eta_hat, x_axis_range, x_axis_label):
    """
    Parameters:
    @data_design {pd dataframe} set of predictor variables (design matrix)
    @nb_model {statsmodels genmod} negative binomial (nb) regression model
    @mu_hat_nb {numpy array} vector of values of mu (aka the poisson mean)
    @var_eta_hat {pd dataframe} vector of variance values for the
    linear predictor
    @x_axis_range {numpy array} specifies numerical range of x-axis
    @x_axis_label {String} label for x-axis
    Return:
    @y_nb_pi {pd dataframe}

    This function plots mu as as well as the CIs for mu and the PIs for m
    and y. It also saves the plot as a .png figure.
    """
    # calculate the associated confidence and prediction intervals for mu_hat
    ci_mu_nb = calc_ci_mu_nb(mu_hat, var_eta_hat)
    pi_m_nb = calc_pi_m_nb(nb_model, mu_hat, var_eta_hat)
    pi_y_nb = calc_pi_y_nb(nb_model, mu_hat, var_eta_hat)

    # plot mu_hat
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
    mu_hat, = plt.plot(x_axis_range, mu_hat)

    # plot the 95% ci for mu
    lb_ci_mu, = ax.plot(x_axis_range, ci_mu_nb['LB CI mu'], linestyle=':')
    ub_ci_mu, = ax.plot(x_axis_range, ci_mu_nb['UB CI mu'], linestyle='--')

    # plot the 95% pi for m
    lb_pi_m, = ax.plot(x_axis_range, pi_m_nb['LB PI m'])
    ub_pi_m, = ax.plot(x_axis_range, pi_m_nb['UB PI m'], linestyle='-.')

    # plot the 95% pi for y
    lb_pi_y, = ax.plot(x_axis_range, pi_y_nb['LB PI y'])
    ub_pi_y, = ax.plot(x_axis_range, pi_y_nb['UB PI y'], linestyle='-')

    # set the plot labels
    plt.title('95% CIs and PIs for NB Model', fontsize=16)
    plt.xlabel(x_axis_label, fontsize=14)
    plt.xlim(np.min(x_axis_range), np.max(x_axis_range))
    plt.ylabel('Number of Crashes', fontsize=14)

    # create a legend and make it appear outside of the plot space
    plt.legend([mu_hat, lb_ci_mu, ub_ci_mu, lb_pi_m, ub_pi_m, lb_pi_y,
                ub_pi_y], ['mu_hat', 'LB CI mu', 'UB CI mu', 'LB PI m',
                           'UB PI m', 'LB PI y', 'UB PI y'],
               loc='center left', bbox_to_anchor=(1, 0.5), fontsize=14)

    # set the plot size and save
    fig.set_size_inches(10, 6, forward=True)
    fig.savefig('nb_cis_and_pis.png')
