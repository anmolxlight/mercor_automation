# Mercor Airtable Automation

A comprehensive automation system for managing applicant data in Airtable with JSON compression, automated shortlisting, and AI-powered candidate evaluation.

## Features

- **Data Compression**: Convert multi-table applicant data into compressed JSON format
- **Automated Shortlisting**: Rule-based candidate filtering with detailed reasoning
- **AI Evaluation**: LLM-powered candidate summaries and scoring using Google Gemini
- **Data Integrity**: SHA-256 hash verification for data consistency
- **Batch Processing**: Support for single applicant or bulk operations
- **CLI Interface**: Comprehensive command-line tools for all operations

## Architecture

The system operates on five interconnected Airtable tables:
- **Applicants** (Primary table with compressed data and AI insights)
- **Personal Details** (Contact information and location)
- **Work Experience** (Employment history and technologies)
- **Salary Preferences** (Rate expectations and availability)
- **Shortlisted Leads** (Approved candidates with reasoning)

## Prerequisites

- Python 3.10 or newer
- Airtable account with API access
- Google AI API key for Gemini access

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/anmolxlight/mercor_automation.git
   cd mercor_automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API credentials:
   ```env
   AIRTABLE_API_KEY=your_airtable_api_key
   AIRTABLE_BASE_ID=your_base_id
   LLM_PROVIDER=your_gemini_api_key
   ```

## Airtable Database Schema

Create an Airtable base with these exact table structures:

### Applicants Table
- **Applicant ID** (Primary Key): Unique identifier
- **Compressed JSON** (Long Text): Serialized applicant data
- **JSON Hash** (Single Line Text): SHA-256 integrity hash
- **Shortlist Status** (Single Select): Current status
- **LLM Summary** (Long Text): AI-generated summary
- **LLM Score** (Number): Quality score (1-10)
- **LLM Follow Ups** (Long Text): Suggested questions

### Personal Details Table
- **Applicant ID** (Link to Applicants): Foreign key
- **Full Name** (Single Line Text): Candidate name
- **Email** (Email): Contact email
- **Location** (Single Line Text): Geographic location
- **LinkedIn** (URL): LinkedIn profile

### Work Experience Table
- **Applicant ID** (Link to Applicants): Foreign key
- **Company** (Single Line Text): Employer name
- **Title** (Single Line Text): Job position
- **Start** (Date): Employment start date (ISO format)
- **End** (Date): Employment end date (empty for current)
- **Technologies** (Single Line Text): Comma-separated skills

### Salary Preferences Table
- **Applicant ID** (Link to Applicants): Foreign key
- **Preferred Rate** (Number): Desired hourly rate
- **Minimum Rate** (Number): Minimum acceptable rate
- **Currency** (Single Select): Currency denomination
- **Availability** (Number): Hours per week

### Shortlisted Leads Table
- **Applicant** (Link to Applicants): Reference to candidate
- **Compressed JSON** (Long Text): Data snapshot
- **Score Reason** (Long Text): Shortlisting reasoning
- **Created At** (Created Time): Automatic timestamp

## Usage

### Single Applicant Operations

```bash
# Compress applicant data into JSON
python -m app.main compress --applicant APP123

# Decompress JSON back to relational tables
python -m app.main decompress --applicant APP123

# Apply shortlisting rules
python -m app.main shortlist --applicant APP123

# Generate AI evaluation
python -m app.main llm --applicant APP123

# Run complete pipeline
python -m app.main run_all --applicant APP123
```

### Batch Operations

```bash
# Process all applicants
python -m app.main compress_all
python -m app.main shortlist_all
python -m app.main llm_all
python -m app.main run_all_all
```

## Shortlisting Criteria

Candidates are automatically evaluated based on:

1. **Experience**: 4+ years OR Tier 1 company experience
2. **Compensation**: ≤$100/hour preferred rate AND ≥20 hours/week availability
3. **Location**: Must be in target countries (US, Canada, UK, Germany, India, Spain)

## Configuration

Customize business rules via environment variables:

```env
# Tier 1 Companies (comma-separated)
TIER1_COMPANIES=Google,Meta,OpenAI,Microsoft,Apple,Amazon,NVIDIA

# Target Countries (comma-separated)
TARGET_COUNTRIES=United States,Canada,United Kingdom,Germany,India,Spain

# LLM Settings
LLM_MAX_TOKENS=400
LLM_RETRY_MAX=3
```

## Project Structure

```
mercor_automation/
├── app/
│   ├── main.py          # CLI interface and orchestration
│   ├── airtable.py      # Airtable API integration
│   ├── compressor.py    # JSON compression logic
│   ├── decompressor.py  # JSON decompression logic
│   ├── shortlist.py     # Automated shortlisting engine
│   ├── llm.py          # AI integration (Gemini)
│   ├── config.py       # Configuration management
│   ├── schema.py       # Database schema definitions
│   └── util.py         # Utility functions
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md          # This file
```

## Error Handling

The system includes comprehensive error handling:
- Automatic retry with exponential backoff for API failures
- Graceful degradation when optional operations fail
- Detailed logging for debugging
- Data integrity verification via hash checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for the Mercor technical assessment.

