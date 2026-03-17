import streamlit as st

def show_dashboard():
    st.subheader("📊 Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Patients", 120)
    col2.metric("Active Cases", 85)
    col3.metric("Complications", 34)

    st.subheader("📈 Progression Trend")

    st.line_chart({
        "Stage 1": [10, 20, 30],
        "Stage 2": [5, 15, 25],
        "Stage 3": [2, 10, 18]
    })