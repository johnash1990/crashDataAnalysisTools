import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd


def fit_nb_model:
    return

def fit_poisson_model:
    return

def estimate_empirical_bayes(nb_model, predictors, segment_lengths, observed_crash_ct):
    # the NB variance is mu+alpha*mu^2 where alpha=1/scale param of the NB distr
    # extract the scale param and get alpha
    alpha = 1/modNB.scale

    # compute the safety performance function
    spf = modNB.predict(predictors)

    # compute the weight factor
    # w_i 1/(1+spf_i/(alpha*L_i^gamma)), take gamma=1
    w = 1/(1+(spf/(alpha*segment_lengths)))

    # compute the safety (i.e., expected crash count at each site as weighted
    # sum of predicted and observed crash count)
    pi = (w*spf) + (1-w)*observed_crash_ct

    return pi
    
def calc_arp:
    return


def calc_ci_mu:
    return

def calc_pi_m:
    return

def calc_pi_y:
    return

def plot_all_intervals:
    return

#def plot
