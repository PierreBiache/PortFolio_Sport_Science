import streamlit as st
import pandas as pd

st.title("Player Search by Statistical Profile")
st.markdown("---") 

# --- DICTIONARIES FOR TRANSLATION ---

# Position mapping dictionary 
position_mapping = {
    'A': 'Striker',
    'MO': 'Attacking Midfielder',
    'MD': 'Defending Midfielder',
    'DL': 'Wing Defender',
    'DC': 'Central Defender',
    'G': 'Goalkeeper'
}

# Column translation dictionary (French to English)
column_translation = {
    'Joueur': 'Player',
    'Poste': 'Position',
    'Buts': 'Goals',
    'Tirs': 'Shots',
    'Duel G/P': 'Duels W/L',
    '%Passes': 'Pass Completion %',
    'Interceptions': 'Interceptions',
    'Tacles': 'Tackles',
    'Fautes': 'Fouls',
    'Ballons perdus': 'Turnovers'
}

# --- SECURE DATA LOADING LOGIC ---
try:
    csv_file_path = "Data/players.csv"
    
    # Load the raw data
    raw_data = pd.read_csv(csv_file_path, sep=';', decimal=',')
    
    # Translate column names to English immediately after loading
    raw_data.rename(columns=column_translation, inplace=True)
    
    # Fill missing values with 0
    full_data = raw_data.fillna(0)
    
    # Apply the mapping to create the full position name column
    full_data['Full_Position'] = full_data['Position'].map(position_mapping)
    
except FileNotFoundError:
    st.error(f"Error: File {csv_file_path} not found. Please check your 'Data' folder.")
    st.stop()

# --- 1. WIDGET SELECTION ---

# List of all possible positions
position_list = ['All positions'] + full_data['Full_Position'].unique().tolist()

# List of translated numerical statistics available for ranking
statistics_to_rank = ['Goals', 'Shots', 'Duels W/L', 'Pass Completion %', 'Interceptions', 'Tackles', 'Fouls', 'Turnovers']

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_position = st.selectbox(
        'Position:',
        position_list
    )

with filter_col2:
    selected_statistics = st.multiselect(
        'Statistics to include in the ranking (Max 3):',
        statistics_to_rank,
        default=statistics_to_rank[:2] 
    )

# --- 2. FILTERING AND RANKING LOGIC ---

ranking_df = full_data.copy() 

# Filter based on the selected position
if selected_position != 'All positions':
    ranking_df = ranking_df[ranking_df['Full_Position'] == selected_position]

if not selected_statistics:
    st.warning("Please select at least one statistic for ranking.")
    st.stop()
    
# Check that all chosen columns exist in the DataFrame
if all(stat in ranking_df.columns for stat in selected_statistics):

    # Create a DataFrame containing only player identification columns
    ranks_df = ranking_df[['Player', 'Club', 'Full_Position']].copy()
    
    # Loop over each selected statistic to calculate its rank
    for stat in selected_statistics:
        
        # Define ranking order: True if lower is better (Fouls, Turnovers)
        ascending_order = True if stat in ['Fouls', 'Turnovers'] else False
        
        # Calculate the rank (1 is the best performance)
        ranks_df[f'Rank_{stat}'] = ranking_df[stat].rank(
            method='average', 
            ascending=ascending_order 
        )

    # Isolate the rank columns to calculate the average
    rank_columns = [col for col in ranks_df.columns if col.startswith('Rank_')]
    ranks_df['Average_Rank'] = ranks_df[rank_columns].mean(axis=1)

    # Sort by Average Rank and isolate the top 5
    final_top5_df = ranks_df.sort_values(by='Average_Rank', ascending=True).head(5)
    
    display_columns = ['Player', 'Club', 'Full_Position', 'Average_Rank'] + rank_columns
    
    # Display the results
    st.header(f"Top 5 {selected_position} by Statistical Profile")
    st.info(f"Ranking based on average rank for: {', '.join(selected_statistics)}")
    
    st.dataframe(
        final_top5_df[display_columns]
        .reset_index(drop=True)
        .style.format({'Average_Rank': "{:.2f}"}), 
        use_container_width=True
    )

else:
    st.warning("Please choose valid statistics.")