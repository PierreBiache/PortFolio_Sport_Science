import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pierre Biache | Portfolio",
    page_icon="⚽",
    layout="wide"
)

st.title("Sport & Data Science Portfolio | Pierre Biache")

st.markdown("""
### Welcome to my Professional Portfolio
<div style="font-size: 1.2rem; line-height: 1.6;">
    I am a <strong>Sports Data Scientist</strong> specializing in performance analysis and athlete monitoring. 
    With a background in both sports science and data engineering, I bridge the gap between 
    raw data and technical or fitness coaching staffs.
    <br><br>
    This portfolio showcases my ability to process complex datasets (Tracking, GPS, Scouting) 
    into actionable insights using current sports science principles. 
    It is divided into multiple pages showcasing various projects completed during my internships and university studies.
</div>
""", unsafe_allow_html=True)

st.divider()

st.subheader("Project 1: Interactive Power BI Match Report")

st.markdown("""
<div style="font-size: 1.2rem; line-height: 1.6;">
    This report was designed for the performance department of the AC Sparta Academy. The fitness and technical staff needed a way to visualize the physical GPS performances of each player across different categories during games.
    <br><br>
    The main challenge was the data architecture. Every category had its own file, so we had to centralize everything into a single source. I built fact tables for the raw data and dimension tables to characterize it, adopting a star schema architecture. 
    <br><br>
    Finally, I designed the report to be accessible to players and coaches without a data background, while remaining analytical enough for the sports science staff. 
    <br><br>
    <em><strong>Note:</strong> For reasons of data privacy, an interactive but fully anonymized version of the Power BI report is displayed below, with player names and specific analyzed categories carefully redacted.</em>
</div>
""", unsafe_allow_html=True)

power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiMmY0NjdlZDItMWM1ZS00MzdkLWE4NmItMTA4ZTc1YzhjMzc5IiwidCI6Ijg5M2FiY2JhLTNiYzItNDY2ZC05ODBkLTEyNGVmNGFlYjBkNyIsImMiOjl9"

power_bi_iframe = f"""
<iframe title="Power BI Report" width="100%" height="600" src="{power_bi_url}" frameborder="0" allowFullScreen="true"></iframe>
"""

components.html(power_bi_iframe, height=600)

st.divider()

pdf_path = "Documents/MatchReport_PowerBi.pdf"

try:
    with open(pdf_path, "rb") as file:
        st.download_button(
            label="Download Full Power BI Report",
            data=file.read(),
            file_name="MatchReport_PowerBi.pdf",
            mime="application/pdf"
        )
except FileNotFoundError:
    st.error("PDF not found. Please check the Documents folder.")
