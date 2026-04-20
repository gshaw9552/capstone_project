# main.py
from fastapi import FastAPI, HTTPException
from db import query

app = FastAPI(
    title="Student Analytics API",
    description="Serves KPIs from the Student Analytics Platform Gold layer",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

# ─────────────────────────────────────────────
# STUDENT RISK
# Source: gold_student_risk_predictions (ML model output)
# ─────────────────────────────────────────────

@app.get("/student/{student_id}/risk")
def get_student_risk(student_id: int):
    sql = f"""
        SELECT 
            student_id,
            avg_score,
            total_clicks,
            num_of_prev_attempts,
            studied_credits,
            is_at_risk,
            predicted_at_risk,
            risk_probability,
            _model_version,
            _scored_at
        FROM gold_student_risk_predictions
        WHERE student_id = {student_id}
    """
    df = query(sql)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found in predictions")
    
    row = df.iloc[0].to_dict()
    row["risk_label"] = "High Risk" if row["risk_probability"] >= 0.6 else \
                        "Medium Risk" if row["risk_probability"] >= 0.4 else "Low Risk"
    return row

# ─────────────────────────────────────────────
# COURSE DIFFICULTY
# Source: gold_course_difficulty (KPI aggregation)
# ─────────────────────────────────────────────

@app.get("/course/{course_id}/difficulty")
def get_course_difficulty(course_id: str):
    sql = f"""
        SELECT
            course_id,
            total_students,
            passed_students,
            failed_students,
            withdrawn_students,
            pass_rate,
            dropout_rate,
            fail_rate,
            avg_score,
            avg_submission_delay,
            difficulty_score,
            difficulty_band
        FROM gold_course_difficulty
        WHERE course_id = '{course_id.upper()}'
    """
    df = query(sql)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    return df.iloc[0].to_dict()

# ─────────────────────────────────────────────
# INSTRUCTOR EFFECTIVENESS
# Source: gold_instructor_effectiveness (KPI aggregation)
# ─────────────────────────────────────────────

@app.get("/instructor/{instructor_id}/effectiveness")
def get_instructor_effectiveness(instructor_id: str):
    sql = f"""
        SELECT
            instructor_id,
            instructor_name,
            department,
            course_id,
            pass_rate,
            dropout_rate,
            avg_student_score,
            avg_engagement_clicks,
            effectiveness_score,
            effectiveness_band
        FROM gold_instructor_effectiveness
        WHERE instructor_id = '{instructor_id.upper()}'
    """
    df = query(sql)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Instructor {instructor_id} not found")
    return df.iloc[0].to_dict()

# ─────────────────────────────────────────────
# REAL-TIME ENGAGEMENT
# Source: gold_engagement (streaming events aggregation)
# ─────────────────────────────────────────────

@app.get("/student/{student_id}/engagement")
def get_student_engagement(student_id: int):
    sql = f"""
        SELECT
            student_id,
            course_id,
            total_events,
            weighted_event_score,
            avg_duration_min,
            active_days,
            last_active_ts,
            avg_event_score,
            engagement_score,
            engagement_band
        FROM gold_engagement
        WHERE student_id = {student_id}
    """
    df = query(sql)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No engagement data for student {student_id}")
    return df.to_dict(orient="records")

# ─────────────────────────────────────────────
# RECOMMENDATIONS
# Source: gold_student_risk + gold_engagement (rule-based)
# ─────────────────────────────────────────────

@app.get("/student/{student_id}/recommendations")
def get_recommendations(student_id: int):
    # Get risk profile
    risk_sql = f"""
        SELECT risk_probability, avg_score, total_clicks, num_of_prev_attempts
        FROM gold_student_risk_predictions
        WHERE student_id = {student_id}
    """
    risk_df = query(risk_sql)
    if risk_df.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    row = risk_df.iloc[0]
    recommendations = []

    # Rule-based recommendations derived from feature values
    if row["risk_probability"] >= 0.6:
        recommendations.append({
            "priority": "HIGH",
            "action": "Immediate academic support intervention required",
            "reason": f"Risk probability {row['risk_probability']:.0%}"
        })

    if row["avg_score"] < 50:
        recommendations.append({
            "priority": "HIGH",
            "action": "Enroll in remedial assessment sessions",
            "reason": f"Average score is {row['avg_score']:.1f} — below passing threshold"
        })

    if row["total_clicks"] < 500:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Increase VLE engagement — review course materials weekly",
            "reason": f"Total platform interactions: {int(row['total_clicks'])} — low engagement"
        })

    if row["num_of_prev_attempts"] >= 2:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Meet with academic advisor to review study strategy",
            "reason": f"{int(row['num_of_prev_attempts'])} previous attempts recorded"
        })

    if not recommendations:
        recommendations.append({
            "priority": "LOW",
            "action": "Maintain current study habits",
            "reason": "Student is on track — no immediate intervention needed"
        })

    return {
        "student_id": student_id,
        "risk_probability": round(float(row["risk_probability"]), 4),
        "recommendations": recommendations
    }

# ─────────────────────────────────────────────
# FORECAST (trend-based)
# Source: gold_weekly_trends
# ─────────────────────────────────────────────

@app.get("/course/{course_id}/forecast")
def get_course_forecast(course_id: str):
    sql = f"""
        SELECT
            course_id,
            semester,
            week_number,
            total_clicks,
            active_students,
            avg_clicks_per_student
        FROM gold_weekly_trends
        WHERE course_id = '{course_id.upper()}'
        ORDER BY semester, week_number
    """
    df = query(sql)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No trend data for course {course_id}")
    
    # Simple trend: compare last 4 weeks avg vs previous 4 weeks avg
    records = df.to_dict(orient="records")
    recent     = df.tail(4)["total_clicks"].mean()
    prior      = df.iloc[-8:-4]["total_clicks"].mean() if len(df) >= 8 else None
    trend      = "increasing" if prior and recent > prior else \
                 "decreasing" if prior and recent < prior else "stable"

    return {
        "course_id": course_id.upper(),
        "trend": trend,
        "recent_avg_clicks": round(float(recent), 2),
        "prior_avg_clicks":  round(float(prior), 2) if prior else None,
        "weekly_data":       records
    }

# ─────────────────────────────────────────────
# ALL COURSES SUMMARY
# ─────────────────────────────────────────────

@app.get("/courses/summary")
def get_all_courses():
    sql = """
        SELECT
            d.course_id,
            d.difficulty_band,
            d.difficulty_score,
            d.pass_rate,
            d.dropout_rate,
            d.avg_score,
            i.instructor_name,
            i.effectiveness_score,
            i.effectiveness_band
        FROM gold_course_difficulty d
        LEFT JOIN gold_instructor_effectiveness i ON d.course_id = i.course_id
        ORDER BY d.difficulty_score DESC
    """
    df = query(sql)
    return df.to_dict(orient="records")