from crash_modeling_tools import *
import numpy as np
import os
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import unittest


class CrashModelingToolsTester(unittest.TestCase):
    """
    In many unit test functions, we need call functions that take different
    datasets or intermediate results (numpy arrays, statsmodels genmods,
    pandas dataframes etc.). Below, prior to doing any unit testing, we
    set such data up.
    """

    # load in a standard dataset
    cwd = os.getcwd()
    crash_data_path = '../data/unit_test_data/crash_data_final_90_test.csv'
    crash_data = pd.read_csv(crash_data_path)
    crash_data = crash_data.dropna()

    # compute the offset term and fit a nb regression model
    offset_term = np.log(crash_data['seg_lng'] * 3)

    # need to cast log_avg_aadt to float since statsmodels thinks
    # (incorrectly) that it is categorical
    crash_data['log_aadt'] = crash_data.log_avg_aadt.astype(np.float)
    mod_nb = smf.glm('tot_acc_ct~log_aadt+lanewid+avg_grad+C(curve)+\
                     C(surf_typ)', data=crash_data, offset=offset_term,
                     family=sm.families.NegativeBinomial()).fit()

    # load a new dataset on which to apply the eb method
    eb_data_path = '../data/unit_test_data/crash_data_eb_test.csv'
    data_eb = pd.read_csv(eb_data_path)
    data_eb = data_eb.dropna()
    data_eb['log_aadt'] = data_eb.log_avg_aadt.astype(np.float)
    segment_lengths = data_eb['seg_lng']
    observed_crash_ct = data_eb['tot_acc_ct']

    # predict the values of the spf
    spf = compute_spf(mod_nb, data_eb)

    # load a dataset to represent the design matrix for the modeling and ci/pi
    data_design_path = '../data/unit_test_data/data_design_test.csv'
    data_design = pd.read_csv(data_design_path)

    # calculate the variance of the linear predictor
    var_eta_hat = calc_var_eta_hat(mod_nb, data_design)

    # calculate the Poisson mean
    mu_hat = calc_mu_hat_nb(mod_nb, data_design)

    def test_show_summary_stats_continuous(self):
        """
        Test that the function used to show summary stats works properly
        for dataframes with continuous variables.
        """
        # call the function to get summary stats for continuous variables
        cont = show_summary_stats(self.crash_data)

        # check that a continuous variable is included in the dataframe
        self.assertTrue('medwid' in cont.columns)
        # check that a categorical variable is NOT included in the dataframe
        self.assertTrue('curve' not in cont.columns)

    def test_show_summary_stats_categorical(self):
        """
        Test that the function used to show summary stats works properly
        for dataframes with categorical variables.
        """
        # call the function to get summary stats for continuous variables
        # column 9 is curve indicator variable
        categorical = show_summary_stats(self.crash_data, [9])

        # check that a categorical variable is  included in the dataframe
        self.assertTrue('curve' in categorical.columns)

        # check that a continuous variable is NOT included in the dataframe
        self.assertTrue('medwid' not in categorical.columns)

    def test_compute_spf(self):
        """
        Test the function computing the spf on a different dataset. If it
        works correctly, it should return a non-zero vector of predictions
        based on the developed nb regression model.
        """
        # count the number of non-zero entries
        non_zeros = np.count_nonzero(self.spf)

        # check that the number of non-zero entries=length of spf vector
        self.assertTrue(non_zeros == len(self.spf))

    def test_compute_alpha(self):
        """
        Here, we test the function used to compute alpha, the dispersion
        parameter associated with the nb regression. Since we are aware
        of overdispersion in the dataset, the scale parameter, and in
        turn, the value of alpha itself should have a non-zero value.
        """
        self.assertTrue(compute_alpha(self.mod_nb) != 0)

    def test_compute_eb_weights(self):
        """
        Test computation of the weight vector used in eb calculations.
        All entries should be non-zero and further positive.
        """
        w = compute_eb_weights(self.mod_nb, self.data_eb, self.segment_lengths)

        # count the number of non-zero entries and make sure it is
        # equal to the length as the weight vector
        # use [0] to get the array of indices with positive entries only
        self.assertTrue(len(np.where(w > 0)[0]) == len(w))

    def test_estimate_empirical_bayes(self):
        """
        Here, we check that all eb estimates obtained are greater than 0
        as the number of preicted crashes must be positive and is comprised
        of a sum of two terms, each of which is itself positive.
        """
        eb_est = estimate_empirical_bayes(self.mod_nb, self.data_eb,
                                          self.segment_lengths,
                                          self.observed_crash_ct)

        self.assertTrue(len(np.where(eb_est > 0)[0]) == len(eb_est))

    def test_calc_accid_reduc_potential(self):
        """
        Values of ARP will be non-zero, but can be both positive or negative.
        Simply check that all values are non-zero.
        """
        arp = calc_accid_reduc_potential(self.mod_nb, self.data_eb,
                                         self.segment_lengths,
                                         self.observed_crash_ct)

        self.assertTrue(len(np.where(arp != 0)[0]) == len(arp))

    def test_calc_var_eta_hat(self):
        """
        All values in the variance vector for the linear predictor evaluated
        at different variables must greater than zero. We check this here.
        """
        self.assertTrue(len(np.where(self.var_eta_hat > 0)[0]) ==
                        len(self.var_eta_hat))

    def test_calc_mu_hat_nb(self):
        """
        All values in the vector reprsenting the Poisson mean must be
        positive. We check this here.
        """
        self.assertTrue(len(np.where(self.mu_hat > 0)[0]) == len(self.mu_hat))

    def test_calc_ci_mu_nb(self):
        """
        Check that a dataframe with two columns is returned and that all
        entries in both columns are greater than 0.
        """
        ci_mu_nb = calc_ci_mu_nb(self.mu_hat, self.var_eta_hat)

        # check that a df with 2 columns is returned
        self.assertTrue(len(ci_mu_nb.columns) == 2)

        # confirm the entries are greater than zero
        self.assertTrue(len(np.where(ci_mu_nb[[0]] > 0)[0]) ==
                        len(ci_mu_nb[[0]]))
        self.assertTrue(len(np.where(ci_mu_nb[[1]] > 0)[0]) ==
                        len(ci_mu_nb[[1]]))

    def test_calc_pi_m_nb(self):
        """
        Check that a dataframe with two columns is returned and that all
        entries in column 0 are greater than or equal to 0, while all entries
        in column 1 are greater than 0.
        """
        pi_m_nb = calc_pi_m_nb(self.mod_nb, self.mu_hat, self.var_eta_hat)

        # check that a df with 2 columns is returned
        self.assertTrue(len(pi_m_nb.columns) == 2)

        # confirm the entries are greater than or equal to zero for column 0
        # and greater than 0 for column 1
        self.assertTrue(len(np.where(pi_m_nb[[0]] >= 0)[0]) ==
                        len(pi_m_nb[[0]]))
        self.assertTrue(len(np.where(pi_m_nb[[1]] > 0)[0]) ==
                        len(pi_m_nb[[1]]))

    def test_calc_pi_y_nb(self):
        """
        Check that a dataframe with two columns is returned and that all
        entries in column 0 are equal to 0, while all entries in column 1
        are greater than 0.
        """
        pi_y_nb = calc_pi_y_nb(self.mod_nb, self.mu_hat, self.var_eta_hat)

        # check that a df with 2 columns is returned
        self.assertTrue(len(pi_y_nb.columns) == 2)

        # confirm the entries are greater than zero
        self.assertTrue(len(np.where(pi_y_nb[[0]] == 0)[0]) ==
                        len(pi_y_nb[[0]]))
        self.assertTrue(len(np.where(pi_y_nb[[1]] > 0)[0]) ==
                        len(pi_y_nb[[1]]))

    def test_plot_and_save_nb_cis_and_pis(self):
        """
        Here, we test the plotting function by making sure that it properly
        generates and saves the plot.
        """
        # fix an aadt range
        aadt_range = np.arange(9700, 148400, 100)

        # call the plot function
        plot_and_save_nb_cis_and_pis(self.data_design, self.mod_nb,
                                     self.mu_hat, self.var_eta_hat,
                                     aadt_range, 'AADT')

        # check that an image file with the proper file name exists
        self.assertTrue(os.path.exists(self.cwd + '//nb_cis_and_pis.png'))

        # check that an image file with an improper file name does not exist
        self.assertFalse(os.path.exists(self.cwd + '//cis_and_pis.png'))

if __name__ == '__main__':
    unittest.main()
