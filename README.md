# Course Difficulty & Instructor Effectiveness Analyzer  
## Real-Time Lakehouse + AI Analytics Platform

An end-to-end **Microsoft Fabric** project that ingests batch academic data and simulated real-time LMS events, processes them through a **Bronze / Silver / Gold** lakehouse architecture, generates KPI tables and ML-based risk predictions, and exposes results through **FastAPI** and **Power BI**.

---

## Problem Statement

Educational institutions generate large volumes of student interaction, assessment, and course data. However, this data is often fragmented and not used effectively to:

- identify difficult courses  
- detect at-risk students  
- evaluate instructor effectiveness  
- monitor real-time engagement  

This project builds a unified analytics platform to solve these problems using a lakehouse architecture.

---

## Objective

- Build a **lakehouse-based data platform**  
- Combine **batch + streaming data**  
- Generate **KPIs and ML predictions**  
- Expose insights via **APIs and dashboards**  
- Simulate a **real-world analytics system**

---

## Architecture
```text
Batch Data (OULAD / UCI)
        +
Streaming LMS Events
        ↓
   Fabric Eventstream
        ↓
   Lakehouse Bronze Tables
        ↓
   Silver Cleaning / Enrichment
        ↓
   Gold KPI / Model Tables
        ↓
   FastAPI + Power BI
```


---

## Tech Stack

- Microsoft Fabric (Lakehouse, Eventstream, Notebooks)
- Apache Spark (via Fabric)
- Delta Lake
- Python
- FastAPI
- Power BI
- Pandas / PyODBC

---

## Data Sources

### Batch Data
- Open University Learning Analytics Dataset (OULAD)

### Streaming Data (Simulated)
Generated using `lms_producer.py`:
- lecture_viewed
- quiz_attempted
- assignment_submitted
- attendance_marked
- forum_posted

---

## Lakehouse Design

### Silver Tables (Cleaned Layer)

| Table | Description |
|------|------------|
| silver_students | Student demographics + outcomes |
| silver_assessments | Assessment scores and delays |
| silver_lms_events | Streaming LMS events |
| silver_vle_activity | Clickstream activity |
| silver_instructors | Instructor mapping |

---

### Gold Tables (Analytics Layer)

| Table | Purpose |
|------|--------|
| gold_course_difficulty | Course difficulty metrics |
| gold_engagement | Student engagement scoring |
| gold_instructor_effectiveness | Instructor performance |
| gold_student_risk | Risk scoring (feature table) |
| gold_student_risk_predictions | ML predictions |
| gold_weekly_trends | Weekly activity trends |

---

## Pipeline Flow

1. **Bronze Layer**
   - Raw ingestion of datasets and streaming events

2. **Silver Layer**
   - Cleaning, standardization, enrichment
   - Sessionization and feature creation

3. **Gold Layer**
   - KPI aggregation
   - Risk scoring
   - Trend generation

4. **ML Layer**
   - Predict student risk
   - Store predictions in Gold tables

5. **Serving Layer**
   - FastAPI endpoints

6. **Visualization**
   - Power BI dashboard

---

## Streaming Pipeline

- Python producer (`lms_producer.py`)
- Sends JSON events to Fabric Eventstream
- Eventstream writes to Lakehouse (Bronze)
- Spark processes into Silver → Gold

### Sample Event

```json
{
  "student_id": 101,
  "course_id": "CS101",
  "event_type": "quiz_attempted",
  "score": 65,
  "timestamp": "2026-03-31T14:30:00"
}

---
```

## KPIs & Metrics

### Course Level
- pass_rate  
- dropout_rate  
- fail_rate  
- avg_score  
- avg_submission_delay  
- difficulty_score  

### Student Level
- risk_score  
- engagement_score  
- avg_score  
- total_clicks  
- activity frequency  

### Instructor Level
- effectiveness_score  
- avg_student_score  
- engagement_clicks  
- pass_rate per instructor  

---

## FastAPI Endpoints

| Endpoint | Description |
|---------|------------|
| `/health` | Health check |
| `/student/{id}/risk` | ML risk prediction |
| `/student/{id}/engagement` | Engagement metrics |
| `/student/{id}/recommendations` | Rule-based suggestions |
| `/course/{id}/difficulty` | Course metrics |
| `/instructor/{id}/effectiveness` | Instructor metrics |
| `/courses/summary` | Overall course summary |

---

## Running the API

```bash
uvicorn student_api.main:app --reload --port 8000
```
## Repository Structure

```text
capstone_project/
├── README.md
├── lms_producer.py
├── student_api/
│   ├── main.py
│   ├── db.py
│   └── requirements.txt
├── notebooks/
│   ├── 00_validation_test.ipynb
│   ├── 01_bronze_batch_ingestion.ipynb
│   ├── 02_silver_transformation.ipynb
│   ├── 03_gold_kpi_aggregations.ipynb
│   ├── 04_ml_risk_model.ipynb
│   └── 05_gold_enhancements.ipynb
├── sample_data/
└── assets/
```

---

## Setup Instructions

### Prerequisites

- Microsoft Fabric workspace access
- Fabric trial or capacity access
- Python 3.11+
- FastAPI
- Uvicorn
- pandas
- pyodbc or equivalent SQL connector
- access to your Fabric SQL analytics endpoint

### Install Dependencies

```bash
pip install -r requirements.txt 
```

---

## Run the API

Start the FastAPI server:

    uvicorn student_api.main:app --reload --port 8000

---

## Verify API

### Health check:

    GET http://127.0.0.1:8000/health

### Example endpoints:

    GET http://127.0.0.1:8000/student/101/risk
    GET http://127.0.0.1:8000/student/101/engagement
    GET http://127.0.0.1:8000/course/CS101/difficulty
    GET http://127.0.0.1:8000/instructor/I45/effectiveness

---

## Run Streaming Producer

Start the LMS event simulator:

    python lms_producer.py

This will continuously push simulated events to Fabric Eventstream.

---

## Fabric Execution Flow

1. Upload datasets to Lakehouse  
2. Run notebooks in order:
   - 00_validation_test  
   - 01_bronze_batch_ingestion  
   - 02_silver_transformation  
   - 03_gold_kpi_aggregations  
   - 04_ml_risk_model  
   - 05_gold_enhancements  
3. Start Eventstream  
4. Run producer script  
5. Refresh semantic model  
6. Open Power BI report  

---

## Validation Checklist

- Bronze tables populated  
- Silver tables cleaned  
- Gold tables contain KPIs  
- Streaming events flowing  
- ML predictions generated  
- API endpoints returning data  
- Power BI dashboard loading  

---