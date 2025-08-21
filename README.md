Mercor Airtable Multi Table Form and JSON Automation

Scope
This implements the assignment requirements using local Python scripts and Airtable REST API. It covers JSON compression and decompression, auto shortlist rules, and LLM evaluation with retries and token guardrails. See the original task for details.

Prerequisites
1. Python 3.10 or newer
2. Airtable base created with these tables and fields exactly:
   Applicants: Applicant ID primary key, Compressed JSON long text, JSON Hash single line text, Shortlist Status single select, LLM Summary long text, LLM Score number, LLM Follow Ups long text
   Personal Details: Applicant ID link to Applicants, Full Name, Email, Location, LinkedIn
   Work Experience: Applicant ID link to Applicants, Company, Title, Start ISO date, End ISO date or empty for current, Technologies comma separated
   Salary Preferences: Applicant ID link to Applicants, Preferred Rate number, Minimum Rate number, Currency single select, Availability number hours per week
   Shortlisted Leads: Applicant link to Applicants, Compressed JSON long text, Score Reason long text, Created At created time
   All child tables link back to Applicants by Applicant ID as described. 

Env setup
Copy .env.example to .env and fill in values.

Install
pip install -r requirements.txt

CLI usage
python -m app.main compress --applicant APP123
python -m app.main compress_all
python -m app.main decompress --applicant APP123
python -m app.main shortlist --applicant APP123
python -m app.main shortlist_all
python -m app.main llm --applicant APP123
python -m app.main llm_all
python -m app.main run_all --applicant APP123
python -m app.main run_all_all

