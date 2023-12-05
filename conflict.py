import requests
from bs4 import BeautifulSoup
import logging
import re

# Setting up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_civil_conflict(country):
    """
    Check if a given country is currently in a civil conflict using Wikipedia and fetch details.
    
    Args:
    country (str): Name of the country to check.

    Returns:
    str: Detailed information about the civil conflict, if present.
    """

    # Format the Wikipedia URL for the given country
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        logging.info(f"Fetching information for {country} from Wikipedia.")
        # Get the Wikipedia page for the country
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Search for phrases indicating an active conflict
        conflict_phrases = [
            r"civil war", 
            r"armed conflict", 
            r"insurgency", 
            r"rebellion", 
            r"uprising",
            r"ongoing conflict",
            r"current conflict",
            r"conflict"
        ]

        # Combine the phrases into a single regex pattern
        pattern = '|'.join(conflict_phrases)

        # Search the entire text of the page for the pattern
        content_text = soup.get_text()
        if re.search(pattern, content_text, re.IGNORECASE):
            logging.info(f"Evidence of active conflict found in Wikipedia page for {country}.")
            # Attempt to extract the conflict details
            # [Your existing logic to extract conflict details goes here]
            return f"Evidence of active conflict found for {country}."
        
        logging.info(f"No evidence of active conflict found for {country}.")
        return f"No civil conflict currently reported in {country} on Wikipedia."
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching page: {e}")
        return f"An error occurred while fetching information: {e}"
    except Exception as e:
        logging.error(f"General error: {e}")
        return f"An error occurred: {e}"

# Example usage
check_civil_conflict("Israel")  # Example country known for recent conflicts

