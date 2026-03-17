import streamlit as st

def show_case_detail():
    st.subheader("🔍 Case Detail")

    st.write("Patient ID: 101")
    st.write("Disease: Diabetes")

    st.subheader("Stage History")
    st.table([
        ["Stage 1", "2026-01"],
        ["Stage 2", "2026-02"],
        ["Stage 3", "2026-03"]
    ])

    st.subheader("⚠️ Complications")
    st.table([
        ["Neuropathy", "Moderate"],
        ["Kidney Damage", "Severe"]
    ])