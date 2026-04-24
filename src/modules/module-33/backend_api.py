from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
import mysql.connector

app = FastAPI(title="Module 33 Disease Progression API")


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="parulruchika",
        database="DiseaseProgressionDB"
    )


class PatientIn(BaseModel):
    full_name: str
    dob: date
    gender: str
    contact_info: Optional[str] = None


class DiseaseIn(BaseModel):
    disease_name: str
    category: Optional[str] = None
    chronicity: Optional[str] = None


class StageIn(BaseModel):
    disease_id: int
    stage_name: str
    stage_order: int
    description: Optional[str] = None


class ProgressionIn(BaseModel):
    patient_id: int
    disease_id: int
    current_stage: int
    diagnosis_date: date
    severity_index: Optional[float] = 0.0
    last_updated: Optional[date] = None


class ComplicationIn(BaseModel):
    progression_id: int
    complication_name: str
    severity: Optional[str] = None
    notes: Optional[str] = None


class NaturalHistoryIn(BaseModel):
    disease_id: int
    typical_duration_days: Optional[int] = None
    mortality_rate: Optional[float] = None
    recurrence_rate: Optional[float] = None
    notes: Optional[str] = None


@app.get("/")
def home():
    return {"message": "Module 33 backend is running with MySQL"}


@app.get("/patients")
def get_patients():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Patient")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/patients")
def add_patient(patient: PatientIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Patient (FullName, DOB, Gender, ContactInfo)
        VALUES (%s, %s, %s, %s)
        """,
        (patient.full_name, patient.dob, patient.gender, patient.contact_info)
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Patient added", "PatientID": new_id}


@app.get("/diseases")
def get_diseases():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Disease")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/diseases")
def add_disease(disease: DiseaseIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Disease (DiseaseName, Category, Chronicity)
        VALUES (%s, %s, %s)
        """,
        (disease.disease_name, disease.category, disease.chronicity)
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Disease added", "DiseaseID": new_id}


@app.get("/stages")
def get_stages():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Stage ORDER BY DiseaseID, StageOrder")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/stages")
def add_stage(stage: StageIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Stage (DiseaseID, StageName, StageOrder, Description)
        VALUES (%s, %s, %s, %s)
        """,
        (stage.disease_id, stage.stage_name, stage.stage_order, stage.description)
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Stage added", "StageID": new_id}


@app.get("/progressions")
def get_progressions():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            dp.ProgressionID,
            p.FullName,
            d.DiseaseName,
            s.StageName,
            dp.DiagnosisDate,
            dp.SeverityIndex,
            dp.LastUpdated
        FROM DiseaseProgression dp
        JOIN Patient p ON dp.PatientID = p.PatientID
        JOIN Disease d ON dp.DiseaseID = d.DiseaseID
        LEFT JOIN Stage s ON dp.CurrentStage = s.StageID
        ORDER BY dp.ProgressionID
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/progressions")
def add_progression(prog: ProgressionIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO DiseaseProgression
        (PatientID, DiseaseID, CurrentStage, DiagnosisDate, SeverityIndex, LastUpdated)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            prog.patient_id,
            prog.disease_id,
            prog.current_stage,
            prog.diagnosis_date,
            prog.severity_index,
            prog.last_updated or prog.diagnosis_date
        )
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Progression added", "ProgressionID": new_id}


@app.get("/complications")
def get_complications():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            c.ComplicationID,
            c.ProgressionID,
            c.ComplicationName,
            c.Severity,
            c.Notes
        FROM Complication c
        ORDER BY c.ComplicationID
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/complications")
def add_complication(comp: ComplicationIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Complication (ProgressionID, ComplicationName, Severity, Notes)
        VALUES (%s, %s, %s, %s)
        """,
        (comp.progression_id, comp.complication_name, comp.severity, comp.notes)
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Complication added", "ComplicationID": new_id}


@app.get("/natural-history")
def get_natural_history():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM NaturalHistory")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/natural-history")
def add_natural_history(item: NaturalHistoryIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO NaturalHistory
        (DiseaseID, TypicalDurationDays, MortalityRate, RecurrenceRate, Notes)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            item.disease_id,
            item.typical_duration_days,
            item.mortality_rate,
            item.recurrence_rate,
            item.notes
        )
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Natural history added", "NaturalHistoryID": new_id}


@app.get("/summary")
def get_summary():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM vw_PatientDiseaseSummary")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows