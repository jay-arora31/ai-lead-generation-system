"""
AI-powered web scraping service for extracting company insights
Focused on hardware computer store B2B sales opportunities
"""
import re
import os
import json
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from utils.logger import setup_logger
logger = setup_logger()

# Simplified Pydantic models for focused insights
class HardwareNeeds(BaseModel):
    workstations: bool = Field(default=False, description="Needs desktop computers/workstations")
    servers: bool = Field(default=False, description="Needs servers or data center equipment")
    networking: bool = Field(default=False, description="Needs networking equipment")
    storage: bool = Field(default=False, description="Needs storage solutions")
    peripherals: bool = Field(default=False, description="Needs printers, monitors, etc.")

class CompanyInsights(BaseModel):
    """Focused insights for hardware computer store sales"""
    business_summary: str = Field(description="One sentence: what the company does")
    company_size_indicator: str = Field(description="small/medium/large based on website signals")
    key_insights: List[str] = Field(description="2-3 key business insights for personalized outreach", max_length=3)
    hardware_opportunity: HardwareNeeds = Field(default_factory=HardwareNeeds, description="Specific hardware needs identified")
    decision_maker_hint: str = Field(default="", description="Who likely makes IT purchasing decisions")
    personalization_hook: str = Field(description="One specific detail for personalized messaging")

class ScraperError(Exception):
    """Custom exception for scraping errors"""
    pass

class ScraperService:
    def __init__(self, openai_api_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.openai_client = OpenAI(api_key=openai_api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=lambda x: isinstance(x, (requests.exceptions.RequestException, ScraperError))
    )
    def scrape_website(self, url: str) -> CompanyInsights:
        """
        Scrape company website and extract 2-3 key insights for hardware sales
        
        Args:
            url: Company website URL
            
        Returns:
            CompanyInsights with focused business intelligence
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            logger.info(f"Analyzing website: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get clean text content
            text_content = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text for faster processing
            max_chars = 6000
            if len(clean_text) > max_chars:
                clean_text = clean_text[:max_chars] + "..."
            
            insights = self._analyze_with_ai(clean_text, url)
            
            return insights
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return self._get_fallback_insights(url)
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            return self._get_fallback_insights(url)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=3, max=10),
        retry=lambda x: isinstance(x, (Exception,)) and not isinstance(x, (json.JSONDecodeError, ValidationError))
    )
    def _analyze_with_ai(self, content: str, url: str) -> CompanyInsights:
        """
        Use AI to extract focused business insights for hardware sales
        """
        prompt = f"""
        You are a sales analyst for a hardware computer store. Analyze this company website to identify B2B sales opportunities.

        Website: {url}
        Content: {content}

        Extract exactly these insights in JSON format:
        {{
            "business_summary": "One clear sentence describing what this company does",
            "company_size_indicator": "small/medium/large (based on mentions of employees, offices, scale)",
            "key_insights": [
                "2-3 specific business insights that would help personalize a hardware sales pitch",
                "Focus on: growth signals, tech challenges, office setup, team size, current tech stack"
            ],
            "hardware_opportunity": {{
                "workstations": true/false,
                "servers": true/false, 
                "networking": true/false,
                "storage": true/false,
                "peripherals": true/false
            }},
            "decision_maker_hint": "Who likely makes IT purchasing decisions (IT Manager, CTO, Operations, etc.)",
            "personalization_hook": "One specific detail about the company for personalized messaging"
        }}

        Focus on:
        - Signs they might need new computers, servers, or IT equipment
        - Growth indicators (hiring, expanding, new offices)
        - Technology pain points or outdated systems
        - Company culture/values for relationship building

        Return only valid JSON, no other text.
        """

        try:
            logger.debug(f"Sending AI analysis request for {url}")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a B2B sales analyst for a hardware computer store. Provide concise, actionable insights for sales outreach. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            raw_response = response.choices[0].message.content
            logger.debug(f"AI response received for {url}")
            
            insights_data = json.loads(raw_response)
            insights = CompanyInsights(**insights_data)
            
            logger.info(f"Successfully analyzed {url} with AI")
            return insights
            
        except json.JSONDecodeError as e:
            logger.error(f"AI returned invalid JSON for {url}: {e}")
            return self._get_fallback_insights(url)
        except ValidationError as e:
            logger.error(f"AI response validation failed for {url}: {e}")
            return self._get_fallback_insights(url)
        except Exception as e:
            logger.warning(f"AI analysis attempt failed for {url}: {e}, retrying...")
            raise  # This will trigger the retry mechanism

    def _get_fallback_insights(self, url: str) -> CompanyInsights:
        """Return basic insights when AI analysis fails"""
        logger.warning(f"Using fallback insights for {url}")
        return CompanyInsights(
            business_summary="Company details could not be analyzed from website",
            company_size_indicator="unknown",
            key_insights=[
                "Website analysis was unsuccessful",
                "Manual research recommended",
                "Basic contact information may be available"
            ],
            hardware_opportunity=HardwareNeeds(),
            decision_maker_hint="General Manager or IT contact",
            personalization_hook="Professional services company"
        )

