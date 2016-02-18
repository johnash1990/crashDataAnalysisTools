# Crash Data Analysis Tool (CDAT) Design Manual

Vehicle accident is a world-wide problem that can transportation agencies are facing. Depending on the severity of the accident, it may result in property damage, personal injury or death. Traffic accidents are responsible for great social and economical costs and enormous efferts were made to reduce crash rates as well as to mitigate crash impacts.

A number of factors can contribute to the risk of vehicle crash, including vehicle design and operation status, traffic flow conditions, roadway design, and human factors. Previous studies have developed some general forms of crash model to help reveal the impact of some factors.

The objective of the research is to understand how on-road crash is related to different types of factors, including traffic flow parameters, roadway geometry, and weather conditions. In addressing the problem, three different data sources (HSIS, Freeway Elevation Dataset, Weather Data) are integrated containing those factors. Users can refer to the data description markdown file for more details about the datasets. Analysis of the datasets focusing on the several following tasks:

# Tasks
- Obtain crash data, road network data, elevation data and weather data and compile them together.
- Investigate necessary packages to perform modeling and visualization tasks.
- Apply statistical model package to the data to develop crash prediction models and crash serverity models.
- Interpret the results with interactive plots and tables.
- Identify the crash hotspots through methods from literature research.
- Provide a tool to help people analyze different aspects of crash data.

# Use Cases

## Use Case 1: Plot the crash frequency versus an independent variable that can be chosen by the user.
- Data frame with crash frequency (dependent variable) and one or more independent variables
- Package to perform plotting/visualization (also to save plot to file)
- User interface to specify independent variables via ipython widgets and view plot results
- Control logic

## Use Case 2: Develop a crash frequency model (i.e., a multivariate negative binomial regression model) based upon a given data frame.
- Data frame with crash frequency (dependent variable) and one or more independent variables
- Statistical modeling package to develop prediction model (negative binomial model)
- User interface to show results of modeling
- Control logic

## Use Case 3: Develop a crash severity model (i.e., a multinomial logit regression model) based upon a given data frame.
- Data frame with crash severity (dependent variable) and one or more independent variables
- Statistical modeling package to develop model (logit model)
- User interface to show results of modeling
- Control logic

## Use Case 4: Predict the crash frequency at a new site.
- Prediction model developed from a previous use case
- Values of the independent variables to be used in the prediction
- User interface to output the results of the prediction
- Control logic

## Use Case 5: Determine the hotspot rating of a list of sites.
- Data frame with list of sites, their characteristics, and crash counts
- Procedure to determine hotspot ranking based on literature search
- User interface to display results
- Package to export ranking list to file
- Control logic

**NOTE:** This is a preliminary list of use cases that will likely be updated and modified as the project progresses.
