import streamlit as st

def show_sql_view():
    st.subheader("🧠 SQL Queries")

    st.code("""
    SELECT patient_id, COUNT(stage) as progression_steps
    FROM disease_progression
    GROUP BY patient_id;
    """, language="sql")

    st.subheader("⚙️ Trigger Example")

    st.code("""
    CREATE TRIGGER update_stage
    AFTER INSERT ON progression
    FOR EACH ROW
    BEGIN
        UPDATE patients
        SET current_stage = NEW.stage
        WHERE id = NEW.patient_id;
    END;
    """, language="sql")