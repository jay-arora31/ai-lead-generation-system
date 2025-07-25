"""
Apollo API integration for lead generation
"""
from typing import List, Optional
import os
import json
from dotenv import load_dotenv
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas.schemas import Company
from utils.logger import setup_logger

logger = setup_logger()

class ApolloApiError(Exception):
    """Custom exception for Apollo API errors"""
    pass

class ApolloService:
    BASE_URL = "https://api.apollo.io/api/v1"
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": api_key
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=lambda x: isinstance(x, (requests.exceptions.RequestException, ApolloApiError))
    )
    def find_companies(
        self, 
        company_size: str,
        industry: str,
        location: Optional[str] = None
    ) -> List[Company]:
        """
        Find companies matching the given criteria using Apollo API
        
        Args:
            company_size: Size range (e.g., "50-200")
            industry: Industry type (will be used as keyword)
            location: Optional location filter
            
        Returns:
            List of Company objects matching the criteria
            
        Raises:
            ApolloApiError: If API request fails
        """
        try:
            # Parse company size range
            size_min, size_max = map(int, company_size.split("-"))
            size_range = f"{size_min},{size_max}"
            
            # Build API query
            payload = {
                "organization_num_employees_ranges": [size_range],
                "q_organization_keyword_tags": [industry],
                "page": 1,
                "per_page": 25
            }
            
            if location:
                payload["organization_locations"] = [location]
            
            try:
                logger.info(f"Sending request to Apollo API with payload: {json.dumps(payload, indent=2)}")
                response = self.session.post(
                    f"{self.BASE_URL}/organizations/search",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                if "organizations" not in data:
                    error_msg = data.get("error", "Unexpected API response format")
                    raise ApolloApiError(f"Apollo API error: {error_msg}")
                    
                # Transform API response to Company objects
                companies = []
                for org in data.get("organizations", []):
                    try:
                        company = Company(
                            name=org["name"],
                            website=org.get("website_url", ""),
                            employee_count=org.get("estimated_num_employees", 0),
                            industry=org.get("industry", ""),
                            location=f"{org.get('city', '')}, {org.get('state', '')}, {org.get('country', '')}"
                        )
                        companies.append(company)
                    except KeyError as e:
                        logger.warning(f"Warning: Skipping company due to missing data: {e}")
                        continue
                    
                return companies
                
            except requests.exceptions.RequestException as e:
                raise ApolloApiError(f"Apollo API request failed: {str(e)}")
            except (KeyError, ValueError) as e:
                raise ApolloApiError(f"Error parsing Apollo API response: {str(e)}")
                
        except ValueError as e:
            raise ValueError(f"Invalid company size format. Expected format: 'min-max', got: {company_size}")

    def enrich_company(self, domain: str) -> dict:
        """
        Get detailed information about a specific company
        
        Args:
            domain: Company website domain
            
        Returns:
            Dictionary containing enriched company data
            
        Raises:
            ApolloApiError: If API request fails
        """
        try:
            response = self.session.post(
                f"{self.BASE_URL}/organizations/enrich",
                json={
                    "domain": domain
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if "organization" not in data:
                error_msg = data.get("error", "Unexpected API response format")
                raise ApolloApiError(f"Apollo API error: {error_msg}")
                
            return data["organization"]
            
        except requests.exceptions.RequestException as e:
            raise ApolloApiError(f"Apollo API enrichment failed: {str(e)}")
        except (KeyError, ValueError) as e:
            raise ApolloApiError(f"Error parsing Apollo API enrichment response: {str(e)}")
