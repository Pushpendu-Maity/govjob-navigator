"""
app.py - GovJob Navigator Flask Application
Provides API endpoints for job search, eligibility determination, deadline tracking, and AI guidance.
"""

import os
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from jobs_data import get_all_jobs, get_job_by_id
from engine import evaluate_eligibility, match_all_jobs, calculate_age
from ai_advisor import get_ai_guidance

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# In-memory storage for subscribed alerts (persists during runtime)
SUBSCRIBED_ALERTS = []

# Performance and Caching Headers
@app.after_request
def set_performance_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=86400, stale-while-revalidate=3600'
    return response

@app.route("/ping")
def ping():
    """Lightweight health check endpoint to keep server awake."""
    return jsonify({"status": "active", "timestamp": datetime.now().isoformat()}), 200

@app.route("/")
def index():
    """Render main web application interface."""
    return render_template("index.html")

@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    """List jobs with flexible filtering, searching, and sorting."""
    jobs = get_all_jobs()
    
    # Query parameters
    search = request.args.get("search", "").strip().lower()
    tier = request.args.get("tier", "").strip()
    sector = request.args.get("sector", "").strip()
    state = request.args.get("state", "").strip()
    status = request.args.get("status", "").strip()
    edu = request.args.get("education", "").strip()
    job_type = request.args.get("job_type", "").strip().lower()
    sort_by = request.args.get("sort", "status")  # 'deadline', 'vacancies', 'status', 'tier'
    
    filtered = []
    for j in jobs:
        # Job Type filter (govt vs private)
        if job_type and job_type in ["govt", "private"]:
            if j.get("job_type", "govt").lower() != job_type:
                continue

        # Search match
        if search:
            match_str = f"{j['title']} {j['department']} {j['sector']} {j.get('state', '')} {j['description']}".lower()
            if search not in match_str:
                continue
                
        # Tier filter
        if tier and str(j.get("tier")) != tier:
            continue
            
        # Sector filter
        if sector and j.get("sector", "").lower() != sector.lower():
            continue

        # State filter
        if state and state.lower() != "all-india" and j.get("state", "").lower() != state.lower():
            continue
            
        # Status filter
        if status and j.get("status") != status:
            continue
            
        # Education filter
        if edu and edu not in j.get("allowed_education", []):
            continue
            
        filtered.append(j)
        
    # Calculate days left for each job
    today = date(2026, 9, 15)
    for j in filtered:
        try:
            end_d = datetime.strptime(j["app_end_date"], "%Y-%m-%d").date()
            j["days_remaining"] = (end_d - today).days
        except Exception:
            j["days_remaining"] = 999
            
    # Sorting
    if sort_by == "vacancies":
        filtered.sort(key=lambda x: -x.get("vacancies", 0))
    elif sort_by == "deadline":
        filtered.sort(key=lambda x: x.get("days_remaining", 999))
    elif sort_by == "tier":
        filtered.sort(key=lambda x: x.get("tier", 1))
    else:
        # Priority: closing_soon > open > upcoming
        p_map = {"closing_soon": 0, "open": 1, "upcoming": 2}
        filtered.sort(key=lambda x: (p_map.get(x.get("status"), 3), x.get("days_remaining", 999)))
        
    return jsonify({
        "success": True,
        "count": len(filtered),
        "jobs": filtered
    })

@app.route("/api/check-eligibility", methods=["POST"])
def check_eligibility():
    """
    Evaluate candidate profile against all jobs.
    Computes exact age, relaxation, academic cutoff, and physical checks.
    """
    data = request.get_json() or {}
    
    # Extract candidate parameters
    profile = {
        "age": int(data.get("age", 22)) if data.get("age") else None,
        "dob": data.get("dob"),
        "category": data.get("category", "UR").upper(),
        "education_level": data.get("education_level", "graduate").lower(),
        "stream": data.get("stream", "any").lower(),
        "percentage": float(data.get("percentage", 65.0) or 0),
        "gender": data.get("gender", "male").lower(),
        "is_pwd": bool(data.get("is_pwd", False)),
        "is_ex_serviceman": bool(data.get("is_ex_serviceman", False)),
        "domicile": data.get("domicile", "All-India").strip(),
        "height_cm": float(data.get("height_cm")) if data.get("height_cm") else None,
        "check_physical": bool(data.get("check_physical", False)),
        "job_type_pref": data.get("job_type_pref", "govt").strip().lower()
    }
    
    # If DOB is provided, calculate exact age
    if profile["dob"]:
        calculated_age, fractional = calculate_age(profile["dob"])
        profile["age"] = calculated_age
        profile["fractional_age"] = fractional
    else:
        profile["fractional_age"] = profile["age"]
        
    results = match_all_jobs(profile)
    
    return jsonify({
        "success": True,
        "profile_summary": profile,
        "summary": {
            "eligible_count": len(results["eligible"]),
            "near_match_count": len(results["near_match"]),
            "ineligible_count": len(results["ineligible"]),
            "total_analyzed": results["total_jobs_analyzed"],
            "total_vacancies": results["total_eligible_vacancies"]
        },
        "eligible": results["eligible"],
        "near_match": results["near_match"],
        "ineligible": results["ineligible"]
    })

@app.route("/api/deadlines", methods=["GET"])
def get_deadlines():
    """Fetch active deadlines sorted by closest closing date."""
    jobs = get_all_jobs()
    today = date(2026, 9, 15)
    
    deadline_list = []
    for j in jobs:
        try:
            end_d = datetime.strptime(j["app_end_date"], "%Y-%m-%d").date()
            days_left = (end_d - today).days
            start_d = datetime.strptime(j["app_start_date"], "%Y-%m-%d").date()
            is_open = start_d <= today <= end_d
        except Exception:
            days_left = 999
            is_open = False
            
        deadline_list.append({
            "id": j["id"],
            "title": j["title"],
            "department": j["department"],
            "tier_label": j["tier_label"],
            "sector": j["sector"],
            "vacancies": j["vacancies"],
            "app_start_date": j["app_start_date"],
            "app_end_date": j["app_end_date"],
            "exam_date": j["exam_date"],
            "days_remaining": days_left,
            "status": j["status"],
            "apply_url": j["apply_url"],
            "notification_pdf_url": j["notification_pdf_url"],
            "pay_level": j["pay_level"],
            "in_hand_salary": j["in_hand_salary"]
        })
        
    # Sort: closing_soon (0 to 7 days) first, then open, then upcoming
    deadline_list.sort(key=lambda x: x["days_remaining"])
    
    return jsonify({
        "success": True,
        "count": len(deadline_list),
        "deadlines": deadline_list
    })

@app.route("/api/job/<job_id>", methods=["GET"])
def get_job_detail(job_id):
    """Fetch complete details of a specific job by ID."""
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({"success": False, "error": "Job not found"}), 404
        
    return jsonify({
        "success": True,
        "job": job
    })

@app.route("/api/ai-counselor", methods=["POST"])
def ai_counselor():
    """Natural language counselor and recommendation endpoint."""
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    profile = data.get("profile")
    
    if not query and not profile:
        return jsonify({"success": False, "error": "No query or profile supplied"}), 400
        
    guidance = get_ai_guidance(query, profile)
    return jsonify({
        "success": True,
        "guidance": guidance
    })

@app.route("/api/subscribe-alert", methods=["POST"])
def subscribe_alert():
    """Register user email / phone for job notifications."""
    data = request.get_json() or {}
    contact = data.get("contact", "").strip()
    category = data.get("category", "UR")
    education = data.get("education", "graduate")
    sectors = data.get("sectors", ["All"])
    
    if not contact:
        return jsonify({"success": False, "error": "Contact details required"}), 400
        
    subscription = {
        "contact": contact,
        "category": category,
        "education": education,
        "sectors": sectors,
        "subscribed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    SUBSCRIBED_ALERTS.append(subscription)
    
    return jsonify({
        "success": True,
        "message": f"Successfully registered alerts for {contact}! You will receive notifications matching your criteria."
    })

if __name__ == "__main__":
    print("GovJob Navigator Server starting on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
