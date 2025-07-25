# Lead Generation Automation System

A complete B2B lead generation automation system designed for hardware computer store owners to find potential business clients and generate personalized outreach messages.

## 🎯 Features

- **Company Discovery**: Uses Apollo API to find companies matching specific criteria
- **AI-Powered Website Analysis**: Extracts key business insights and hardware needs
- **Contact Finding**: Uses Hunter.io to find decision-maker email addresses
- **Personalized Message Generation**: Creates tailored B2B outreach emails
- **Google Sheets Integration**: Automatically saves leads to organized spreadsheets
- **Complete Pipeline**: Automated workflow from search to personalized messages
- **Professional Output**: Clean, structured data ready for sales outreach

## 🔧 Setup

### 1. Environment Setup

```bash
# Clone or download the project
cd lead-generation-system

# Install dependencies using uv
uv pip install -e .
```

### 2. API Keys Configuration

Create a `.env` file in the project root:

```bash
# Apollo API credentials
APOLLO_API_KEY=your_apollo_api_key_here

# OpenAI API credentials for message generation
OPENAI_API_KEY=your_openai_api_key_here

# Hunter.io API credentials for contact finding
HUNTER_API_KEY=your_hunter_api_key_here

# Google Sheets Apps Script endpoint URL (optional)
# Get this from your Google Apps Script deployment
GOOGLE_SHEETS_ENDPOINT=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec

# Optional: Configure output directory
OUTPUT_DIR=data/output

# Optional: Configure logging level
LOG_LEVEL=INFO
```

### 3. Get API Keys

- **Apollo API**: Sign up at [Apollo.io](https://apollo.io) for lead generation
- **OpenAI API**: Get your key from [OpenAI Platform](https://platform.openai.com)
- **Hunter.io API**: Get your key from [Hunter.io](https://hunter.io) for contact finding

### 4. Setup Google Sheets Integration (Optional)

The system can automatically save leads to Google Sheets via Google Apps Script:

1. **Create a Google Sheets document** for your leads
2. **Copy the Google Sheets ID** from the URL (the long string between `/d/` and `/edit`)
3. **Set up Google Apps Script**:
   - In your Google Sheets, go to `Extensions > Apps Script`
   - Replace the default code with the contents of `google_apps_script.js`
   - Update the `SHEET_ID` variable with your Google Sheets ID
   - Save the script
4. **Deploy as Web App**:
   - Click `Deploy > New deployment`
   - Choose type: `Web app`
   - Execute as: `Me`
   - Who has access: `Anyone`
   - Click `Deploy` and authorize permissions
5. **Copy the deployment URL** and set it as `GOOGLE_SHEETS_ENDPOINT` in your `.env` file

**Benefits of Google Sheets Integration:**
- ✅ Automatic data saving to organized spreadsheet
- ✅ Easy sharing with team members
- ✅ Built-in data visualization and filtering
- ✅ Real-time collaboration on lead management

## 🚀 Usage

### Basic Usage

```bash
# Run with default settings (hardware companies, 250-500 employees, India)
uv run main.py

# Custom search parameters
uv run main.py --industry "software" --size-range "50-200" --location "United States"

# Limit number of leads processed
uv run main.py --max-leads 5

# Custom output file
uv run main.py --output-file "my_leads.json"
```

### Command Line Options

```bash
--size-range     Company size range (e.g., "50-200", "250-500")
--industry       Industry or keywords to search for
--location       Geographic location to search in
--max-leads      Maximum number of leads to process (default: 10)
--output-file    Custom output filename
```

### Example Output

```
Starting Lead Generation Automation System
Search parameters: 250-500 employees, hardware, india

Step 1: Finding companies via Apollo API...
Found 25 companies
Processing top 5 companies...

Processing company 1/5: Pentoz Technology
  Analyzing website: https://www.pentoz.com
  Generating personalized message...
  Successfully processed Pentoz Technology

LEAD GENERATION SUMMARY
============================================================
Total Leads Generated: 5

Lead 1: Pentoz Technology
  Industry: Information Technology
  Size: 250 employees
  Website: https://www.pentoz.com
  Business: Technology company specializing in mobile app development
  Hardware Opportunities: Workstations, Servers, Networking
  Message Subject: IT Infrastructure Solutions for Your Growing Tech Team

SAMPLE PERSONALIZED MESSAGE:
============================================================
Subject: IT Infrastructure Solutions for Your Growing Tech Team

Hello IT Manager,

I came across Pentoz Technology and was impressed by your innovative mobile 
app development work. With 250+ employees and focus on emerging technologies, 
I imagine your team needs reliable, high-performance computing infrastructure.

We specialize in providing businesses with enterprise-grade workstations, 
servers, and networking equipment that can handle demanding development 
workloads while staying within budget.

Would you be open to a brief 15-minute call to discuss how we can support 
your technology infrastructure needs?

Best regards,
[Your Name]
Hardware Solutions Specialist
```

## 📁 Project Structure

```
.
├── services/           # External service integrations
│   ├── apollo_service.py    # Apollo API integration
│   ├── scraper_service.py   # AI-powered web scraping
│   └── ai_service.py        # AI message generation
├── models/            # Data models and schemas
├── utils/             # Configuration and logging
├── pipeline/          # Lead enrichment pipeline
├── tests/             # Test files
├── data/output/       # Generated leads and messages
├── main.py           # Main entry point
└── README.md         # Documentation
```

## 🔍 Testing Individual Components

### Test Apollo API Integration
```bash
uv run services/apollo_service.py
```

### Test Website Scraping
```bash
uv run services/scraper_service.py
```

### Test AI Message Generation
```bash
uv run services/ai_service.py
```

### Test Complete Pipeline
```bash
uv run pipeline/enrichment.py
```

## 📊 Output Format

The system saves data in two formats:

### Google Sheets Format (when configured)
Data is automatically organized in a spreadsheet with columns:
- Timestamp, Company Name, Website, Employee Count, Industry, Location
- Business Summary, Hardware Opportunities, Decision Maker Hint
- Contact Emails, Decision Makers, Personalized Message

### JSON File Format (local backup)
The system also generates a JSON file with the following structure:

```json
[
  {
    "company": {
      "name": "Company Name",
      "website": "https://company.com",
      "employee_count": 250,
      "industry": "Technology",
      "location": "City, State, Country"
    },
    "insights": {
      "business_summary": "What the company does",
      "company_size_indicator": "medium",
      "key_insights": ["insight 1", "insight 2", "insight 3"],
      "hardware_opportunity": {
        "workstations": true,
        "servers": true,
        "networking": false,
        "storage": false,
        "peripherals": true
      },
      "decision_maker_hint": "IT Manager",
      "personalization_hook": "Specific company detail"
    },
    "personalized_message": "Complete formatted email message",
    "generated_at": "2024-01-15T10:30:00"
  }
]
```

## 🎯 Use Cases

- **Hardware Store Owners**: Find B2B clients needing IT equipment
- **Sales Teams**: Generate personalized outreach at scale
- **Business Development**: Identify companies with specific hardware needs
- **Market Research**: Analyze company technology requirements

## ⚡ Performance Notes

- Processes 5-10 leads in approximately 2-3 minutes
- Includes retry mechanisms for API reliability
- Respects rate limits for external services
- Generates detailed business insights for each lead

## 🔧 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure both Apollo and OpenAI API keys are set in `.env`
2. **Rate Limits**: Reduce `--max-leads` if hitting API limits
3. **Website Access**: Some sites may block scraping; this is handled gracefully
4. **JSON Parsing**: AI responses are validated; fallbacks provided for errors

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## 📝 License

This project is for educational and business use. Ensure compliance with Apollo and OpenAI terms of service.
