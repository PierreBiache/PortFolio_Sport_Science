import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.title(" College Basketball Computer Vision Tracking Data Analysis")

st.markdown("""
**Project Description:** This analysis was conducted during my internship at Stats Perform. The goal was to gain firsthand experience with computer vision tracking data, which is rapidly developing across multiple sports and becoming more precise than traditional GPS data. Using historical game data from Indiana University (USA), I aimed to create meaningful analyses and visualizations to make this initial experience highly rewarding. 

I developed a dashboard to observe key tracking metrics, such as distance covered, movement speed, and the percentage of time each player spent in different speed zones per game. Additionally, a spatial chart visualizes the specific locations of different run types on the court, highlighting how often a player hits maximum speed, particularly during fast breaks.
""")

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

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    selected_name = st.selectbox("Select Player", ["ALL"] + sorted(df_metrics['NAME'].dropna().unique()))

with filter_col2:
    selected_game = st.selectbox("Select Game ID", ["ALL"] + sorted(df_metrics['GAME'].astype(str).unique()))

with filter_col3:
    status_map = {"Global": 0, "Offense": 1, "Defense": 2}
    selected_status_label = st.selectbox("Select Phase", list(status_map.keys()))
    selected_status = status_map[selected_status_label]

filtered_df = df_metrics.copy()

if selected_name != "ALL":
    filtered_df = filtered_df[filtered_df['NAME'] == selected_name]
    
if selected_game != "ALL":
    filtered_df = filtered_df[filtered_df['GAME'].astype(str) == str(selected_game)]
    
filtered_df = filtered_df[filtered_df['OFF_DEF_STATUS'] == selected_status]

if filtered_df.empty:
    st.warning("No data found for the selected filters.")
else:
    st.dataframe(filtered_df, use_container_width=True)
    
    if selected_name != "ALL":
        st.subheader(f"Time Intensity Distribution: {selected_name}")
        metrics_cols = ['WALK_TIME%', 'JOG_TIME%', 'RUN_TIME%', 'SPRINT_TIME%', 'MAXSPEED_TIME%']
        st.bar_chart(filtered_df[metrics_cols].T)

st.markdown("---")
st.subheader("Sample Spatial Movement Map")
st.write("Displaying raw tracking trajectory for Player ID: 1076247 during Game: 2175533.")

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
            title=f"Court Movement Map - Player ID: {target_player_id} (Game: {target_game_id})",
            opacity=0.6,
        )
        
        fig.update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1),
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            legend_title_text='Intensity Zone'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sample tracking data not found. Please ensure TRACKING_2175533.csv is present in the Data folder.")