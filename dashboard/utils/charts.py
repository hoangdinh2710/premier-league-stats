"""
Reusable chart components for the dashboard.
"""
import plotly.graph_objects as go
import plotly.express as px


def draw_half_pitch():
    """
    Draw a half football pitch for shot maps.
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Pitch outline (half pitch)
    fig.add_shape(type="rect", x0=0.5, y0=0, x1=1, y1=1,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Penalty area
    fig.add_shape(type="rect", x0=0.83, y0=0.21, x1=1, y1=0.79,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # 6-yard box
    fig.add_shape(type="rect", x0=0.94, y0=0.37, x1=1, y1=0.63,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Goal
    fig.add_shape(type="rect", x0=1, y0=0.44, x1=1.02, y1=0.56,
                  line=dict(color="white", width=2), fillcolor="rgba(255,255,255,1)")
    
    # Penalty spot (approximate)
    fig.add_shape(type="circle", x0=0.885, y0=0.49, x1=0.895, y1=0.51,
                  line=dict(color="white", width=2), fillcolor="white")
    
    # Penalty arc
    fig.add_shape(type="path",
                  path="M 0.83 0.21 Q 0.75 0.5 0.83 0.79",
                  line=dict(color="white", width=2))
    
    fig.update_layout(
        plot_bgcolor="#2d8c3e",  # Football pitch green
        paper_bgcolor="#1e1e1e",
        xaxis=dict(range=[0.5, 1.05], showgrid=False, zeroline=False, 
                   showticklabels=False, fixedrange=True),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, 
                   showticklabels=False, fixedrange=True),
        height=600,
        width=700,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    return fig


def create_xg_scatter(df, x_col='xG', y_col='goals', hover_name='player', 
                      title='Goals vs xG', color_col=None):
    """
    Create a scatter plot comparing xG to actual performance.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis (xG)
        y_col: Column name for y-axis (actual)
        hover_name: Column to show on hover
        title: Chart title
        color_col: Optional column for color coding
    
    Returns:
        Plotly Figure object
    """
    fig = px.scatter(df, x=x_col, y=y_col, hover_name=hover_name,
                     color=color_col, title=title,
                     labels={x_col: 'Expected (xG)', y_col: 'Actual'})
    
    # Add diagonal line (y = x) showing "expected" performance
    max_val = max(df[x_col].max(), df[y_col].max())
    fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                  line=dict(color="gray", width=2, dash="dash"))
    
    fig.update_layout(
        height=500,
        hovermode='closest'
    )
    
    return fig


def create_league_table_comparison(actual_df, xg_df):
    """
    Create side-by-side league tables (actual vs xG).
    
    Args:
        actual_df: DataFrame with actual standings
        xg_df: DataFrame with xG-based standings
    
    Returns:
        Tuple of (actual_table, xg_table) as formatted DataFrames
    """
    # Add position columns
    actual_df['Pos'] = range(1, len(actual_df) + 1)
    xg_df['xG Pos'] = range(1, len(xg_df) + 1)
    
    # Create a mapping of team to xG position
    xg_positions = dict(zip(xg_df['team'], xg_df['xG Pos']))
    
    # Add xG position to actual table for comparison
    actual_df['xG Pos'] = actual_df['team'].map(xg_positions)
    actual_df['Diff'] = actual_df['Pos'] - actual_df['xG Pos']
    
    return actual_df, xg_df


def style_dataframe_with_performance(df, position_col='Pos', xg_position_col='xG Pos'):
    """
    Apply conditional formatting to a dataframe based on performance vs xG.
    
    Args:
        df: DataFrame to style
        position_col: Column with actual position
        xg_position_col: Column with xG-based position
    
    Returns:
        Styled DataFrame
    """
    def highlight_performance(row):
        if position_col in row and xg_position_col in row:
            diff = row[position_col] - row[xg_position_col]
            if diff < 0:  # Actual position better than xG (overperforming)
                return ['background-color: rgba(0, 255, 0, 0.2)'] * len(row)
            elif diff > 0:  # Actual position worse than xG (underperforming)
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
        return [''] * len(row)
    
    return df.style.apply(highlight_performance, axis=1)
