"""
Lead enrichment pipeline orchestration
Complete workflow from company search to personalized outreach messages
"""
import os
import json
import requests
from typing import List
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.schemas import SearchCriteria, Lead, Company
from services.apollo_service import ApolloService
from services.scraper_service import ScraperService, CompanyInsights
from services.ai_service import AIService, OutreachMessage
from services.hunter_service import HunterService, HunterError
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger()

class EnrichmentError(Exception):
    """Custom exception for pipeline errors"""
    pass

class LeadEnrichmentPipeline:
    def __init__(self, apollo_service: ApolloService, scraper_service: ScraperService, ai_service: AIService, hunter_service: HunterService, config: Config):
        self.apollo_service = apollo_service
        self.scraper_service = scraper_service
        self.ai_service = ai_service
        self.hunter_service = hunter_service
        self.config = config

    def process_leads(self, search_criteria: SearchCriteria, max_leads: int = 10) -> List[Lead]:
        """
        Main pipeline that orchestrates the entire lead enrichment flow
        
        Args:
            search_criteria: Company search parameters
            max_leads: Maximum number of leads to process
            
        Returns:
            List of enriched leads with personalized messages
        """
        logger.info("Starting lead generation pipeline...")
        logger.info(f"Search criteria: {search_criteria.size_range} employees, {search_criteria.industry}, {search_criteria.location}")
        
        enriched_leads = []
        
        try:
            # Step 1: Find companies using Apollo API
            logger.info("Step 1: Finding companies via Apollo API...")
            companies = self.apollo_service.find_companies(
                company_size=search_criteria.size_range,
                industry=search_criteria.industry,
                location=search_criteria.location
            )
            
            if not companies:
                logger.warning("No companies found matching criteria")
                return []
            
            logger.info(f"Found {len(companies)} companies")
            
            # Limit to max_leads for processing
            companies_to_process = companies[:max_leads]
            logger.info(f"Processing top {len(companies_to_process)} companies...")
            
            # Step 2 & 3: Scrape websites and generate messages for each company
            for i, company in enumerate(companies_to_process, 1):
                try:
                    logger.info(f"Processing company {i}/{len(companies_to_process)}: {company.name}")
                    
                    # Skip companies without websites
                    if not company.website:
                        logger.warning(f"No website found for {company.name}, skipping...")
                        continue
                    
                    # Step 2: Scrape company website for insights
                    logger.info(f"Analyzing website: {company.website}")
                    insights = self.scraper_service.scrape_website(company.website)
                    
                    # Step 3: Find contact information
                    logger.info("Finding contact information...")
                    contacts = []
                    try:
                        decision_makers = self.hunter_service.get_all_contacts(company.website)
                        contacts = [contact.model_dump() for contact in decision_makers]
                        if contacts:
                            logger.info(f"Found {len(contacts)} decision maker contacts")
                        else:
                            logger.info("No decision maker contacts found")
                    except HunterError as e:
                        logger.error(f"Hunter.io error: {e}")
                    except Exception as e:
                        logger.error(f"Contact search failed: {e}")
                    
                    # Step 4: Generate personalized message
                    logger.info("Generating personalized message...")
                    message = self.ai_service.generate_message(company, insights)
                    
                    # Create enriched lead
                    lead = Lead(
                        company=company,
                        insights=insights.model_dump(),  # Convert Pydantic to dict
                        personalized_message=message.format_email(),
                        contacts=contacts
                    )
                    
                    enriched_leads.append(lead)
                    logger.info(f"Successfully processed {company.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {company.name}: {str(e)}")
                    continue
            
            logger.info("Pipeline completed successfully!")
            logger.info(f"Generated {len(enriched_leads)} enriched leads")
            
            return enriched_leads
            
        except Exception as e:
            raise EnrichmentError(f"Pipeline failed: {str(e)}")

    def save_leads_to_file(self, leads: List[Lead], filename: str = None) -> str:
        """
        Save enriched leads to Google Sheets via Apps Script endpoint and/or local JSON file
        
        Args:
            leads: List of enriched leads
            filename: Optional custom filename for local backup
            
        Returns:
            Path to saved file or Google Sheets confirmation
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert leads to serializable format
        leads_data = []
        for lead in leads:
            # Extract contact emails for easier viewing in sheets
            contact_emails = []
            decision_makers = []
            if lead.contacts:
                for contact in lead.contacts:
                    email = contact.get('email', '')
                    if email:
                        contact_emails.append(email)
                        name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                        position = contact.get('position', '')
                        if name and position:
                            decision_makers.append(f"{name} ({position})")
                        elif name:
                            decision_makers.append(name)
                        elif position:
                            decision_makers.append(position)
            
            # Extract hardware opportunities
            hardware_needs = []
            if isinstance(lead.insights, dict):
                hardware_opportunity = lead.insights.get('hardware_opportunity', {})
                if hardware_opportunity.get('workstations'): hardware_needs.append('Workstations')
                if hardware_opportunity.get('servers'): hardware_needs.append('Servers')
                if hardware_opportunity.get('networking'): hardware_needs.append('Networking')
                if hardware_opportunity.get('storage'): hardware_needs.append('Storage')
                if hardware_opportunity.get('peripherals'): hardware_needs.append('Peripherals')
            
            lead_data = {
                "company_name": lead.company.name,
                "website": lead.company.website,
                "employee_count": lead.company.employee_count,
                "industry": lead.company.industry,
                "location": lead.company.location,
                "business_summary": lead.insights.get('business_summary', '') if isinstance(lead.insights, dict) else '',
                "hardware_opportunities": ', '.join(hardware_needs),
                "decision_maker_hint": lead.insights.get('decision_maker_hint', '') if isinstance(lead.insights, dict) else '',
                "contact_emails": ', '.join(contact_emails),
                "decision_makers": ', '.join(decision_makers),
                "personalized_message": lead.personalized_message,
                "generated_at": datetime.now().isoformat()
            }
            leads_data.append(lead_data)
        
        # Try to save to Google Sheets first
        google_sheets_success = False
        if self.config.google_sheets_endpoint:
            try:
                logger.info("Saving leads to Google Sheets...")
                google_sheets_success = self._save_to_google_sheets(leads_data)
                if google_sheets_success:
                    logger.info("Successfully saved leads to Google Sheets")
            except Exception as e:
                logger.error(f"Failed to save to Google Sheets: {str(e)}")
        
        # Always save local backup or primary storage if Google Sheets failed
        if not filename:
            filename = f"data/output/leads_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert back to full format for local JSON
        full_leads_data = []
        for lead in leads:
            lead_data = {
                "company": {
                    "name": lead.company.name,
                    "website": lead.company.website,
                    "employee_count": lead.company.employee_count,
                    "industry": lead.company.industry,
                    "location": lead.company.location
                },
                "insights": lead.insights,
                "personalized_message": lead.personalized_message,
                "contacts": lead.contacts or [],
                "generated_at": datetime.now().isoformat()
            }
            full_leads_data.append(lead_data)
        
        # Save to local file
        with open(filename, 'w') as f:
            json.dump(full_leads_data, f, indent=2)
        
        if google_sheets_success:
            logger.info(f"Local backup saved to: {filename}")
            return "Google Sheets + Local Backup"
        else:
            logger.info(f"Leads saved to: {filename}")
            return filename
    
    def _save_to_google_sheets(self, leads_data: List[dict]) -> bool:
        """
        Send leads data to Google Sheets via Apps Script endpoint
        
        Args:
            leads_data: Formatted leads data for Google Sheets
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.google_sheets_endpoint:
            return False
        
        try:
            # Prepare the payload for Google Apps Script
            payload = {
                "action": "addLeads",
                "data": leads_data
            }
            
            # Send POST request to Google Apps Script
            response = requests.post(
                self.config.google_sheets_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    logger.info(f"Successfully added {len(leads_data)} leads to Google Sheets")
                    return True
                else:
                    logger.error(f"Google Sheets API returned error: {result.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Google Sheets API returned status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while connecting to Google Sheets")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while saving to Google Sheets: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while saving to Google Sheets: {str(e)}")
            return False

    def display_leads_summary(self, leads: List[Lead]):
        """
        Display a summary of generated leads
        """
        if not leads:
            logger.info("No leads to display")
            return
        
        logger.info("LEAD GENERATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Leads Generated: {len(leads)}")
        
        for i, lead in enumerate(leads, 1):
            logger.info(f"Lead {i}: {lead.company.name}")
            logger.info(f"  Industry: {lead.company.industry}")
            logger.info(f"  Size: {lead.company.employee_count} employees")
            logger.info(f"  Website: {lead.company.website}")
            
            # Extract key insights
            insights = lead.insights
            if isinstance(insights, dict):
                business_summary = insights.get('business_summary', 'N/A')
                hardware_needs = insights.get('hardware_opportunity', {})
                
                logger.info(f"  Business: {business_summary}")
                
                # Show hardware opportunities
                needs = []
                if hardware_needs.get('workstations'): needs.append('Workstations')
                if hardware_needs.get('servers'): needs.append('Servers')
                if hardware_needs.get('networking'): needs.append('Networking')
                if hardware_needs.get('storage'): needs.append('Storage')
                if hardware_needs.get('peripherals'): needs.append('Peripherals')
                
                if needs:
                    logger.info(f"  Hardware Opportunities: {', '.join(needs)}")
                else:
                    logger.info(f"  Hardware Opportunities: General IT needs")
            
            logger.info(f"  Message Subject: {self._extract_subject_line(lead.personalized_message)}")
            
            # Show contact information
            if lead.contacts:
                logger.info("  Decision Maker Contacts:")
                for contact in lead.contacts[:3]:  # Show top 3
                    email = contact.get('email', 'N/A')
                    name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                    position = contact.get('position', 'N/A')
                    logger.info(f"    - {email} - {name} ({position})")
            else:
                logger.info("  Decision Maker Contacts: None found")
            
            logger.info("-" * 40)

    def _extract_subject_line(self, email_message: str) -> str:                                                                                                                                                                                                                                                                                                                                                             
        """Extract subject line from formatted email"""
        lines = email_message.split('\n')
        for line in lines:
            if line.startswith('Subject:'):
                return line.replace('Subject:', '').strip()
        return "N/A"
