"""
Logging configuration
"""
import logging
import sys
def setup_logger():
    """
    Configure logging for the application
    """
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)  