"""
engine.py - Deterministic Eligibility & Category Relaxation Engine
Accurately assesses candidate eligibility against Indian Government examination rules.
"""

from datetime import datetime, date
from jobs_data import get_all_jobs

# Hierarchical education levels: lower levels are satisfied by higher levels
EDUCATION_HIERARCHY = {
    "10th": 1,
    "12th": 2,
    "iti": 2,
    "diploma": 3,
    "graduate": 4,
    "post_graduate": 5
}

def parse_date(date_str):
    """Safely parse ISO date string."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def calculate_age(dob_date, reference_date=None):
    """
    Calculate candidate's exact age as of reference_date.
    Default reference date: 2026-08-01 (standard GoI exam cutoff date).
    """
    if not reference_date:
        reference_date = date(2026, 8, 1)
    
    if isinstance(dob_date, str):
        dob_date = parse_date(dob_date)
    
    if not dob_date:
        return 0, 0
    
    years = reference_date.year - dob_date.year
    if (reference_date.month, reference_date.day) < (dob_date.month, dob_date.day):
        years -= 1
    
    # Precise float age for fractional evaluation
    days = (reference_date - dob_date).days
    fractional_years = round(days / 365.25, 1)
    
    return years, fractional_years

def evaluate_eligibility(candidate_profile, job):
    """
    Evaluate a candidate's profile against a single job notification.
    Returns:
        status: 'eligible', 'near_match', 'ineligible'
        score: integer 0-100
        met_criteria: list of strings
        unmet_criteria: list of strings
        notes: list of strings
    """
    met = []
    unmet = []
    notes = []
    
    # 1. AGE EVALUATION WITH CATEGORY RELAXATION
    user_age = candidate_profile.get("age")
    dob_str = candidate_profile.get("dob")
    user_category = candidate_profile.get("category", "UR").upper()
    
    if dob_str:
        user_age, _ = calculate_age(dob_str)
    elif user_age is None:
        user_age = 23  # Fallback default if not specified
    
    # Determine allowed max age with reservation relaxation
    base_min_age = job.get("min_age", 18)
    base_max_age = job.get("max_age_general", 30)
    
    relaxation_dict = job.get("age_relaxation", {})
    # Check for compound relaxation (e.g., PwD + SC/ST)
    is_pwd = candidate_profile.get("is_pwd", False)
    is_ex_sm = candidate_profile.get("is_ex_serviceman", False)
    
    extra_years = 0
    if is_pwd:
        extra_years += relaxation_dict.get("PwD", 10)
    elif is_ex_sm:
        extra_years += relaxation_dict.get("ExSM", 3)
    else:
        extra_years += relaxation_dict.get(user_category, 0)
    
    effective_max_age = base_max_age + extra_years
    
    age_ok = False
    if user_age < base_min_age:
        unmet.append(f"Underage: Minimum age required is {base_min_age} years (Current age: {user_age} years).")
    elif user_age > effective_max_age:
        relaxation_info = f" (Includes {extra_years} yrs relaxation for {user_category})" if extra_years > 0 else ""
        unmet.append(f"Overage: Maximum allowed age is {effective_max_age} years{relaxation_info} (Current age: {user_age} years).")
    else:
        age_ok = True
        relaxation_info = f" [Category {user_category} max age: {effective_max_age} yrs]" if extra_years > 0 else ""
        met.append(f"Age criteria satisfied: {user_age} years (Permitted range: {base_min_age} - {effective_max_age} years){relaxation_info}.")

    # 2. EDUCATION LEVEL & HIERARCHY EVALUATION
    user_edu = candidate_profile.get("education_level", "graduate").lower()
    allowed_edus = job.get("allowed_education", ["graduate"])
    
    user_edu_rank = EDUCATION_HIERARCHY.get(user_edu, 1)
    min_job_edu = job.get("education_level", "graduate")
    job_edu_rank = EDUCATION_HIERARCHY.get(min_job_edu, 1)
    
    edu_level_ok = False
    # If user's education level is equal or higher, or explicitly allowed
    if user_edu in allowed_edus or user_edu_rank >= job_edu_rank:
        edu_level_ok = True
        met.append(f"Education level satisfied: Qualified as '{user_edu.upper()}' (Job requires minimum '{min_job_edu.upper()}').")
    else:
        unmet.append(f"Education qualification not met: Job requires '{min_job_edu.upper()}', candidate holds '{user_edu.upper()}'.")

    # 3. STREAM / DEGREE SPECIALIZATION CHECK
    user_stream = candidate_profile.get("stream", "any").lower().strip()
    job_streams = [s.lower().strip() for s in job.get("education_streams", ["any"])]
    
    STREAM_ALIASES = {
        "cse_it": ["cse_it", "computer_science", "cs", "it", "b.tech cse", "b.e. cse"],
        "computer_science": ["cse_it", "computer_science", "cs", "it"],
        "bca": ["bca", "computer_applications", "bachelor of computer applications"],
        "mechanical": ["mechanical", "automobile", "fitter"],
        "electrical": ["electrical", "electrician", "eee"],
        "civil": ["civil"],
        "law": ["law", "llb", "ba_llb", "bba_llb", "llm"],
        "education": ["education", "bed", "deled", "btc"],
        "nursing": ["nursing", "bsc_nursing", "gnm"],
        "12th_pcm": ["12th_pcm", "pcm", "science_pcm"]
    }
    
    stream_ok = False
    if "any" in job_streams or user_stream == "any":
        stream_ok = True
        met.append("Degree stream: Any stream / specialization is eligible.")
    else:
        user_aliases = STREAM_ALIASES.get(user_stream, [user_stream])
        matched = False
        for alias in user_aliases:
            if alias in job_streams or any(alias in js for js in job_streams):
                matched = True
                break
                
        if matched:
            stream_ok = True
            display_name = "Graduation in CSE / CS & IT" if user_stream == "cse_it" else (user_stream.upper() if user_stream == "bca" else user_stream.title())
            met.append(f"Stream criteria satisfied: Candidate's field '{display_name}' matches required discipline.")
        else:
            display_name = "Graduation in CSE / CS & IT" if user_stream == "cse_it" else (user_stream.upper() if user_stream == "bca" else user_stream.title())
            unmet.append(f"Specialization required: Job specifically requires '{', '.join(job_streams).title()}', candidate stream is '{display_name}'.")

    # 4. PERCENTAGE / CUTOFF CHECK
    user_percentage = float(candidate_profile.get("percentage", 65.0) or 0)
    job_min_pct = job.get("min_percentage", 0)
    
    # Relax percentage for SC/ST/PwD in certain exams (like RBI Grade B)
    if user_category in ["SC", "ST"] or is_pwd:
        if job_min_pct >= 60:
            job_min_pct = 50
            
    pct_ok = False
    if user_percentage >= job_min_pct:
        pct_ok = True
        if job_min_pct > 0:
            met.append(f"Academic cutoff satisfied: Candidate has {user_percentage}% (Cutoff is {job_min_pct}%).")
        else:
            met.append("Academic cutoff: No minimum percentage required (Passing marks sufficient).")
    else:
        unmet.append(f"Cutoff score not met: Job requires minimum {job_min_pct}% marks (Candidate reported {user_percentage}%).")

    # 5. GENDER CHECK
    job_gender = job.get("gender_allowed", "all").lower()
    user_gender = candidate_profile.get("gender", "all").lower()
    
    gender_ok = True
    if job_gender != "all" and user_gender != "all":
        if job_gender != user_gender:
            gender_ok = False
            unmet.append(f"Gender criteria: This recruitment is only open to {job_gender.title()} candidates.")
        else:
            met.append(f"Gender eligibility satisfied ({job_gender.title()}).")

    # 6. PHYSICAL STANDARDS (IF APPLICABLE & PROVIDED)
    check_physical = candidate_profile.get("check_physical", False)
    job_has_physical = job.get("physical_required", False)
    user_height = candidate_profile.get("height_cm")
    
    if job_has_physical and check_physical and user_height:
        phys = job.get("physical_standards", {}) or {}
        min_h = phys.get("min_height_male", 165) if user_gender == "male" else phys.get("min_height_female", 152)
        if float(user_height) < float(min_h):
            unmet.append(f"Physical measurement: Minimum height required is {min_h} cm (Candidate is {user_height} cm).")
        else:
            met.append(f"Physical measurement satisfied: Height {user_height} cm meets standard (>= {min_h} cm).")
    elif job_has_physical:
        notes.append("Uniformed post: Involves physical standard test (PST) & running endurance test (PET).")

    # 7. STATE DOMICILE EVALUATION
    user_domicile = (candidate_profile.get("domicile") or "All-India").strip()
    job_state = (job.get("state") or "All-India").strip()
    state_elig = job.get("state_eligibility", "All-India")
    
    is_home_state = False
    if job_state == "All-India":
        is_home_state = False
        met.append("Jurisdiction: Central Government / All-India recruitment (Open to all Indian States & UTs).")
    elif user_domicile != "All-India" and user_domicile.lower() == job_state.lower():
        is_home_state = True
        met.append(f"📍 Home State Govt Job: You belong to {job_state} and receive full domicile reservation & quota benefits.")
    elif user_domicile == "All-India":
        is_home_state = False
        if "open to all-india" in state_elig.lower() or "open to all" in state_elig.lower():
            met.append(f"State Recruitment ({job_state}): Open to All-India candidates.")
        else:
            notes.append(f"State Recruitment ({job_state}): May require {job_state} domicile or local language proficiency.")
    else:
        is_home_state = False
        if "open to all-india" in state_elig.lower() or "open to all" in state_elig.lower():
            met.append(f"Other State Quota: Candidates from {user_domicile} can apply under Open / Unreserved category.")
        else:
            notes.append(f"State Recruitment ({job_state}): May require state domicile certificate or local language proficiency.")

    # 8. COMPUTE FINAL STATUS & SCORE
    total_checks = len(met) + len(unmet)
    score = int((len(met) / total_checks) * 100) if total_checks > 0 else 0
    
    if len(unmet) == 0:
        status = "eligible"
        score = 100
    elif len(unmet) == 1 and ("age" in unmet[0].lower() and user_age <= effective_max_age + 1):
        status = "near_match"
        score = max(score, 75)
    elif len(unmet) == 1 and ("stream" in unmet[0].lower() or "cutoff" in unmet[0].lower()):
        status = "near_match"
        score = max(score, 70)
    else:
        status = "ineligible"

    return {
        "job_id": job["id"],
        "job_title": job["title"],
        "department": job["department"],
        "tier": job["tier"],
        "tier_label": job["tier_label"],
        "sector": job["sector"],
        "state": job_state,
        "is_home_state": is_home_state,
        "state_eligibility": state_elig,
        "vacancies": job["vacancies"],
        "status": status,
        "match_score": score,
        "app_status": job["status"],
        "app_start_date": job["app_start_date"],
        "app_end_date": job["app_end_date"],
        "exam_date": job["exam_date"],
        "pay_level": job["pay_level"],
        "salary_range": job["salary_range"],
        "in_hand_salary": job["in_hand_salary"],
        "apply_url": job["apply_url"],
        "notification_pdf_url": job["notification_pdf_url"],
        "official_portal": job["official_portal"],
        "description": job["description"],
        "met_criteria": met,
        "unmet_criteria": unmet,
        "notes": notes,
        "special_skills": job.get("special_skills", []),
        "selection_stages": job.get("selection_stages", []),
        "syllabus_highlights": job.get("syllabus_highlights", []),
        "preparation_tips": job.get("preparation_tips", "")
    }

def match_all_jobs(candidate_profile):
    """
    Run evaluation against all government jobs in the database.
    Returns partitioned results:
        eligible: jobs candidate can apply for right now or soon
        near_match: jobs candidate is close to qualifying
        ineligible: jobs where criteria are not met
    """
    all_jobs = get_all_jobs()
    results = {
        "eligible": [],
        "near_match": [],
        "ineligible": [],
        "total_jobs_analyzed": len(all_jobs),
        "total_eligible_vacancies": 0
    }
    
    for job in all_jobs:
        eval_result = evaluate_eligibility(candidate_profile, job)
        status = eval_result["status"]
        results[status].append(eval_result)
        if status == "eligible":
            results["total_eligible_vacancies"] += eval_result["vacancies"]
            
    # Sort eligible: Prioritize Home State jobs first, then closing_soon, then open, then upcoming
    priority_order = {"closing_soon": 0, "open": 1, "upcoming": 2}
    results["eligible"].sort(key=lambda x: (
        0 if x.get("is_home_state") else 1,
        priority_order.get(x["app_status"], 3),
        x["app_end_date"]
    ))
    results["near_match"].sort(key=lambda x: -x["match_score"])
    
    return results
