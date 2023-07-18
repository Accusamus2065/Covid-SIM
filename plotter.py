"""CSC111 Winter 2023 Course Project: Plotter

Instructions
===============================

This python module only contains the function for visual presentation.
This function is automatically triggered in main() function.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of instructors and TAs of
CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. :)

This file is Copyright (c) 2023 Marshal Guo, Yibin Cui, Zherui Zhang.
"""

import plotly.graph_objects as go
import pandas as pd


def plot_diagram(states_file: str, edges_file: str) -> None:
    """Plots a geographical diagram of the United States showing states and their connections.

    Args:
        states_file: A string representing the file path of the CSV file containing information about the states.
            The CSV file should contain columns for State, Latitude, and Longitude.
        edges_file: A string representing the file path of the CSV file containing information about the edges
            connecting the states. The CSV file should contain columns for start_state, start_lat, start_lon,
            end_state, end_lat, and end_lon.

    Preconditions:
        - The 'states_file' and 'edges_file' paths must point to valid CSV files.
        - The CSV file specified by 'states_file' must contain columns for 'State', 'Latitude', and 'Longitude'.
        - The CSV file specified by 'edges_file' must contain columns for 'start_state', 'start_lat', 'start_lon',
          'end_state', 'end_lat', and 'end_lon'.
    """
    df_states = pd.read_csv(states_file)
    df_states.head()

    df_state_paths = pd.read_csv(edges_file)
    df_state_paths.head()

    fig = go.Figure()

    for i in range(len(df_state_paths)):
        fig.add_trace(
            go.Scattergeo(
                locationmode='USA-states',
                text=df_state_paths['state2'] + ' - ' + df_state_paths['state1'],
                lon=[df_state_paths['start_lon'][i], df_state_paths['end_lon'][i]],
                lat=[df_state_paths['start_lat'][i], df_state_paths['end_lat'][i]],
                mode='lines+markers',
                marker=dict(size=5, color='red'),
                line=dict(width=1, color='red'),
            )
        )

    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        lon=df_states['Longitude'],
        lat=df_states['Latitude'],
        hoverinfo='text',
        text=df_states['State'],
        mode='markers',
        marker=dict(
            size=5,
            color='blue',
            line=dict(
                width=3,
                color='rgba(68, 68, 68, 0)'
            )
        )))

    fig.update_layout(
        title_text='COVID-19 Spread in the USA',
        showlegend=False,
        geo=dict(
            scope='north america',
            projection_type='azimuthal equal area',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        )
    )

    # Show the figure
    fig.show()
