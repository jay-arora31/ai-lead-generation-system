"""
Lead Generation Automation System
Complete B2B lead generation for hardware computer store
"""
import argparse
from schemas.schemas import SearchCriteria
from services.apollo_service import ApolloService
from services.scraper_service import ScraperService
from services.ai_service import AIService
from services.hunter_service import HunterService
from pipeline.enrichment import LeadEnrichmentPipeline
from utils.config import load_config
from utils.logger import setup_logger
import sys

logger = setup_logger()

def create_search_criteria(args) -> SearchCriteria:
    """Create search criteria from command line arguments or defaults"""
    return SearchCriteria(
        size_range=args.size_range,
        industry=args.industry,
        location=args.location
    )

def main():
    """Main lead generation workflow"""
    parser = argparse.ArgumentParser(description='Lead Generation Automation for Hardware Store')
    parser.add_argument('--size-range', default='201-500', help='Company size range (e.g., 50-200)')
    parser.add_argument('--industry', default='hardware', help='Industry or keywords to search for')
    parser.add_argument('--location', default='india', help='Location to search in')
    parser.add_argument('--max-leads', type=int, default=10, help='Maximum number of leads to process')
    parser.add_argument('--output-file', help='Custom output filename')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting Lead Generation Automation System")
        logger.info(f"Search parameters: {args.size_range} employees, {args.industry}, {args.location}")
        
        # Load configuration
        config = load_config()
        
        # Initialize services
        logger.info("Initializing services...")
        apollo_service = ApolloService(api_key=config.apollo_api_key)
        scraper_service = ScraperService(openai_api_key=config.openai_api_key)
        ai_service = AIService(openai_api_key=config.openai_api_key)
        hunter_service = HunterService(api_key=config.hunter_api_key)
        
        # Create pipeline
        pipeline = LeadEnrichmentPipeline(
            apollo_service=apollo_service,
            scraper_service=scraper_service,
            ai_service=ai_service,
            hunter_service=hunter_service,
            config=config
        )
        
        # Create search criteria
        search_criteria = create_search_criteria(args)
        
        # Process leads
        logger.info("Starting lead enrichment pipeline...")
        leads = pipeline.process_leads(search_criteria, max_leads=args.max_leads)
        
        if not leads:
            logger.warning("No leads were generated")
            return
        
        # Display summary
        pipeline.display_leads_summary(leads)
        
        # Save results
        filename = pipeline.save_leads_to_file(leads, args.output_file)
        logger.info(f"Lead generation completed successfully!")
        logger.info(f"Generated {len(leads)} leads saved to: {filename}")
        
        # Show sample message
        if leads:
            print(f"\nSAMPLE PERSONALIZED MESSAGE:")
            print("=" * 60)
            print(leads[0].personalized_message)
        
    except Exception as e:
        logger.error(f"Lead generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
