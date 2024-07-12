import streamlit as st
from mplsoccer import PyPizza
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ######################
#Clear Cache
def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)

def make_radar(names, percentiles, slice_colors, text_colors, size):
   
    baker = PyPizza(
            params=names,                  # list of parameters
            straight_line_color="#000000",  # color for straight lines
            straight_line_lw=1,             # linewidth for straight lines
            last_circle_lw=1,               # linewidth of last circle
            other_circle_lw=1,              # linewidth for other circles
            other_circle_ls="-."            # linestyle for other circles
        )
    
    radar, ax = baker.make_pizza(
        percentiles,              # list of values
        figsize=(size, size),      # adjust figsize according to your need
        param_location=110,
        slice_colors=slice_colors,
        value_colors = text_colors,
        value_bck_colors=slice_colors,
        # where the parameters will be added
        kwargs_slices=dict(
            facecolor="cornflowerblue", edgecolor="#000000",
            zorder=2, linewidth=1
        ),                   # values to be used when plotting slices
        kwargs_params=dict(
            color="#000000", fontsize=5,
            # fontproperties=font_normal.prop, va="center"
        ),                   # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=5,
            # fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
         )                    # values to be used when adding parameter-values
        ) 

    return radar

def make_bar_plot (data):

    df = pd.DataFrame(data)

    # Create the bar plot
    fig = plt.figure()

    #VERTICAL
    barplot = sns.barplot(x='Value', y='Attribute', data=df, palette='coolwarm', width=0.8)  # Create the plot (barplot)

    #HORIZONTAL
    # barplot = sns.barplot(y='Value', x='Attribute', data=df, palette='coolwarm', width=0.8)  # Create the plot (barplot)

    # Customize the plot
    plt.title('')  # Add a title
    plt.xlabel('')  # Label for the x-axis
    plt.ylabel('')  # Label for the y-axis
    plt.xlim(0, 100)  # Set the limit for the x-axis values to make comparisons easier
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    # # Annotate each bar with its value HORIZONTAL
    # for p in barplot.patches:
    #     barplot.annotate(format(p.get_height(), '.1f'), 
    #                     (p.get_x() + p.get_width() / 2., p.get_height()), 
    #                     ha = 'center', va = 'center', 
    #                     xytext = (0, 9), 
    #                     textcoords = 'offset points')
    
    # Annotate each horizontal bar with its value VERTICAL
    for p in barplot.patches:
        barplot.annotate(format(p.get_width(), '.1f'),  # Use bar's width for value
                     (p.get_width(), p.get_y() + p.get_height() / 2.),  # Position at the end of the bar
                     ha = 'left',  # Horizontal alignment is now 'left' to place text to the right of the bar
                     va = 'center',  # Vertical alignment remains 'center'
                     xytext = (9, 0),  # Offset text to the right of the bar
                     textcoords = 'offset points')

    # Show plot
    plt.tight_layout()  # Adjust layout to not cut off labels
    
    return fig
