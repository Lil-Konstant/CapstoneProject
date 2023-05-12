# ST1 Capstone Project - GUI Implementation (Streamlit)
# Author: Ronan Richardson - u3248669
# Date Created: 21/04/2023
# Date Last Edited: 12/05/2023

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from skforecast.utils import load_forecaster

# All the valid datasets the user can choose from and predict for
SELECTABLE_COUNTRIES = ('Australia', 'United States', 'United Kingdom', 'Germany', 'Austria', 'Belgium', 'Brazil', 'Canada', 'Denmark', 'Sweden', 'France', 'Spain', 'China', 'Russia')
SELECTABLE_COUNTRIES = sorted(SELECTABLE_COUNTRIES)

class ForecasterGUI:
    """ The ForecasterGUI class is used to create a simple Streamlit page that allows for user input from 3 different
    selection boxes. The class manages loading and displaying the selected country's average monthly temperature predictions
    from cached forecasters.
    """

    def __init__(self):
        """ The constructor for ForecasterGUI sets up a simple streamlit page with three selection boxes for taking
        the users input of country, month and year, as well as a predict button that is used to trigger the
        OnPredictionSelect method for prediction calculations.
        """

        # Get the file path of this script so this project can run on different devices
        self.__absolute_path = os.path.dirname(__file__)
        # Read in the temperature dataset and store it in the df field
        self.__df = pd.read_csv(f'{self.__absolute_path}\Datasets\GlobalLandTemperaturesByCountry.csv')

        # Set the page and tab title
        st.set_page_config(page_title="Average Temperature Predictor")
        st.title('Average Temperature Predictor')

        # Create the country selection box from the tuple of SELECTABLE_COUNTRIES
        self.__countrySelection = st.selectbox('Please choose the country and month + year you want to predict temperatures for.', SELECTABLE_COUNTRIES, key=5)

        # Create the month and year selection boxes + the prediction button (bound to OnPredictionSelect)
        self.__months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        self.__monthSelection = st.selectbox('Month', self.__months, key=2)
        self.__yearSelection = st.selectbox('Year', range(2023, 2100), key=1)
        self.__predictButton = st.button('Predict', key=4, on_click=self.__OnPredictionSelect)

    def __OnPredictionSelect(self):
        """ OnPredictionSelect is called when the Predict button is pressed, and will first get the subset country data
        based on the country selected by the user, and makes sure all the dates are formatted correctly and ordered by
        index. The function will then graph all the previous data for the user, before loading the appropriate country's
        forecaster for the Forecasters folder (the naming convention is CountryName_forecaster.py). The function then
        uses the pre-trained forecaster to predict as far along in years and months as the user has selected, and finishes
        by displaying the average monthly temperature prediction back to the user on the page.
        """

        # Get the user selected country and format + cache that country's temperature data
        selectedCountryDF = self.__df[self.__df["Country"] == self.__countrySelection]
        selectedCountryDF['dt'] = pd.to_datetime(selectedCountryDF['dt'], format='%Y/%m/%d')
        selectedCountryDF = selectedCountryDF.set_index('dt')
        selectedCountryDF = selectedCountryDF.rename(columns={'x': 'y'})
        selectedCountryDF = selectedCountryDF.asfreq('MS')
        selectedCountryDF = selectedCountryDF.sort_index()

        # Get the earliest and latest years in the selected country subset to display to the user
        earliestYear = selectedCountryDF.iloc[0].name.year
        latestYear = selectedCountryDF.iloc[-1].name.year

        # Plot the whole country's dataset, with training data in red and testing in blue
        fig = go.Figure([
            go.Scatter(
                x=selectedCountryDF.index,
                y=selectedCountryDF['AverageTemperature'],
                mode='lines',
                marker=dict(color='red', size=2),
                showlegend=False
            ),
        ])
        fig.update_layout(
            yaxis_title="Average National Temperature (\u00B0C)",
            title=f'{self.__countrySelection} Monthly Temperature ({earliestYear} - {latestYear})',
            hovermode="x")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        st.plotly_chart(fig)
        selectedCountryDF = selectedCountryDF.asfreq('MS', fill_value=0)

        # Get the most recent date and temperature recording from this country's data set, and display it to the user
        mostRecentDate = selectedCountryDF.index[-1]
        mostRecentTemp = selectedCountryDF['AverageTemperature'].iloc[-1]
        st.write(f'The average monthly temperature for {self.__countrySelection} was most recently recorded as {mostRecentTemp:.2f} \u00B0C on {mostRecentDate.month}/{mostRecentDate.year}')

        # Load this country's forecaster, and use it to predict that far along the data set (calculated in trainOffset)
        forecaster = load_forecaster(f'{self.__absolute_path}\Forecasters\{self.__countrySelection}_forecaster.py')
        chosenYear = int(self.__yearSelection)
        chosenMonthNum = self.__months.index(self.__monthSelection) + 1
        trainOffset = selectedCountryDF.index[-1].year - forecaster.training_range[-1].year - 1
        steps = ((trainOffset + (chosenYear - selectedCountryDF.index[-1].year)) * 12) + chosenMonthNum
        predictions = forecaster.predict(steps)
        # Display the last prediction to the user, which will be their chosen month and year
        st.markdown(f":green[{self.__countrySelection}'s predicted average temperature for the month of {self.__monthSelection} in {chosenYear} is {predictions.iloc[-1]:.2f} \u00B0C.]")


if __name__ == '__main__':
    forecasterGUI = ForecasterGUI()
