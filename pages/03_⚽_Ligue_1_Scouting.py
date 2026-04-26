import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

st.title("LIGUE 1 SCOUTING REPORT")

st.markdown("""
**Project Description:** The following two pages showcase an independent, self-driven project. My primary objective was to gain hands-on experience with Streamlit, a powerful Python framework that enables the rapid development of highly readable and accessible data visualization applications. It bridges the gap between complex backend analysis (such as machine learning) and user-friendly interfaces.

Before having access to proprietary club data, I leveraged publicly available datasets to build a functional scouting tool. This first page allows scouts to select a specific player and benchmark their performance against the league average. The second page operates in reverse: it enables scouts to filter by specific metrics and positions to identify the top 5 matching profiles, allowing them to search for a specific skill set rather than just a known name.
""")

st.sidebar.header("Player Selection")

position_mapping = {
    'A': 'Striker',
    'MO': 'Attacking Midfielder',
    'MD': 'Defending Midfielder',
    'DL': 'Wing Defender',
    'DC': 'Center Defender',
    'G': 'Goalkeeper'
}

column_translation = {
    'Joueur': 'Player',
    'Poste': 'Position',
    'Club': 'Club',
    '%Titu': 'Start %',
    'Buts': 'Goals',
    'Tirs': 'Shots',
    'Tirs cadrés': 'Shots on Target',
    'Duel G/P': 'Duels W/L',
    '%Passes': 'Pass Completion %',
    'Interceptions': 'Interceptions',
    'Tacles': 'Tackles',
    'Fautes': 'Fouls',
    'Ballons perdus': 'Turnovers'
}

raw_data = pd.read_csv("Data/players.csv", sep=';', decimal=',')
raw_data.rename(columns=column_translation, inplace=True)

full_data = raw_data.fillna(0)
full_data['Full_Position'] = full_data['Position'].map(position_mapping)

player_list = full_data["Player"].unique()

selected_player = st.sidebar.selectbox('Select a Player to Analyze:', player_list)

player_stats_row = full_data[full_data['Player'] == selected_player]

player_name = player_stats_row['Player'].iloc[0]
full_pos = player_stats_row['Full_Position'].iloc[0]
club = player_stats_row['Club'].iloc[0]
starts_pct = player_stats_row['Start %'].iloc[0]

age = 25
nationality = "..."
height = 1.80
weight = 75

st.header(f"Player Profile: {selected_player}")

col_metrics, col_photo = st.columns([4, 1])

with col_metrics:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="FAVORED FOOT", value="Right")
    with c2:
        st.metric(label="POSITION", value=full_pos)
    with c3:
        st.metric(label="CURRENT CLUB", value=club)
    with c4:
        st.metric(label="START %", value=starts_pct)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric(label="AGE", value=f"{age} yrs")
    with c6:
        st.metric(label="NATIONALITY", value=nationality)
    with c7:
        st.metric(label="HEIGHT", value=f"{height}m")
    with c8:
        st.metric(label="WEIGHT", value=f"{weight}kg")

with col_photo:
    st.markdown(" ")
    st.markdown(
        """
        <style>
        .photo-placeholder {
            background-color: #1a1a1a;
            width: 100%;
            height: 200px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.2em;
        }
        </style>
        <div class="photo-placeholder">
            Player Photo
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")
st.subheader("Physical & Locomotor Data")

c9, c10, c11, c12 = st.columns([1, 1, 1, 1])
with c9:
    st.metric(label="Distance Covered", value="6km")
with c10:
    st.metric(label="Max Speed", value="32km/h")
with c11:
    st.metric(label="No. Sprints", value="12")
with c12:
    st.metric(label="Vertical Jump", value="2m93")

st.markdown("---")

radar_cols = ['Goals', 'Shots', 'Shots on Target', 'Duels W/L', 'Pass Completion %', 'Interceptions', 'Tackles', 'Fouls', 'Turnovers']
normalized_data = full_data.copy()

raw_avg_values = full_data[radar_cols].mean()
player_raw_values = player_stats_row[radar_cols].iloc[0]

raw_comparison_df = pd.DataFrame({
    f'{selected_player}': player_raw_values,
    'League Average': raw_avg_values
})

scaler = MinMaxScaler(feature_range=(0, 100))
normalized_data[radar_cols] = scaler.fit_transform(normalized_data[radar_cols])

avg_data_radar = normalized_data[radar_cols].mean().to_frame().T
avg_data_radar['Player'] = 'League Average'

player_stats_normalized = normalized_data[normalized_data['Player'] == selected_player]
player_data_radar = player_stats_normalized[radar_cols].copy()
player_data_radar['Player'] = selected_player

comparison_df = pd.concat([player_data_radar, avg_data_radar])

radar_df = pd.melt(
    comparison_df,
    id_vars=['Player'],
    value_vars=radar_cols,
    var_name='Statistic',
    value_name='Value'
)

raw_long_df = pd.melt(
    raw_comparison_df.T.reset_index().rename(columns={'index': 'Player'}),
    id_vars=['Player'],
    value_vars=radar_cols,
    var_name='Statistic',
    value_name='Raw_Value'
)

radar_df = radar_df.merge(raw_long_df, on=['Player', 'Statistic'])

player_df = radar_df[radar_df['Player'] == selected_player]
average_df = radar_df[radar_df['Player'] == 'League Average']

player_texts = player_df['Raw_Value'].round(2).astype(str).tolist()
average_texts = average_df['Raw_Value'].round(2).astype(str).tolist()

st.subheader("Performance vs Ligue 1 Average")

if not radar_df.empty:
    fig = px.line_polar(
        radar_df,
        r='Value',
        theta='Statistic',
        color='Player',
        line_close=True,
        range_r=[0, 100],
        height=700,
        width=900,
    )

    fig.update_traces(
        fill='toself',
        textposition='middle right',
        mode='lines+markers',
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}<br>Raw Value: %{text}<extra></extra>',
    )

    fig.update_traces(
        selector=dict(name=selected_player),
        text=player_texts,
        mode='lines+markers+text',
        textfont=dict(color='Blue', size=20)
    )

    fig.update_traces(
        selector=dict(name='League Average'),
        text=average_texts,
        mode='lines+markers+text',
        textfont=dict(color='Black', size=20)
    )

    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                tickfont=dict(size=20)
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)