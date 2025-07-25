"""
AI service for generating personalized B2B outreach messages
Focused on hardware computer store sales
"""
import os
from typing import Dict, List, Optional
from openai import OpenAI
from pydantic import BaseModel, Field
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas.schemas import Company
from utils.logger import setup_logger
# Import scraper models for type hints
from services.scraper_service import CompanyInsights, HardwareNeeds

class OutreachMessage(BaseModel):
    """Structured outreach message for B2B sales"""
    subject_line: str = Field(description="Compelling email subject line")
    greeting: str = Field(description="Personalized greeting")
    opening: str = Field(description="Opening paragraph with personalization")
    value_proposition: str = Field(description="Main value proposition for hardware solutions")
    specific_offer: str = Field(description="Specific hardware solutions offered")
    call_to_action: str = Field(description="Clear next step")
    closing: str = Field(description="Professional closing")
    
    def format_email(self) -> str:
        """Format as a complete email"""
        return f"""Subject: {self.subject_line}

{self.greeting}

{self.opening}

{self.value_proposition}

{self.specific_offer}

{self.call_to_action}

{self.closing}

Best regards,
Jay Arora
Hardware Solutions Specialist
NewTech Computers
+1 (619) 200-0000 | jay@newtechcomputers.com"""

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass

class AIService:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.logger = setup_logger()
    def generate_message(self, company: Company, insights: CompanyInsights) -> OutreachMessage:
        """
        Generate personalized outreach message for hardware sales
        
        Args:
            company: Company information from Apollo
            insights: Website insights from scraper
            
        Returns:
            OutreachMessage with personalized B2B outreach
        """
        try:
            hardware_needs = self._summarize_hardware_needs(insights.hardware_opportunity)
            
            prompt = f"""
            You are writing a personalized B2B sales email for a hardware computer store owner reaching out to a potential business client.

            COMPANY INFORMATION:
            - Company Name: {company.name}
            - Industry: {company.industry}
            - Size: {company.employee_count} employees ({insights.company_size_indicator})
            - Website: {company.website}
            - Location: {company.location}

            BUSINESS INSIGHTS:
            - What they do: {insights.business_summary}
            - Key insights: {', '.join(insights.key_insights)}
            - Decision maker: {insights.decision_maker_hint}
            - Personalization hook: {insights.personalization_hook}
            - Hardware opportunities: {hardware_needs}

            Write a professional B2B outreach email in JSON format:
            {{
                "subject_line": "Compelling subject that references their business (max 60 chars)",
                "greeting": "Personalized greeting using decision maker hint",
                "opening": "Opening paragraph that shows you researched them, reference specific insights",
                "value_proposition": "How your hardware solutions solve their specific challenges",
                "specific_offer": "Concrete hardware solutions based on their identified needs",
                "call_to_action": "Clear, low-pressure next step (consultation, demo, quote)",
                "closing": "Professional closing that reinforces value"
            }}

            GUIDELINES:
            - Keep it concise (under 200 words total)
            - Reference specific details from their business
            - Focus on business value, not technical specs
            - Professional but friendly tone
            - Avoid being pushy or salesy
            - Include specific hardware solutions they likely need

            Return only valid JSON, no other text.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert B2B sales copywriter specializing in hardware solutions. Write personalized, professional outreach emails that build relationships and provide value. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
            )

            import json
            raw_response = response.choices[0].message.content
            message_data = json.loads(raw_response)
            message = OutreachMessage(**message_data)
            
            return message

        except json.JSONDecodeError as e:
            self.logger.error(f"AI returned invalid JSON: {e}")
            return self._get_fallback_message(company, insights)
        except Exception as e:
            self.logger.error(f"AI message generation failed: {e}")
            return self._get_fallback_message(company, insights)

    def _summarize_hardware_needs(self, hardware: HardwareNeeds) -> str:
        """Convert hardware needs to readable summary"""
        needs = []
        if hardware.workstations:
            needs.append("desktop computers/workstations")
        if hardware.servers:
            needs.append("servers")
        if hardware.networking:
            needs.append("networking equipment")
        if hardware.storage:
            needs.append("storage solutions")
        if hardware.peripherals:
            needs.append("peripherals")
        
        if not needs:
            return "general IT hardware needs"
        
        return ", ".join(needs)

    def _get_fallback_message(self, company: Company, insights: CompanyInsights) -> OutreachMessage:
        """Generate a basic fallback message when AI fails"""
        return OutreachMessage(
            subject_line=f"Hardware Solutions for {company.name}",
            greeting=f"Hello {insights.decision_maker_hint or 'there'},",
            opening=f"I came across {company.name} and was impressed by your work in {company.industry}.",
            value_proposition="As a growing business, having reliable IT infrastructure is crucial for your continued success.",
            specific_offer="We specialize in providing businesses like yours with quality computers, servers, and networking equipment at competitive prices.",
            call_to_action="Would you be open to a brief 15-minute call to discuss your current IT needs?",
            closing="I'd love to learn more about your business and see how we can support your technology requirements."
        )
