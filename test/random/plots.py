import streamlit as st
import plotly.graph_objects as go
import numpy as np

def scatterplot_with_trendline(df, x_column, y_column, title):
    # Create a scatter plot with Plotly
    fig = go.Figure()

    # Scatter plot for the data points with hover info for player name, salary, and projection
    fig.add_trace(go.Scatter(
        x=df[x_column], 
        y=df[y_column], 
        mode='markers', 
        name='Data points',
        marker=dict(color='blue'),
        hovertemplate = (
            "Player: %{text}<br>" +  # Player name
            "Salary: %{y}$<br>" +    # Salary (y-axis)
            "Projection: %{x}<extra></extra>"  # Projection (x-axis)
        ),
        text=df['Name']  # Use the player name for hover text
    ))

    # Fit a 3rd-degree polynomial
    z = np.polyfit(df[x_column], df[y_column], 3)
    p = np.poly1d(z)

    # Create a smooth range of x values to plot a smoother line
    x_smooth = np.linspace(df[x_column].min(), df[x_column].max(), 500)
    
    # Plot the polynomial trendline
    fig.add_trace(go.Scatter(
        x=x_smooth, 
        y=p(x_smooth),  # Evaluate polynomial on the smooth x values
        mode='lines', 
        name='3rd-degree polynomial trendline',
        line=dict(color='red')
    ))

    # Adjust layout: Compress horizontally, remove legend, reduce top margin
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        height=670,   # Increase height for vertical stretch
        width=1100,   # Slightly increase width of the plot
        showlegend=False,  # Remove the legend
        margin=dict(t=10)  # Reduce top margin to close the gap between chart and tabs
    )

    # Use Streamlit columns to center the plot
    col1, col2, col3 = st.columns([1, 6, 1])  # Adjust ratios for centering
    with col2:
        st.plotly_chart(fig)

