import streamlit as st

st.title("Work In Progress / Coming Soon")

st.markdown("""
<div style="font-size: 1.2rem; line-height: 1.6; margin-bottom: 2rem;">
    This section highlights the personal projects and technical challenges I am currently working on. 
    These tools are in active development and will be fully integrated into this portfolio upon completion.
</div>
""", unsafe_allow_html=True)

st.divider()

st.subheader("1: Power BI Training Report")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    **Objective:** Similar to the Match Report, the goal is to provide technical coaches with clear insights into their training sessions. This allows them to adapt each session to match the club's planned physical load for every individual player.
    
    **Current Focus:**
    * Structuring historical data into an optimized schema and format.
    * Designing a highly intuitive, beginner-friendly interface.
    * Developing a "Drill Builder" tool using machine learning to recommend or create new drills based on historical physical data.
    """)

with col2:
    st.info("**Status:** Development (80%)")
    st.write("**Tech Stack:**")
    st.write("• Power BI")
    st.write("• Streamlit")
    st.write("• Excel")

st.divider()

st.subheader("2: Research Project: Influence of Biological Age on Football Physical Test Performances (CMJ, 505, Sprint)")

col3, col4 = st.columns([3, 1])

with col3:
    st.markdown("""
    **Objective:** A primary goal of any elite football academy is talent identification. While physical tests help detect above-average players, chronological age in youth sports often misrepresents biological development. This discrepancy can lead to massive performance gaps between early and late bloomers. This study aims to normalize physical performances by predicting a player's baseline capacity at 16 years old, accounting for their specific biological (skeletal) age.
    
    **Current Focus:**
    * Testing and validating the Linear Mixed Model (LMM).
    * Processing test results to generate age-predicted performance curves for every player.
    * Translating these statistical results into actionable insights for the club's coaching and scouting staff.
    """)

with col4:
    st.warning("**Status:** Statistical Modeling (75%)")
    st.write("**Tech Stack:**")
    st.write("• RStudio")
    st.write("• Excel")
    st.write("• VALD Testing Devices")
