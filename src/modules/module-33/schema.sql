-- =========================================
-- DATABASE SETUP
-- =========================================
CREATE DATABASE IF NOT EXISTS DiseaseProgressionDB;
USE DiseaseProgressionDB;

-- =========================================
-- TABLE: Patient
-- =========================================
CREATE TABLE Patient (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT CHECK (Age > 0 AND Age < 120),
    Gender ENUM('Male','Female','Other') NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- TABLE: Disease
-- =========================================
CREATE TABLE Disease (
    DiseaseID INT AUTO_INCREMENT PRIMARY KEY,
    DiseaseName VARCHAR(100) NOT NULL UNIQUE
);

-- =========================================
-- TABLE: Stage
-- =========================================
CREATE TABLE Stage (
    StageID INT AUTO_INCREMENT PRIMARY KEY,
    DiseaseID INT NOT NULL,
    StageName VARCHAR(50) NOT NULL,
    StageOrder INT NOT NULL,
    ClinicalCriteria TEXT,
    TypicalDuration INT,
    FOREIGN KEY (DiseaseID) REFERENCES Disease(DiseaseID)
        ON DELETE CASCADE
);

-- =========================================
-- TABLE: DiseaseProgression
-- =========================================
CREATE TABLE DiseaseProgression (
    ProgressionID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DiseaseID INT NOT NULL,
    StartDate DATE NOT NULL,
    LastUpdated DATE,
    CurrentStage INT,
    SeverityIndex INT DEFAULT 1 CHECK (SeverityIndex >= 1),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
        ON DELETE CASCADE,
    FOREIGN KEY (DiseaseID) REFERENCES Disease(DiseaseID)
        ON DELETE CASCADE
);

-- =========================================
-- TABLE: StageTransitionLog
-- =========================================
CREATE TABLE StageTransitionLog (
    TransitionID INT AUTO_INCREMENT PRIMARY KEY,
    ProgressionID INT NOT NULL,
    StageID INT NOT NULL,
    TransitionDate DATE NOT NULL,
    Notes TEXT,
    FOREIGN KEY (ProgressionID) REFERENCES DiseaseProgression(ProgressionID)
        ON DELETE CASCADE,
    FOREIGN KEY (StageID) REFERENCES Stage(StageID)
);

-- =========================================
-- TABLE: Complication
-- =========================================
CREATE TABLE Complication (
    ComplicationID INT AUTO_INCREMENT PRIMARY KEY,
    ProgressionID INT NOT NULL,
    ComplicationType VARCHAR(100) NOT NULL,
    OccurrenceDate DATE NOT NULL,
    Severity ENUM('Mild','Moderate','Severe'),
    Outcome VARCHAR(100),
    FOREIGN KEY (ProgressionID) REFERENCES DiseaseProgression(ProgressionID)
        ON DELETE CASCADE
);

-- =========================================
-- TABLE: NaturalHistory
-- =========================================
CREATE TABLE NaturalHistory (
    HistoryID INT AUTO_INCREMENT PRIMARY KEY,
    DiseaseID INT NOT NULL,
    PopulationGroup VARCHAR(50),
    AvgProgressionRate DECIMAL(5,2),
    MedianSurvival INT,
    RiskFactors TEXT,
    FOREIGN KEY (DiseaseID) REFERENCES Disease(DiseaseID)
        ON DELETE CASCADE
);

-- =========================================
-- INDEXES (Performance Optimization)
-- =========================================
CREATE INDEX idx_patient ON DiseaseProgression(PatientID);
CREATE INDEX idx_disease ON DiseaseProgression(DiseaseID);
CREATE INDEX idx_transition_date ON StageTransitionLog(TransitionDate);

-- =========================================
-- SAMPLE DATA (DML)
-- =========================================

INSERT INTO Patient (Name, Age, Gender) VALUES
('Ravi Kumar', 45, 'Male'),
('Anita Sharma', 50, 'Female'),
('Amit Singh', 60, 'Male');

INSERT INTO Disease (DiseaseName) VALUES
('Diabetes'),
('Chronic Kidney Disease'),
('COPD');

-- Stages
INSERT INTO Stage (DiseaseID, StageName, StageOrder) VALUES
(1, 'Stage 1', 1),
(1, 'Stage 2', 2),
(1, 'Stage 3', 3),
(2, 'Stage 1', 1),
(2, 'Stage 2', 2);

-- Disease Progression
INSERT INTO DiseaseProgression 
(PatientID, DiseaseID, StartDate, LastUpdated, CurrentStage, SeverityIndex)
VALUES
(1,1,'2023-01-01','2023-06-01',2,2),
(2,2,'2022-05-01','2023-05-01',2,3);

-- Stage Transitions
INSERT INTO StageTransitionLog 
(ProgressionID, StageID, TransitionDate) VALUES
(1,1,'2023-01-01'),
(1,2,'2023-06-01'),
(2,4,'2022-05-01'),
(2,5,'2023-05-01');

-- Complications
INSERT INTO Complication 
(ProgressionID, ComplicationType, OccurrenceDate, Severity, Outcome) VALUES
(1,'Neuropathy','2023-08-01','Moderate','Ongoing'),
(2,'Anemia','2023-06-01','Severe','Critical');

-- Natural History
INSERT INTO NaturalHistory 
(DiseaseID, PopulationGroup, AvgProgressionRate, MedianSurvival)
VALUES
(1,'Adults',1.5,20),
(2,'Elderly',2.0,10);

-- =========================================
-- TRIGGER: Auto Severity Update
-- =========================================
DELIMITER //
CREATE TRIGGER trg_UpdateSeverity
AFTER INSERT ON StageTransitionLog
FOR EACH ROW
BEGIN
    UPDATE DiseaseProgression
    SET SeverityIndex = (
        SELECT StageOrder FROM Stage WHERE StageID = NEW.StageID
    ),
    LastUpdated = NEW.TransitionDate
    WHERE ProgressionID = NEW.ProgressionID;
END //
DELIMITER ;

-- =========================================
-- TRIGGER: Auto Risk Increase on Complication
-- =========================================
DELIMITER //
CREATE TRIGGER trg_UpdateRisk
AFTER INSERT ON Complication
FOR EACH ROW
BEGIN
    UPDATE DiseaseProgression
    SET SeverityIndex = SeverityIndex + 1
    WHERE ProgressionID = NEW.ProgressionID;
END //
DELIMITER ;

-- =========================================
-- STORED PROCEDURE: Risk Score
-- =========================================
DELIMITER //
CREATE PROCEDURE CalcRiskScore(
    IN p_id INT,
    OUT risk_score INT
)
BEGIN
    DECLARE comp_count INT;

    SELECT COUNT(*) INTO comp_count
    FROM Complication
    WHERE ProgressionID IN (
        SELECT ProgressionID
        FROM DiseaseProgression
        WHERE PatientID = p_id
    );

    SET risk_score = comp_count * 10;
END //
DELIMITER ;

-- =========================================
-- STORED PROCEDURE: Get Progression History
-- =========================================
DELIMITER //
CREATE PROCEDURE GetProgressionHistory(
    IN p_id INT,
    IN d_id INT
)
BEGIN
    SELECT st.TransitionDate, s.StageName
    FROM StageTransitionLog st
    JOIN DiseaseProgression dp ON st.ProgressionID = dp.ProgressionID
    JOIN Stage s ON st.StageID = s.StageID
    WHERE dp.PatientID = p_id AND dp.DiseaseID = d_id
    ORDER BY st.TransitionDate;
END //
DELIMITER ;

-- =========================================
-- VIEW: Patient Summary
-- =========================================
CREATE VIEW vw_PatientDiseaseSummary AS
SELECT 
    p.PatientID,
    p.Name,
    d.DiseaseName,
    dp.CurrentStage,
    dp.SeverityIndex,
    COUNT(c.ComplicationID) AS TotalComplications,
    MAX(c.OccurrenceDate) AS LastComplication
FROM Patient p
JOIN DiseaseProgression dp ON p.PatientID = dp.PatientID
JOIN Disease d ON dp.DiseaseID = d.DiseaseID
LEFT JOIN Complication c ON dp.ProgressionID = c.ProgressionID
GROUP BY p.PatientID, d.DiseaseName, dp.CurrentStage, dp.SeverityIndex;

-- =========================================
-- ADVANCED QUERIES
-- =========================================

-- Q1: Progression Rate
SELECT ProgressionID,
DATEDIFF(MAX(TransitionDate), MIN(TransitionDate)) AS DaysElapsed
FROM StageTransitionLog
GROUP BY ProgressionID;

-- Q2: Rapid Progressors (Window Function)
SELECT 
    ProgressionID,
    StageID,
    TransitionDate,
    LAG(TransitionDate) OVER (PARTITION BY ProgressionID ORDER BY TransitionDate) AS PrevDate
FROM StageTransitionLog;

-- Q3: Complication Frequency
SELECT 
    dp.CurrentStage,
    COUNT(c.ComplicationID) AS TotalComplications
FROM DiseaseProgression dp
JOIN Complication c ON dp.ProgressionID = c.ProgressionID
GROUP BY dp.CurrentStage;

-- Q4: High Risk Patients
SELECT * FROM DiseaseProgression
WHERE SeverityIndex >= 3;

-- Q5: Risk Level Classification
SELECT PatientID,
CASE
    WHEN SeverityIndex >= 4 THEN 'High Risk'
    WHEN SeverityIndex >= 2 THEN 'Medium Risk'
    ELSE 'Low Risk'
END AS RiskLevel
FROM DiseaseProgression;