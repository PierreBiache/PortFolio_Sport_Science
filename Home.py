import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    page_title="Pierre Biache | Portfolio",
    page_icon="⚽",
    layout="wide"
)

st.title("Sport & Data Science Portfolio | Pierre Biache")

st.markdown("""
### Welcome to my Professional Portfolio
I am a **Sports Data Scientist** specializing in performance analysis and athlete monitoring. 
With a background in both sports science and data engineering, I bridge the gap between 
raw data and technical or fitness coaching staffs.

This portfolio showcases my ability to process complex datasets (Tracking, GPS, Scouting) 
into actionable insights using current sports science principles. 
It is divided into multiple pages showcasing various projects completed during my internships and university studies.
""")

st.divider()

st.subheader("Project 1: Interactive Power BI Match Report")
st.write("""
This report was designed for the performance department of the AC Sparta Academy. The fitness and technical staff needed a way to visualize the physical GPS performances of each player across different categories during games.

The main challenge was the data architecture. Every category had its own file, so we had to centralize everything into a single source. I built fact tables for the raw data and dimension tables to characterize it, adopting a star schema architecture. 

Finally, I designed the report to be accessible to players and coaches without a data background, while remaining analytical enough for the sports science staff.
""")

pdf_path = "Documents/MatchReport_PowerBi.pdf"

try:
    with open(pdf_path, "rb") as file:
        st.download_button(
            label="Download Full Power BI Report",
            data=file.read(),
            file_name="MatchReport_PowerBi.pdf",
            mime="application/pdf"
        )
    pdf_viewer(pdf_path)
except FileNotFoundError:
    st.error("PDF not found. Please check the Documents folder.")