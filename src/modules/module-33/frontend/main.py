import streamlit as st
from dashboard import show_dashboard
from patient_list import show_patient_list
from progression import show_progression
from case_detail import show_case_detail
from sql_view import show_sql_view

def module33_app():
    st.title("🧬 Disease Progression Case Repository")

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Patients", "Progression", "Case Detail", "SQL & Triggers"]
    )

    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Patients":
        show_patient_list()
    elif menu == "Progression":
        show_progression()
    elif menu == "Case Detail":
        show_case_detail()
    elif menu == "SQL & Triggers":
        show_sql_view()