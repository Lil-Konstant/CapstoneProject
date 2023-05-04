import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum


def main():

    st.set_page_config(page_title="Average Temperature Predictor")
    st.title('Average Temperature Predictor')
    st.sidebar.success("Select a page above.")

    selectableCountries = []
    selectedCountry = st.selectbox(
        'Please choose which country you want to predict temperatures for.',
        ('Australia', 'United States', 'United Kingdom', 'Germany'))

    if st.button('Select'):
        OnCountrySelection(selectedCountry)


def OnCountrySelection(selectedCountry):
    # For regression modelling, we need to calculate unique forecasters for each country being included in the software implementation
    # So we will choose Australia as an example country and demonstrate how the regression models will be built for country
    # This will be automated in the final implementation

    df = pd.read_csv('D:/UC/ST4483/Tutorials/Master-Project/CapstoneProject/GlobalLandTemperaturesByCountry.csv')
    selectedCountryDF = df[df["Country"] == selectedCountry]
    selectedCountryDF['dt'] = pd.to_datetime(selectedCountryDF['dt'], format='%Y/%m/%d')
    selectedCountryDF = selectedCountryDF.set_index('dt')
    selectedCountryDF = selectedCountryDF.drop(index=selectedCountryDF.index[0:selectedCountryDF.index.get_loc('1855-02-01')])
    selectedCountryDF = selectedCountryDF.rename(columns={'x': 'y'})
    selectedCountryDF = selectedCountryDF.asfreq('MS', fill_value=0)
    selectedCountryDF = selectedCountryDF.sort_index()

    # Plot the whole australian dataset, with training data in red and testing in blue
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
        title=f'{selectedCountry} Monthly Temperature (1750 - 2013)',
        hovermode="x")
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
    st.plotly_chart(fig)

    mostRecentDate = selectedCountryDF.index[-1]
    mostRecentTemp = selectedCountryDF['AverageTemperature'].iloc[-1]

    st.write(f'The average temperature for {selectedCountry} was most recently recorded as {mostRecentTemp}\u00B0C on {mostRecentDate}')


main()
