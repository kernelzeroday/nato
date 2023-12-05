#!/usr/bin/env python3
import argparse
import datetime
import logging
import requests
from bs4 import BeautifulSoup
import re
from colored import fg, attr
from nltk.tokenize import sent_tokenize, word_tokenize
import textwrap



# Configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




# Static data for NATO and BRICS membership status
nato_countries = {
    "AL": "Member", "BE": "Member", "BG": "Member", "CA": "Member",
    "HR": "Member", "CZ": "Member", "DK": "Member", "EE": "Member",
    "FR": "Member", "DE": "Member", "GR": "Member", "HU": "Member",
    "IS": "Member", "IT": "Member", "LV": "Member", "LT": "Member",
    "LU": "Member", "NL": "Member", "NO": "Member", "PL": "Member",
    "PT": "Member", "RO": "Member", "SK": "Member", "SI": "Member",
    "ES": "Member", "TR": "Member", "GB": "Member", "US": "Member",
    "MK": "Member", "ME": "Member", "FI": "Member"  # Including Finland
}

brics_countries = ["BR", "RU", "IN", "CN", "ZA", "EG", "ET", "IR", "SA", "AE"]  # Including new members effective 2024


def check_civil_conflict(country):
    """
    Check if a given country is currently in a civil conflict using Wikipedia.
    """
    # [Previous setup code, if any]

    # Format the Wikipedia URL for the given country
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        # Fetch the Wikipedia page for the country
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the current year
        current_year = datetime.datetime.now().year

        # Convert the entire Wikipedia page text into a string
        content_text = soup.get_text()

        # Tokenize the text into sentences
        sentences = sent_tokenize(content_text)

        # Define conflict-related keywords
        conflict_keywords = ["war", "conflict", "insurgency", "rebellion", "uprising"]

        # Search each sentence for the current year and conflict keywords
        for sentence in sentences:
            words = word_tokenize(sentence)
            year_positions = [i for i, word in enumerate(words) if str(current_year) in word]
            keyword_positions = [i for i, word in enumerate(words) if any(keyword in word.lower() for keyword in conflict_keywords)]

            # Check the proximity of year and keyword
            for year_pos in year_positions:
                for keyword_pos in keyword_positions:
                    if abs(year_pos - keyword_pos) <= 10:  # Adjust the proximity limit as needed
                        # Wrap the sentence to 80 characters
                        wrapped_sentence = textwrap.fill(sentence, width=80)
                        return f"Potential recent conflict found:\n{wrapped_sentence}"

        return f"No recent conflicts found for {country} in {current_year}."
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching page: {e}")
        return f"An error occurred while fetching information: {e}"
    except Exception as e:
        logging.error(f"General error: {e}")
        return f"An error occurred: {e}"




def get_country_info(code):
    """
    Fetch country information with case-insensitive code handling.
    """
    url = f"https://restcountries.com/v2/alpha/{code}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        return None

    data = response.json()

    # Assign colors to each field
    color_name = fg('white')
    color_region = fg('light_red')  # Changed from magenta to grey
    color_subregion = fg('cyan')
    color_population = fg('light_green')
    color_languages = fg('light_yellow')
    color_currencies = fg('light_cyan')

    # Format population with commas
    population_formatted = f"{int(data.get('population', 0)):,}"

    # Check and specify Chinese language variants
    languages = data.get('languages', [])
    for lang in languages:
        if lang['iso639_1'] == 'zh':
            lang['name'] = 'Mandarin/Cantonese'  # Assuming Mandarin/Cantonese for Chinese

    country_info = {
        'Country Name': f"{color_name}{data.get('name')}{attr('reset')}",
        'Region': f"{color_region}{data.get('region')}{attr('reset')}",
        'Subregion': f"{color_subregion}{data.get('subregion')}{attr('reset')}",
        'Population': f"{color_population}{population_formatted}{attr('reset')}",
        'Languages': f"{color_languages}{', '.join([lang['name'] for lang in languages])}{attr('reset')}",
        'Currencies': f"{color_currencies}{', '.join([currency['name'] for currency in data.get('currencies', [])])}{attr('reset')}",
    }
    code_upper = code.upper()  # Normalize code to uppercase

    # Determine membership status with updated color scheme
    if code_upper in nato_countries:
        membership_status = "NATO Member"
        color = fg('green')
    elif code_upper in brics_countries:
        membership_status = "BRICS Member"
        color = fg('red')
    else:
        membership_status = "Neither"
        color = fg('yellow')

    country_info['Membership Status'] = f"{color}{membership_status}{attr('reset')}"
    country_name = data.get('name')  # Assuming 'name' is present in the API response
    conflict_info = check_civil_conflict(country_name)
    country_info['Civil Conflict'] = conflict_info


    return country_info

def main():
    """
    Main execution function with argument parsing.
    """
    parser = argparse.ArgumentParser(description='Get information about a country')
    parser.add_argument('code', type=str, help='Two-letter country code')
    args = parser.parse_args()

    code_normalized = args.code.upper()  # Normalize input code to uppercase
    logging.info(f"Fetching information for country code: {code_normalized}")
    info = get_country_info(code_normalized)

    if info:
        print("\nCountry Information:")
        print("-" * 50)
        for key, value in info.items():
            print(f"{key.ljust(20)}: {value}")
        print("-" * 50)
    else:
        print("No information found for the given code.")

if __name__ == "__main__":
    main()

