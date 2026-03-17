from fastapi import FastAPI
import sqlite3

app = FastAPI()

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_connection():
    return sqlite3.connect("module33.db")

# -------------------------------
# INITIALIZE DATABASE (DBMS RULE)
# -------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Patient Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Patient (
        patient_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER CHECK(age > 0)
    )
    """)

    # Disease Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Disease (
        disease_id INTEGER PRIMARY KEY,
        disease_name TEXT NOT NULL
    )
    """)

    # Disease Progression Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Progression (
        stage_id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        disease_id INTEGER,
        stage TEXT,
        date TEXT,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
        FOREIGN KEY (disease_id) REFERENCES Disease(disease_id)
    )
    """)

    # Complication Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Complication (
        comp_id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        description TEXT,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# API ROUTES (RESTFUL)
# -------------------------------

@app.get("/")
def home():
    return {"message": "Module 33 - Disease Progression API running"}

# -------------------------------
# PATIENT APIs
# -------------------------------

@app.post("/patients")
def add_patient(patient_id: int, name: str, age: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Patient VALUES (?, ?, ?)", (patient_id, name, age))
    conn.commit()
    conn.close()
    return {"message": "Patient added successfully"}

@app.get("/patients")
def get_patients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patient")
    data = cursor.fetchall()
    conn.close()
    return {"patients": data}

# -------------------------------
# DISEASE APIs
# -------------------------------

@app.post("/diseases")
def add_disease(disease_id: int, disease_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Disease VALUES (?, ?)", (disease_id, disease_name))
    conn.commit()
    conn.close()
    return {"message": "Disease added"}

@app.get("/diseases")
def get_diseases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Disease")
    data = cursor.fetchall()
    conn.close()
    return {"diseases": data}

# -------------------------------
# PROGRESSION APIs
# -------------------------------

@app.post("/progression")
def add_progression(stage_id: int, patient_id: int, disease_id: int, stage: str, date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Progression VALUES (?, ?, ?, ?, ?)",
        (stage_id, patient_id, disease_id, stage, date)
    )
    conn.commit()
    conn.close()
    return {"message": "Progression added"}

@app.get("/progression")
def get_progression():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, d.disease_name, pr.stage, pr.date
        FROM Progression pr
        JOIN Patient p ON pr.patient_id = p.patient_id
        JOIN Disease d ON pr.disease_id = d.disease_id
    """)
    data = cursor.fetchall()
    conn.close()
    return {"progression": data}

# -------------------------------
# COMPLICATION APIs
# -------------------------------

@app.post("/complications")
def add_complication(comp_id: int, patient_id: int, description: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Complication VALUES (?, ?, ?)",
        (comp_id, patient_id, description)
    )
    conn.commit()
    conn.close()
    return {"message": "Complication added"}

@app.get("/complications")
def get_complications():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, c.description
        FROM Complication c
        JOIN Patient p ON c.patient_id = p.patient_id
    """)
    data = cursor.fetchall()
    conn.close()
    return {"complications": data}
