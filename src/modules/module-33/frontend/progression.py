import streamlit as st
import pandas as pd

def show_progression():
    st.subheader("📈 Disease Progression Timeline")

    data = pd.DataFrame({
        "Date": ["2026-01", "2026-02", "2026-03"],
        "Stage": [1, 2, 3]
    })

    st.line_chart(data.set_index("Date"))

    st.write("Progression Type: Linear")