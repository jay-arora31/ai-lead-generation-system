"""
Hunter.io API integration for finding contact information
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field
from utils.logger import setup_logger

logger = setup_logger()

class ContactInfo(BaseModel):
    """Contact information from Hunter.io"""
    email: str = Field(description="Email address")
    first_name: Optional[str] = Field(default="", description="First name")
    last_name: Optional[str] = Field(default="", description="Last name")
    position: Optional[str] = Field(default="", description="Job title/position")
    department: Optional[str] = Field(default="", description="Department")

    verified: bool = Field(default=False, description="Email verification status")

class DomainSearchResult(BaseModel):
    """Domain search results from Hunter.io"""
    domain: str = Field(description="Domain searched")
    organization: str = Field(default="", description="Organization name")
    emails: List[ContactInfo] = Field(default_factory=list, description="Found email addresses")
    total_emails: int = Field(default=0, description="Total emails found")

class HunterError(Exception):
    """Custom exception for Hunter.io API errors"""
    pass

class HunterService:
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=lambda x: isinstance(x, (requests.exceptions.RequestException, HunterError))
    )
    def find_emails_by_domain(self, domain: str, limit: int = 10) -> DomainSearchResult:
        """
        Find email addresses for a given domain
        
        Args:
            domain: Company domain (e.g., "company.com")
            limit: Maximum number of emails to return
            
        Returns:
            DomainSearchResult with found contact information
        """
        try:
            # Clean domain (remove http/https and www)
            clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            logger.debug(f"Searching emails for domain: {clean_domain}")
            
            params = {
                'domain': clean_domain,
                'api_key': self.api_key,
            }
            
            response = self.session.get(f"{self.BASE_URL}/domain-search", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errors'):
                raise HunterError(f"Hunter API error: {data['errors']}")
            
            # Parse response
            domain_data = data.get('data', {})
            emails_data = domain_data.get('emails', [])
            
            # Convert to ContactInfo objects
            contacts = []
            for email_data in emails_data:
                contact = ContactInfo(
                    email=email_data.get('value', ''),
                    first_name=email_data.get('first_name') or '',
                    last_name=email_data.get('last_name') or '',
                    position=email_data.get('position') or '',
                    department=email_data.get('department') or '',
                    verified=email_data.get('verification', {}).get('result') == 'deliverable'
                )
                contacts.append(contact)
            
            result = DomainSearchResult(
                domain=clean_domain,
                organization=domain_data.get('organization', ''),
                emails=contacts,
                total_emails=len(contacts)
            )
            
            logger.info(f"Found {len(contacts)} emails for {clean_domain}")
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise HunterError("Invalid Hunter.io API key")
            elif e.response.status_code == 429:
                raise HunterError("Hunter.io API rate limit exceeded")
            else:
                raise HunterError(f"Hunter.io API error: {e}")
        except requests.exceptions.RequestException as e:
            raise HunterError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=lambda x: isinstance(x, (requests.exceptions.RequestException, HunterError))
    )
    def find_email(self, domain: str, first_name: str, last_name: str) -> Optional[ContactInfo]:
        """
        Find specific person's email address
        
        Args:
            domain: Company domain
            first_name: Person's first name
            last_name: Person's last name
            
        Returns:
            ContactInfo if found, None otherwise
        """
        try:
            clean_domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
            
            logger.debug(f"Finding email for {first_name} {last_name} at {clean_domain}")
            
            params = {
                'domain': clean_domain,
                'first_name': first_name,
                'last_name': last_name,
                'api_key': self.api_key
            }
            
            response = self.session.get(f"{self.BASE_URL}/email-finder", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errors'):
                logger.warning(f"Hunter API error for {first_name} {last_name}: {data['errors']}")
                return None
            
            email_data = data.get('data', {})
            if not email_data.get('email'):
                logger.info(f"No email found for {first_name} {last_name} at {clean_domain}")
                return None
            
            contact = ContactInfo(
                email=email_data.get('email', ''),
                first_name=email_data.get('first_name', first_name),
                last_name=email_data.get('last_name', last_name),
                position=email_data.get('position', ''),
                verified=email_data.get('verification', {}).get('result') == 'deliverable'
            )
            
            logger.info(f"Found email for {first_name} {last_name}: {contact.email}")
            return contact
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.info(f"No email found for {first_name} {last_name} at {clean_domain}")
                return None
            else:
                raise HunterError(f"Hunter.io API error: {e}")
        except requests.exceptions.RequestException as e:
            raise HunterError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=lambda x: isinstance(x, (requests.exceptions.RequestException, HunterError))
    )
    def verify_email(self, email: str) -> Dict[str, any]:
        """
        Verify if an email address is valid and deliverable
        
        Args:
            email: Email address to verify
            
        Returns:
            Dictionary with verification results
        """
        try:
            logger.debug(f"Verifying email: {email}")
            
            params = {
                'email': email,
                'api_key': self.api_key
            }
            
            response = self.session.get(f"{self.BASE_URL}/email-verifier", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errors'):
                raise HunterError(f"Hunter API error: {data['errors']}")
            
            verification_data = data.get('data', {})
            
            result = {
                'email': email,
                'result': verification_data.get('result', 'unknown'),
                'score': verification_data.get('score', 0),
                'regexp': verification_data.get('regexp', False),
                'gibberish': verification_data.get('gibberish', False),
                'disposable': verification_data.get('disposable', False),
                'webmail': verification_data.get('webmail', False),
                'mx_records': verification_data.get('mx_records', False),
                'smtp_server': verification_data.get('smtp_server', False),
                'smtp_check': verification_data.get('smtp_check', False),
                'accept_all': verification_data.get('accept_all', False),
                'block': verification_data.get('block', False)
            }
            
            logger.info(f"Email verification for {email}: {result['result']} (score: {result['score']})")
            return result
            
        except requests.exceptions.RequestException as e:
            raise HunterError(f"Network error: {str(e)}")

    def get_all_contacts(self, domain: str) -> List[ContactInfo]:
        """
        Get all email contacts for a domain
        
        Args:
            domain: Company domain
            
        Returns:
            List of all ContactInfo found
        """
        try:
            # Get all emails for the domain
            domain_result = self.find_emails_by_domain(domain, limit=25)
            
            # Get all contacts
            all_contacts = []
            for contact in domain_result.emails:
                all_contacts.append(contact)
                logger.debug(f"Added contact: {contact.email} - {contact.position}")
            
            logger.info(f"Found {len(all_contacts)} contacts for {domain}")
            return all_contacts
            
        except Exception as e:
            logger.error(f"Error finding contacts for {domain}: {e}")
            return []

def main():
    """Test the Hunter.io service"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    hunter_api_key = os.getenv("HUNTER_API_KEY")
    if not hunter_api_key:
        logger.error("HUNTER_API_KEY not found in environment variables")
        return
    
    hunter_service = HunterService(api_key=hunter_api_key)
    
    # Test domains
    test_domains = [
        "pentoz.com",
        "mindstix.com"
    ]
    
    logger.info("HUNTER.IO CONTACT DISCOVERY TEST")
    logger.info("=" * 50)
    
    for domain in test_domains:
        try:
            logger.info(f"Searching contacts for: {domain}")
            
            # Find all contacts
            all_contacts = hunter_service.get_all_contacts(domain)
            
            if all_contacts:
                logger.info(f"Found {len(all_contacts)} contacts:")
                for contact in all_contacts:
                    logger.info(f"  • {contact.email}")
                    logger.info(f"    Name: {contact.first_name} {contact.last_name}")
                    logger.info(f"    Position: {contact.position}")
        
                    logger.info(f"    Verified: {contact.verified}")
            else:
                logger.info("No contacts found")
            
            logger.info("-" * 40)
            
        except Exception as e:
            logger.error(f"Error processing {domain}: {e}")

if __name__ == "__main__":
    main() 