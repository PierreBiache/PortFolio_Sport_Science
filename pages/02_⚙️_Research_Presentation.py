import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

st.title(" Biomechanics & Ergonomics Research Master Project: Low-Tech Working Bed")

st.markdown("""
<div style="font-size: 1.2rem; line-height: 1.6;">
    <strong>Project Description:</strong> This research project focuses on agricultural ergonomics to prevent Musculoskeletal Disorders (MSDs), which affect a vast majority of farmers. I analyzed the "Working Bed," a low-tech innovation designed to reduce severe lower back strain during ground-level farming tasks. 
    <br><br>
    The primary objective was to determine the optimal seat adjustment based on the knee joint's torque-angle relationship to maximize force production capacity. By measuring muscle activity (EMG), task performance time, and perceived discomfort during a simulated harvesting task, this study highlights how biomechanical analysis and low-tech design can be combined to improve occupational health and daily efficiency.
</div>
""", unsafe_allow_html=True)

st.divider()

pdf_path = "Documents/Master_Oral_Presentation.pdf"

try:
    with open(pdf_path, "rb") as file:
        pdf_data = file.read()
        
    st.download_button(
        label="📄 Download Full Research Report",
        data=pdf_data,
        file_name="Pierre_Biache_Working_Bed_Research.pdf",
        mime="application/pdf"
    )
    
    st.divider()
    
    pdf_viewer(pdf_path)

except FileNotFoundError:
    st.error("Research PDF not found in the Documents folder.")
