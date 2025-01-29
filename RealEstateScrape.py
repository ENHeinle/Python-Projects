import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# Function to scrape data from MLS listings
def scrape_data(url, max_retries=5):
    print(f"Fetching data from {url}")
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()  # Raise an HTTPError for bad responses
            break
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the webpage: {url}, Error: {e}")
            if response.status_code == 429:
                retries += 1
                wait_time = 2 ** retries
                print(f"Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Print the HTML content for debugging
    print(soup.prettify())
    
    # Defining the listing container to scrape necessary data
    data = []
    listings = soup.find_all('div', class_='listing-item')
    print(f"Found {len(listings)} listings")
    for listing in listings:
        try:
            price = int(listing.find('span', class_='price').text.strip().replace('$', '').replace(',', ''))
            bedrooms = listing.find('span', class_='bedrooms') or listing.find('span', class_='beds')
            bathrooms = listing.find('span', class_='bathrooms') or listing.find('span', class_='baths')
            if bedrooms:
                bedrooms = int(bedrooms.text.strip())
            if bathrooms:
                bathrooms = int(bathrooms.text.strip())
            garage = 'Yes' if listing.find('span', class_='garage') else 'No'
            listing_url = listing.find('a', class_='listing-link')['href']
            
            # Apply filters
            if bedrooms > 2 and bathrooms > 2 and price <= 500000:
                data.append({'price': price, 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'garage': garage, 'url': listing_url})
                print(f"Added listing: {price}, {bedrooms} bedrooms, {bathrooms} bathrooms, garage: {garage}, url: {listing_url}")
            else:
                print(f"Skipped listing: {price}, {bedrooms} bedrooms, {bathrooms} bathrooms, garage: {garage}, url: {listing_url}")
        except Exception as e:
            print(f"Error parsing listing: {e}")
    
    return data

# Function to save data to a spreadsheet
def save_to_spreadsheet(data, filename='real_estate_listings.xlsx'):
    if os.path.exists(filename):
        print(f"Appending data to existing file: {filename}")
        existing_data = pd.read_excel(filename)
        new_data = pd.DataFrame(data)
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        print(f"Creating new file: {filename}")
        combined_data = pd.DataFrame(data)
    
    combined_data.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

# Main execution
if __name__ == "__main__":
    url = "https://www.realtor.com/realestateandhomes-search/Allegheny-County_PA"
    listings = scrape_data(url)
    save_to_spreadsheet(listings, 'real_estate_listings.xlsx')