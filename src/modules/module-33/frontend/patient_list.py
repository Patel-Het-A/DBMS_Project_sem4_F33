import streamlit as st
import pandas as pd

def show_patient_list():
    st.subheader("👤 Patient Cases")

    data = pd.DataFrame({
        "Patient ID": [101, 102, 103],
        "Disease": ["Diabetes", "CKD", "COPD"],
        "Current Stage": ["Stage 2", "Stage 3", "Stage 1"],
        "Last Update": ["2026-03-10", "2026-03-12", "2026-03-15"]
    })

    st.dataframe(data)