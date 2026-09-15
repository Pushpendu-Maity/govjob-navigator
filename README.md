# 🏛️ GovJob Navigator – AI Government Job & Exam Eligibility Finder

A modern, responsive web application designed for Indian students and job seekers to evaluate their eligibility, discover active and upcoming exams, track application deadlines, and receive personalized career guidance across all career tiers (from 10th Pass entry-level to UPSC Group A elite).

---

## 🌟 Key Features

- **Multi-Tier Exam Database:** Over 25+ major Indian government examinations representing 2,50,000+ open vacancies across 5 career tiers:
  - **Tier 1 (10th/12th Pass):** India Post GDS (Direct Merit No Exam), SSC MTS, Railway Group D, State Police Constables, Forest Guard, CISF Tradesman, High Court Attendants.
  - **Tier 2 (ITI / Diploma):** Railway Assistant Loco Pilot (RRB ALP), RRB Technicians, SSC Junior Engineer (JE), DRDO CEPTAM.
  - **Tier 3 (Graduate General):** SSC CGL (Inspector, ASO, Auditor), IBPS PO & Clerk, SBI PO & Clerk, CDS Defense, State Police SI.
  - **Tier 4 (Professional):** GATE PSUs (ONGC, IOCL, NTPC), CTET Teaching, AIIMS Nursing Officer, State Judicial Services.
  - **Tier 5 (Group A Gazetted):** UPSC Civil Services (IAS/IPS/IFS), RBI Grade B, UPPSC PCS, UPSC Engineering Services (IES).
- **Deterministic Eligibility Engine:** 100% accurate rule verification with category-based age relaxation (OBC +3y, SC/ST +5y, PwD +10y, Ex-SM +3y), academic streams, and cutoff criteria.
- **Urgent Deadlines Tracker:** Real-time countdowns for closing dates with urgency alerts and "Add to Google Calendar" reminders.
- **AI Exam Counselor:** Natural language guidance for syllabus highlights, salary breakdown under 7th CPC (Basic Pay + DA + HRA), and exam comparisons.
- **Printable Eligibility Card:** Pre-styled official verification card exportable to PDF/Print.
- **Bookmarks & Alerts:** LocalStorage persistence for saving jobs and instant notification registration.

---

## 🚀 Quick Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Pushpendu-Maity/govjob-navigator.git
   cd govjob-navigator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

---

## ☁️ Deployment (Render / Railway / PythonAnywhere)

The repository includes `requirements.txt` and `Procfile` for one-click deployment on platforms like Render:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

---

## 📄 License
MIT License
