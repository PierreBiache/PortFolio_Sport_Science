import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.title("College Basketball Computer Vision Tracking Data Analysis")

st.markdown("""
<div style="font-size: 1.2rem; line-height: 1.6;">
    <strong>Project Description:</strong> This analysis was conducted during my internship at Stats Perform. 
    The goal was to gain firsthand experience with computer vision tracking data, which is rapidly developing 
    across multiple sports and becoming more precise than traditional GPS data. Using historical game data 
    from Indiana University (USA), I aimed to create meaningful analyses and visualizations to make this 
    initial experience highly rewarding. 
    <br><br>
    I developed a dashboard to observe key tracking metrics, such as distance covered, movement speed, 
    and the percentage of time each player spent in different speed zones per game. Additionally, a spatial 
    chart visualizes the specific locations of different run types on the court, highlighting how often a 
    player hits maximum speed, particularly during fast breaks.
</div>
""", unsafe_allow_html=True)

st.divider()

@st.cache_data
def load_production_data():
    metrics_path = "Data/basketball_metrics_ready.csv"
    box_score_path = "Data/Box_Score_Stats.csv"
    
    try:
        df = pd.read_csv(metrics_path)
        box_score = pd.read_csv(box_score_path, sep=None, engine='python')
        
        col_names = ['PLAYER_ID', 'MONIKER', 'LAST_NAME']
        player_names = box_score[col_names].drop_duplicates(subset='PLAYER_ID')
        player_names['FULL_NAME'] = player_names['MONIKER'].fillna('') + ' ' + player_names['LAST_NAME'].fillna('')
        
        return df, player_names
    except FileNotFoundError:
        st.error("Production data not found. Please ensure the ETL process was completed.")
        st.stop()

df_metrics, player_names_df = load_production_data()

if 'NAME' not in df_metrics.columns:
    df_metrics['NAME'] = df_metrics['PLAYER_ID'].map(player_names_df.set_index('PLAYER_ID')['FULL_NAME'])

@st.cache_data
def load_thresholds():
    return pd.read_csv("Data/Optical_Game_Load_Zone_Stats.csv", sep=None, engine='python')

@st.cache_data
def get_player_trajectory(game_id, player_id):
    tracking_path = f"Data/TRACKING_{game_id}.csv.gz"
    
    if not os.path.exists(tracking_path):
        return None
        
    tracking_df = pd.read_csv(tracking_path, compression="gzip")
    thresholds = load_thresholds()
    
    columns = ['PLAYER_ID', 'X_POSITION', 'Y_POSITION', 'TIME']
    if not all(c in tracking_df.columns for c in columns):
        return None
        
    p_df = tracking_df[tracking_df['PLAYER_ID'] == int(player_id)][columns].copy().reset_index(drop=True)
    if p_df.empty:
        return None

    p_df['GAP'] = p_df['TIME'].diff().fillna(0) * 0.001
    p_df['PHASE'] = (p_df['GAP'] > 0.04).cumsum() + 1
    same_phase = p_df['PHASE'] == p_df['PHASE'].shift(-1)
    
    dx = p_df['X_POSITION'].shift(-1) - p_df['X_POSITION']
    dy = p_df['Y_POSITION'].shift(-1) - p_df['Y_POSITION']
    segment = np.where(same_phase, np.sqrt(dx**2 + dy**2), 0)
    p_df['SEGMENT'] = segment * 0.000189394 

    p_df['SPEED'] = np.where(p_df['GAP'] == 0, 0, p_df['SEGMENT'] / p_df['GAP']) * 3600
    p_df['PACK'] = p_df.index // 25
    speed_by_pack = p_df.groupby('PACK')['SPEED'].mean()
    p_df['SPEED_PACK'] = p_df['PACK'].map(speed_by_pack)

    player_th = thresholds[(thresholds['GAME_CODE'] == int(game_id)) & (thresholds['PLAYER_ID'] == int(player_id))]
    
    try:
        bins = [
            0, 
            player_th[player_th['ANAEROBIC_LEVEL_ID'] == 1]['MAX_SPEED'].iloc[0],
            player_th[player_th['ANAEROBIC_LEVEL_ID'] == 2]['MAX_SPEED'].iloc[0],
            player_th[player_th['ANAEROBIC_LEVEL_ID'] == 3]['MAX_SPEED'].iloc[0],
            player_th[player_th['ANAEROBIC_LEVEL_ID'] == 4]['MAX_SPEED'].iloc[0],
            np.inf
        ]
    except (IndexError, KeyError):
        return None

    labels = ['Walk', 'Jog', 'Run', 'Sprint', 'Max Speed']
    p_df['ZONE'] = pd.cut(p_df['SPEED_PACK'], bins=bins, labels=labels, right=False)

    return p_df

st.header("Tracking Data Performance Dashboard")

# --- FILTERS ---
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    selected_name = st.selectbox("Select Player", ["ALL"] + sorted(df_metrics['NAME'].dropna().unique()))

with filter_col2:
    # Update available games based on player selection
    if selected_name != "ALL":
        available_games = sorted(df_metrics[df_metrics['NAME'] == selected_name]['GAME'].astype(str).unique())
    else:
        available_games = sorted(df_metrics['GAME'].astype(str).unique())
        
    selected_game = st.selectbox("Select Game ID", ["ALL"] + available_games)

with filter_col3:
    status_map = {"Global": 0, "Offense": 1, "Defense": 2}
    selected_status_label = st.selectbox("Select Phase", list(status_map.keys()))
    selected_status = status_map[selected_status_label]

# --- DATA FILTERING ---
filtered_df = df_metrics.copy()

if selected_name != "ALL":
    filtered_df = filtered_df[filtered_df['NAME'] == selected_name]
    
if selected_game != "ALL":
    filtered_df = filtered_df[filtered_df['GAME'].astype(str) == str(selected_game)]
    
filtered_df = filtered_df[filtered_df['OFF_DEF_STATUS'] == selected_status]

if filtered_df.empty:
    st.warning("No data found for the selected filters.")
else:
    # --- TABLE FORMATTING ---
    display_df = filtered_df.copy()
    
    # 1. Force NAME to be the first column
    cols = ['NAME'] + [col for col in display_df.columns if col != 'NAME']
    display_df = display_df[cols]
    
    # 2. Rename TOTAL_DISTANCE to include units
    if 'TOTAL_DISTANCE' in display_df.columns:
        display_df.rename(columns={'TOTAL_DISTANCE': 'TOTAL_DISTANCE (Miles)'}, inplace=True)
        
    # 3. Format percentage columns (assuming they contain '%' in their name and are decimals like 0.15)
    pct_cols = [col for col in display_df.columns if '%' in col]
    format_dict = {col: "{:.1%}" for col in pct_cols}
    
    # Display styled dataframe
    st.dataframe(display_df.style.format(format_dict), use_container_width=True)
    
    # --- BAR CHART (FIRST GAME ONLY) ---
    if selected_name != "ALL":
        # Get the first game of the filtered list
        first_game = sorted(filtered_df['GAME'].unique())[0]
        bar_data = filtered_df[filtered_df['GAME'] == first_game]
        
        st.subheader(f"Time Intensity Distribution: {selected_name}")
        st.write(f"*Displaying data for the first available game (ID: {first_game})*")
        
        metrics_cols = ['WALK_TIME%', 'JOG_TIME%', 'RUN_TIME%', 'SPRINT_TIME%', 'MAXSPEED_TIME%']
        # Extract only the percentage columns for the bar chart
        if not bar_data.empty:
            st.bar_chart(bar_data[metrics_cols].T)

st.markdown("---")
st.subheader("Spatial Movement Map")

st.markdown("""
<div style="font-size: 1.2rem; line-height: 1.6; margin-bottom: 20px;">
    Displaying a raw tracking trajectory example for one specific player during a single game. 
    <br><br>
    <em><strong>Note:</strong> The decision was made to showcase only a single representative example. 
    Importing and processing the raw optical tracking dataset (which records spatial coordinates 
    at 25 frames per second) for every single game dynamically would require significant computational 
    power and drastically slow down the application's loading time.</em>
</div>
""", unsafe_allow_html=True)

target_game_id = "2175533"
target_player_id = 1076247

with st.spinner('Loading raw tracking data and generating spatial map...'):
    trajectory_df = get_player_trajectory(target_game_id, target_player_id)
    
    if trajectory_df is not None and not trajectory_df.empty:
        intensity_colors = {
            'Walk': '#1f77b4',
            'Jog': '#2ca02c',
            'Run': '#ff7f0e',
            'Sprint': '#d62728',
            'Max Speed': '#9467bd'
        }
        
        fig = px.scatter(
            trajectory_df,
            x='X_POSITION',
            y='Y_POSITION',
            color='ZONE',
            color_discrete_map=intensity_colors,
            title=f"Sample Court Movement Map - Single Player Example (Game ID: {target_game_id})",
            opacity=0.6,
        )
        
        fig.update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1),
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            legend=dict(
                title_text='Intensity Zone',
                font=dict(size=16)  # Legend text size increased
            ),
            title=dict(font=dict(size=20))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sample tracking data not found. Please ensure TRACKING_2175533.csv is present in the Data folder.")
