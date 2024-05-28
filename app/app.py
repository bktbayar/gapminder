import streamlit as st
import pandas as pd
import plotly.express as px

# Function to convert strings like '400k', '3.28M', and '1.2B' to floats
def convert_to_float(value):
    if isinstance(value, str):
        value = value.lower().replace(',', '').replace(' ', '')  # Clean up the string
        if 'k' in value:
            return float(value.replace('k', '')) * 1e3
        elif 'm' in value:
            return float(value.replace('m', '')) * 1e6
        elif 'b' in value:
            return float(value.replace('b', '')) * 1e9
    try:
        return float(value)
    except ValueError:
        return None

# Load and preprocess data
@st.cache_data
def load_and_preprocess_data():
    # Load data
    population_df = pd.read_csv('population.csv')
    life_expectancy_df = pd.read_csv('life_expectancy.csv')
    gni_df = pd.read_csv('gni.csv')

    # Forward fill missing values
    population_df.ffill(inplace=True)
    life_expectancy_df.ffill(inplace=True)
    gni_df.ffill(inplace=True)

    # Transform to tidy format
    population_df = population_df.melt(id_vars=['country'], var_name='year', value_name='population')
    life_expectancy_df = life_expectancy_df.melt(id_vars=['country'], var_name='year', value_name='life_expectancy')
    gni_df = gni_df.melt(id_vars=['country'], var_name='year', value_name='gni_per_capita')

    # Convert columns to float
    population_df['population'] = population_df['population'].apply(convert_to_float)
    life_expectancy_df['life_expectancy'] = life_expectancy_df['life_expectancy'].apply(convert_to_float)
    gni_df['gni_per_capita'] = gni_df['gni_per_capita'].apply(convert_to_float)

    # Ensure the columns are in the correct type
    population_df['year'] = population_df['year'].astype(int)
    population_df['population'] = population_df['population'].astype(float)
    life_expectancy_df['year'] = life_expectancy_df['year'].astype(int)
    life_expectancy_df['life_expectancy'] = life_expectancy_df['life_expectancy'].astype(float)
    gni_df['year'] = gni_df['year'].astype(int)
    gni_df['gni_per_capita'] = gni_df['gni_per_capita'].astype(float)

    # Merge dataframes
    merged_df = population_df.merge(life_expectancy_df, on=['country', 'year'])
    merged_df = merged_df.merge(gni_df, on=['country', 'year'])

    return merged_df

data = load_and_preprocess_data()

st.title('Gapminder')

# Interactive widgets
year = st.slider('Year', min_value=int(data['year'].min()), max_value=int(data['year'].max()), value=int(data['year'].min()))
selected_countries = st.multiselect('Countries', options=data['country'].unique(), default=data['country'].unique())

# Filter data based on widgets
filtered_data = data[(data['year'] == year) & (data['country'].isin(selected_countries))]

# Display the bubble chart
fig = px.scatter(filtered_data, x='gni_per_capita', y='life_expectancy',
                 size='population', color='country', hover_name='country',
                 log_x=True, size_max=60)

# Ensure consistent axis ranges
fig.update_layout(xaxis_range=[1, data['gni_per_capita'].max()],
                  yaxis_range=[data['life_expectancy'].min(), data['life_expectancy'].max()])

st.plotly_chart(fig)
