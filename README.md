# AI Lead Generation Automation System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![Apollo](https://img.shields.io/badge/Apollo-API-orange.svg)](https://apollo.io/)
[![Hunter.io](https://img.shields.io/badge/Hunter.io-API-red.svg)](https://hunter.io/)
[![Google Sheets](https://img.shields.io/badge/Google-Sheets-34A853.svg)](https://sheets.google.com/)

## Assignment Overview

The system demonstrates:

- **Backend API/Script** with command-line interface
- **Apollo API Integration** for company discovery  
- **AI-Powered Website Scraping** for business insights
- **Personalized Message Generation** using OpenAI
- **Google Sheets Integration** for data management
- **Hardware Store B2B Use Case** implementation

## Key Features

### **Core Functionality**
- **Company Discovery**: Uses Apollo API to find companies matching specific criteria
- **AI Website Analysis**: Extracts key business insights and hardware needs using OpenAI
- **Contact Finding**: Integrates Hunter.io to find decision-maker email addresses  
- **Smart Message Generation**: Creates personalized B2B outreach emails with company-specific details
- **Google Sheets Integration**: Automatically saves leads to organized spreadsheets
- **Command Line Interface**: Easy-to-use CLI with flexible parameters

### **Bonus Features Implemented**
- **Email Validation & Contact Finding** via Hunter.io API
- **Lead Deduplication Logic** built into the pipeline
- **Error Handling & Retry Mechanisms** with exponential backoff
- **Configuration Management** with environment variables
- **Clean, Well-Structured Code** with comprehensive documentation
- **Professional Testing Suite** with integration tests

## Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Apollo API    │    │   OpenAI API    │    │   Hunter.io     │
│ (Lead Discovery)│    │ (AI Scraping &  │    │ (Contact Info)  │
│                 │    │  Message Gen)   │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────┬───────────┴──────────────────────┘
                     │
         ┌───────────▼────────────┐
         │  Lead Enrichment       │
         │     Pipeline           │
         │  (Python Backend)      │
         └───────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼───┐    ┌───────▼────────┐   ┌───▼──────────┐
│ JSON  │    │ Google Sheets  │   │   Console    │
│ Files │    │ (via Apps      │   │   Output     │
│       │    │  Script API)   │   │              │
└───────┘    └────────────────┘   └──────────────┘
```

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-lead-generation-system.git
cd ai-lead-generation-system

# Install dependencies using uv
uv pip install -e .
uv sync
```

### 2. Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
APOLLO_API_KEY=your_apollo_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HUNTER_API_KEY=your_hunter_api_key_here
GOOGLE_SHEETS_ENDPOINT=https://script.google.com/macros/s/AKfycbyP1yj-uIE_0P7DiwbgnyBTMJFkDYF6E0mZ8X8dmRkMskYGDEZLzi-qgvle6tAe6Vkpdw/exec
```

### 3. Google Apps Script Setup

To enable automatic data saving to Google Sheets, you need to deploy the provided Apps Script:

1. **Create a new Google Sheets document** for your leads data
2. **Copy the Sheet ID** from your Google Sheets URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
   ```
3. **Set up Google Apps Script**:
   - In your Google Sheets, go to `Extensions > Apps Script`
   - Replace the default code with the contents of `google_apps_script.js` from this repository
   - Update the `SHEET_ID` variable with your actual Google Sheets ID
   - Save the script with a meaningful name

4. **Deploy as Web App**:
   - Click `Deploy > New deployment`
   - Choose type: `Web app`
   - Execute as: `Me`
   - Who has access: `Anyone`
   - Click `Deploy` and authorize permissions

5. **Update Environment Variables**:
   - Copy the deployment URL and set it as `GOOGLE_SHEETS_ENDPOINT` in your `.env` file
   - The format will be: `https://script.google.com/macros/s/[SCRIPT_ID]/exec`

**Note:** The `google_apps_script.js` file contains the complete server-side code needed to receive lead data and automatically organize it in your spreadsheet with proper formatting and headers.

### 4. Run Lead Generation
```bash
# Basic usage - hardware companies in India, 250-500 employees

uv run main.py

# Custom parameters
uv run main.py --industry "hardware" --size-range "201-500" --location "India" --max-leads 5


```

## Demo Output

**Live Demo Spreadsheet:** [View Generated Leads](https://docs.google.com/spreadsheets/d/1kZdi7Fxr-sg_IYqTCjnMVsCsowM-mzHfhAJ_kX4iJqo/edit?gid=0#gid=0)

**Google Apps Script Endpoint:** [https://script.google.com/macros/s/AKfycbyP1yj-uIE_0P7DiwbgnyBTMJFkDYF6E0mZ8X8dmRkMskYGDEZLzi-qgvle6tAe6Vkpdw/exec](https://script.google.com/macros/s/AKfycbyP1yj-uIE_0P7DiwbgnyBTMJFkDYF6E0mZ8X8dmRkMskYGDEZLzi-qgvle6tAe6Vkpdw/exec)

### Console Output
```
Starting Lead Generation Automation System
Search parameters: 250-500 employees, hardware, india

Step 1: Finding companies via Apollo API...
Found 25 companies
Processing top 5 companies...

Processing company 1/5: Pentoz Technology
  Analyzing website: https://www.pentoz.com
  Finding contact information...
    Found 5 decision maker contacts
  Generating personalized message...
  Successfully processed Pentoz Technology

Leads saved to Google Sheets successfully!
Local backup saved to: data/output/leads_20250125_143045.json

LEAD GENERATION SUMMARY
============================================================
Total Leads Generated: 5

Lead 1: Pentoz Technology
  Industry: Information Technology & Services
  Size: 250 employees
  Website: https://www.pentoz.com
  Business: Technology company providing on-demand talent for AI, cloud, and cybersecurity
  Hardware Opportunities: Workstations, Servers, Networking, Storage, Peripherals
  Decision Maker Contacts:
    - saradha@pentoz.com - Saradha M P (Co-Founder) - 99% confidence
    - hello@pentoz.com - General Contact (Support) - 90% confidence
```

### Generated Personalized Message
```
Subject: Empowering Pentoz's Tech Solutions with Our Hardware

Hi Saradha,

I hope this message finds you well. I've been following Pentoz's commitment to 
empowering Indian talent while delivering elite technology solutions globally. 
Your focus on scaling technology solutions in AI, cloud, and cybersecurity is 
truly impressive.

To support your innovative projects, we specialize in high-performance 
workstations and servers that can handle intensive workloads, ensuring your 
team remains productive and efficient. Our modern peripherals and networking 
solutions are designed to enhance remote work capabilities, aligning perfectly 
with your workforce's tech-savvy nature.

I'd love to discuss how our desktop computers, robust storage solutions, and 
advanced networking equipment can address your current challenges and help you 
stay ahead in the competitive landscape.

Would you be open to a brief consultation next week to explore how we can 
support Pentoz's growth?

Best regards,
[Your Name]
Hardware Solutions Specialist
[Your Hardware Store Name]
[Phone] | [Email]
```

## Project Structure

```
ai-lead-generation-system/
├── services/              # External API integrations
│   ├── apollo_service.py     # Apollo API client
│   ├── scraper_service.py    # AI-powered web scraping
│   ├── ai_service.py         # OpenAI message generation
│   └── hunter_service.py     # Contact finding
├── pipeline/              # Lead processing pipeline
│   └── enrichment.py         # Main orchestration logic
├── schemas/               # Data models & validation
│   └── schemas.py            # Pydantic/dataclass models
├── utils/                 # Configuration & utilities
│   ├── config.py             # Environment management
│   └── logger.py             # Logging setup
├── data/                  # Output directories
│   ├── output/               # Generated lead files
├── main.py                # CLI entry point
├── google_apps_script.js  # Google Sheets integration
├── pyproject.toml         # Dependencies
└── README.md              # This file
```

## API Integrations

### **Apollo API** - Lead Discovery
- Finds companies matching search criteria
- Filters by size, industry, location
- Returns enriched company data

### **OpenAI API** - AI Analysis & Generation  
- Website content analysis and insight extraction
- Business need identification for hardware opportunities
- Personalized message generation with company context

### **Hunter.io API** - Contact Information
- Decision-maker email discovery
- Contact verification and confidence scoring
- Department and role identification

### **Google Apps Script** - Data Management
- Automatic spreadsheet creation and formatting  
- Real-time data synchronization
- Team collaboration features


