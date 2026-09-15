"""
ai_advisor.py - AI Government Job & Exam Counselor
Provides intelligent counseling, salary insights, exam syllabus breakdowns, and career pathways.
"""

from jobs_data import get_all_jobs

FAQ_KNOWLEDGE_BASE = [
    {
        "keywords": ["direct merit", "no exam", "without exam", "no test", "10th merit"],
        "title": "Government Jobs Without Written Exam (Direct Merit)",
        "answer": """**1. India Post Gramin Dak Sevak (GDS):** 
Over 44,000+ posts of Branch Postmaster (BPM) and Assistant Branch Postmaster (ABPM) are filled **100% on the basis of 10th Class Board marks**. No entrance exam or interview is conducted.
- **Eligibility:** 10th pass with Maths & English + Basic Computer knowledge.
- **Age:** 18 to 40 years (Relaxation: OBC +3y, SC/ST +5y, PwD +10y).
- **Salary:** ₹16,500 - ₹22,000/month.

**2. Apprentice Posts in Railways & PSUs:**
Railway workshops (RRC Northern, Western, Central) recruit thousands of Trade Apprentices every year based purely on 10th + ITI marks. Completing Railway apprenticeship gives 20% reserved quota in RRB Group D permanent recruitments!"""
    },
    {
        "keywords": ["10th", "12th", "basic", "high salary", "easy", "entry level"],
        "title": "Top Paying Government Jobs for 10th & 12th Pass",
        "answer": """You don't need a graduate degree to earn a handsome government salary with permanent benefits:

1. **Delhi Police Executive Constable (12th Pass):**
   - In-hand salary: **₹38,000 - ₹43,000/month** (Level 3 + high Delhi HRA + Ration Allowance).
2. **State Police Constable (UP / MP / Bihar) (12th Pass):**
   - In-hand salary: **₹34,000 - ₹38,000/month**.
3. **SSC Multi-Tasking Staff (MTS) & Havaldar (10th Pass):**
   - In-hand salary: **₹28,500 - ₹33,000/month** in Central Ministries.
4. **Railway RRB Group D (Trackman / Pointsman) (10th / ITI):**
   - In-hand salary: **₹26,000 - ₹31,000/month** + Free All-India Railway Travel Passes for family!
5. **CISF Constable Tradesman (10th Pass):**
   - In-hand salary: **₹32,000 - ₹37,000/month**."""
    },
    {
        "keywords": ["cgl", "ssc", "bank", "ibps", "po", "difference", "which is better"],
        "title": "SSC CGL vs IBPS Bank PO: Which Should You Choose?",
        "answer": """| Parameter | SSC CGL (ASO / Inspector) | IBPS PO (Bank Manager) |
|---|---|---|
| **Work-Life Balance** | High (5-day week, 9 to 5, fixed central office) | Moderate (High public pressure & sales targets) |
| **Starting In-Hand Salary** | ₹45,000 to ₹82,000 (Level 7) | ₹58,000 to ₹68,000 + Leased Quarter (₹15-30k) |
| **Exam Speed Required** | Moderate speed, deep conceptual depth | Extreme speed (20-min sectional timers) |
| **Maths Level** | Advanced (Algebra, Trigonometry, Geometry) | Commercial / Arithmetic (DI, Percentage, Profit) |
| **Transfer Policy** | Zonal / State stability (especially CSS/ASO in New Delhi) | All-India transfer every 3 years |
| **Recommendation** | Pick SSC CGL if you value social prestige and peace of mind. Pick Bank PO if you want fast recruitment cycles (6 months from exam to joining) and rapid promotions!"""
    },
    {
        "keywords": ["salary", "7th cpc", "pay level", "da", "hra", "how much salary"],
        "title": "Understanding 7th Pay Commission (7th CPC) Salary Structure",
        "answer": """Your monthly government salary is calculated as:
**Gross Salary = Basic Pay + Dearness Allowance (DA ~50%) + House Rent Allowance (HRA 9% to 27%) + Transport Allowance (TA)**

* **Pay Level 1 (10th Pass - MTS, Group D, Peon):** Basic ₹18,000 -> In-Hand ₹26,000 - ₹32,000
* **Pay Level 2 (ALP, Accounts Clerk):** Basic ₹19,900 -> In-Hand ₹28,000 - ₹35,000 (+ Running Allowance for ALP)
* **Pay Level 3 (Police Constable, CISF):** Basic ₹21,700 -> In-Hand ₹32,000 - ₹40,000
* **Pay Level 6 (Sub-Inspector SI, Junior Engineer JE):** Basic ₹35,400 -> In-Hand ₹52,000 - ₹62,000
* **Pay Level 7 (SSC CGL Inspector, ASO, Nursing Officer):** Basic ₹44,900 -> In-Hand ₹68,000 - ₹82,000
* **Pay Level 10 (UPSC IAS/IPS, CDS Lieutenant, ESE/IES):** Basic ₹56,100 -> In-Hand ₹85,000 - ₹1,15,000 + Official Car & Bungalow!"""
    },
    {
        "keywords": ["relaxation", "age limit", "obc", "sc", "st", "pwd", "quota"],
        "title": "Government Age Relaxation & Reservation Rules",
        "answer": """Under Department of Personnel & Training (DoPT) guidelines, upper age limit relaxations are:
1. **OBC (Non-Creamy Layer):** +3 Years (Valid OBC-NCL certificate issued within 1 financial year required).
2. **SC / ST Candidates:** +5 Years (Permanent caste certificate).
3. **PwD (Persons with Benchmark Disabilities):**
   - General/EWS PwD: +10 Years
   - OBC PwD: +13 Years
   - SC/ST PwD: +15 Years
4. **Ex-Servicemen (Ex-SM):** Military service duration + 3 years.
5. **State Domicile:** State PSCs (like UPPSC, BPSC, MPSC) often allow general candidates up to **40 years of age**!"""
    }
]

def get_ai_guidance(query_text, candidate_profile=None):
    """
    Match query against knowledge base or generate personalized context.
    """
    query_lower = query_text.lower().strip()
    
    # 1. Search FAQ Knowledge Base
    for item in FAQ_KNOWLEDGE_BASE:
        for kw in item["keywords"]:
            if kw in query_lower:
                return {
                    "matched": True,
                    "title": item["title"],
                    "response": item["answer"],
                    "suggested_actions": [
                        "Check your eligibility in the Eligibility Finder tab",
                        "View active application deadlines in the Deadlines tab"
                    ]
                }
                
    # 2. Dynamic generation based on profile
    if candidate_profile:
        edu = candidate_profile.get("education_level", "graduate")
        cat = candidate_profile.get("category", "UR")
        age = candidate_profile.get("age", 23)
        
        all_jobs = get_all_jobs()
        matching_titles = []
        for j in all_jobs:
            if edu in j.get("allowed_education", []):
                matching_titles.append(j["title"])
                
        top_picks = matching_titles[:4]
        
        return {
            "matched": False,
            "title": f"Personalized Recommendation for {cat} Candidate ({edu.upper()})",
            "response": f"""Based on your profile as a **{age}-year-old {edu.upper()} candidate ({cat} category)**:

1. **High Priority Target Exams:**
{chr(10).join([f"- **{title}**" for title in top_picks])}

2. **Preparation Strategy:**
- Since you fall under **{cat} category**, take advantage of age and cutoff relaxations where applicable.
- Focus on building solid foundations in **Quantitative Aptitude, Logical Reasoning, and General Awareness (Polity & Current Affairs)**.
- Start solving previous 5-year question papers (PYQs) for high-vacancy recruitments.

3. **Next Step:**
Open the **Eligibility Finder** tab to view your complete breakdown of 100% eligible exams with direct apply links!""",
            "suggested_actions": [
                "Run instant assessment in Eligibility Finder",
                "Bookmark closing soon exams"
            ]
        }
        
    # 3. Default fallback advice
    return {
        "matched": False,
        "title": "GovJob Navigator AI Career Guidance",
        "response": """Government jobs in India are broadly classified into 5 tiers:
1. **Tier 1 (10th/12th):** Postal GDS, SSC MTS, Railway Group D, Police Constable
2. **Tier 2 (ITI/Diploma):** RRB ALP, RRB Technician, SSC Junior Engineer
3. **Tier 3 (Graduate):** SSC CGL, IBPS Bank PO/Clerk, State Police Sub-Inspector
4. **Tier 4 (Professional):** GATE PSUs (ONGC/IOCL), Teaching (CTET/KVS), AIIMS Nursing, State Judicial Services
5. **Tier 5 (Elite / Group A):** UPSC Civil Services (IAS/IPS), RBI Grade B, State PSC (SDM/DSP)

Fill out your age and education in the **Eligibility Finder** form to see all exams you qualify for!""",
        "suggested_actions": [
            "Use the 1-Minute Eligibility Finder tool",
            "Browse Urgent Deadlines"
        ]
    }
