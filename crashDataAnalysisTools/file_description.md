# File Description

## Core Functionality
- crash_modeling_tools.py
  - Functions to implement a variety of crash data analyses including (but not limited to) summarization of data, predictive crash modeling, implementation of the Empirical Bayes method, prioritization of sites for safety treatment, and calculation/plotting of confidence and prediction intervals for mixed-Poisson regression models.
- data_prep.py
  - Functions to pre-process the research data from different sources. Working with a sqlite database, the studied datasets were integrated through a series of SQL query statements. Some preliminary plotting functions have also been developed for an initial analysis of the data.
- geohelper.py
  - Functions to plot highway network and crash hot spot map based on the crash sites and crash statistics.

## Unit Tests
- crash_modeling_tools_tester.py
  - Unit tests for the crash_modeling_tools file; that is, testing of the crash data analysis functions
- data_prep_tester.py
  - Unit tests for the data_prep file
  
## Demonstration/Walkthrough Files
- Crash_Modeling_Tools_Walkthrough.ipynb
  - Provides a demonstration of the functionality developed in the crash_modeling_tools files based on a crash dataset from Interstate 90 in Washington State
- data_prep_demo.ipynb
  - Provides a demonstration of the data preparation functions and how the data from different sources are combined
- HotSpotMappingDemo.ipynb
  - Provides a demonstration of the crash data hot spot mapping functionality
