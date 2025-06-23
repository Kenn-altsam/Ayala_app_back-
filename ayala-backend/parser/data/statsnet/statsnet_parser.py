from playwright.sync_api import sync_playwright
import csv
import time
import os
import re
from typing import List, Dict
from urllib.parse import urljoin
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Proxy configuration
PROXIES = [
    {
        'server': 'http://94.131.2.254:30068',
        'username': 'NuhaiProxy_VP3eYoUt',
        'password': 'Vh0VvZE9'
    },
    {
        'server': 'http://62.109.14.189:30484',
        'username': 'NuhaiProxy_Kj0cdbMp',
        'password': 'fkfkPV6W'
    }
]

def get_next_proxy():
    """Returns the next proxy from the list"""
    return random.choice(PROXIES)

def create_browser_context(playwright, proxy_config):
    """Creates a new browser context with proxy"""
    try:
        browser = playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ],
            proxy={
                'server': proxy_config['server'],
                'username': proxy_config['username'],
                'password': proxy_config['password']
            }
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        return browser, context
    except Exception as e:
        print(f"Error creating browser context with proxy {proxy_config['server']}: {e}")
        return None, None

def get_region_links(page):
    """Gets all region links from the main page"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempt {retry_count + 1} to get region links...")
            page.goto("https://statsnet.co/states/kz", wait_until='networkidle', timeout=60000)
            time.sleep(5)
            
            region_elements = page.locator('a[href^="/states/kz/"]').all()
            region_links = []
            
            for element in region_elements:
                href = element.get_attribute('href')
                if href and href != "/states/kz":
                    region_links.append({
                        'url': f"https://statsnet.co{href}",
                        'name': element.inner_text().strip()
                    })
            
            if region_links:
                print(f"Successfully found {len(region_links)} regions")
                return region_links
                
        except Exception as e:
            print(f"Error getting region links (attempt {retry_count + 1}): {e}")
            retry_count += 1
            if retry_count < max_retries:
                print("Retrying with different proxy...")
                time.sleep(5)
                return None
            
    print("Failed to get region links after all retries")
    return None

def parse_company_data(company_element):
    """Parses data from a single company element"""
    company = {}
    
    try:
        # Name
        name_element = company_element.locator('h2').first
        company['name'] = name_element.inner_text().strip() if name_element.count() > 0 else ""
        
        # Address
        addr_element = company_element.locator('p.text-sm').first
        company['address'] = addr_element.inner_text().strip() if addr_element.count() > 0 else ""
        
        # Activity
        activity_elements = company_element.locator('div.text-sm.gap-1').all()
        for activity_div in activity_elements:
            activity_text = activity_div.inner_text().strip()
            if activity_text and "чел." not in activity_text and "предприятие" not in activity_text:
                company['activity'] = activity_text
                break
        
        # Manager
        manager_element = company_element.locator('p.text-sm.text-statsnet').first
        if manager_element.count() > 0:
            manager_text = manager_element.inner_text().strip()
            if "— руководитель" in manager_text:
                company['manager'] = manager_text.split("—")[0].strip()
        
        # Company size
        size_elements = company_element.locator('p.text-sm.text-gray-500').all()
        for element in size_elements:
            text = element.inner_text().strip()
            if "предприятие" in text:
                company['company_size'] = text
                break
        
        # BIN
        bin_element = company_element.locator('span.text-sm.text-gray-500').first
        if bin_element.count() > 0:
            bin_text = bin_element.inner_text().strip()
            if "БИН" in bin_text:
                company['bin'] = bin_text.replace("БИН", "").strip()
        
        # Status
        status_element = company_element.locator('span.ui-status').first
        if status_element.count() > 0:
            status_class = status_element.get_attribute('class')
            company['status'] = "Активная" if "ui-status--green" in status_class else "Неактивная"
        
        # Link
        link_element = company_element.locator('a[href]').first
        if link_element.count() > 0:
            href = link_element.get_attribute('href')
            if href:
                company['link'] = f"https://statsnet.co{href}"
        
    except Exception as e:
        print(f"Error parsing company data: {e}")
    
    return company

def get_companies_from_region(playwright, region_url, region_name):
    """Gets all companies from a specific region"""
    companies = []
    page_num = 1
    total_companies = 0
    max_retries = 3
    
    while True:
        print(f"\nProcessing page {page_num} of {region_name}...")
        
        # Create new browser context with fresh proxy for each page
        proxy_config = get_next_proxy()
        browser, context = create_browser_context(playwright, proxy_config)
        
        if not browser or not context:
            print("Failed to create browser context, trying another proxy...")
            time.sleep(5)
            continue
            
        page = context.new_page()
        retry_count = 0
        page_processed = False
        
        while retry_count < max_retries and not page_processed:
            try:
                # Form page URL
                page_url = f"{region_url}?page={page_num}" if page_num > 1 else region_url
                print(f"Using proxy: {proxy_config['server']}")
                
                # Load page
                page.goto(page_url, wait_until='networkidle', timeout=60000)
                time.sleep(5)
                
                # Wait for company elements
                page.wait_for_selector('li.flex.flex-col.border-b.py-2', timeout=30000)
                
                # Get all company elements
                company_elements = page.locator('li.flex.flex-col.border-b.py-2').all()
                
                if not company_elements:
                    print("No more companies found")
                    browser.close()
                    return total_companies
                
                print(f"Found {len(company_elements)} companies on page {page_num}")
                
                # Parse each company
                for element in company_elements:
                    try:
                        company_data = parse_company_data(element)
                        if company_data and company_data.get('name'):
                            companies.append(company_data)
                            total_companies += 1
                            print(f"Added company: {company_data['name'][:50]}...")
                    except Exception as e:
                        print(f"Error parsing company: {e}")
                        continue
                
                page_processed = True
                
                # Save progress every 50 companies
                if len(companies) >= 50:
                    save_to_csv(companies, f"data/{region_name.lower()}_companies_{total_companies}.csv")
                    companies = []
                
            except Exception as e:
                print(f"Error processing page (attempt {retry_count + 1}): {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print("Retrying with different proxy...")
                    time.sleep(5)
                    # Try with another proxy
                    browser.close()
                    proxy_config = get_next_proxy()
                    browser, context = create_browser_context(playwright, proxy_config)
                    if browser and context:
                        page = context.new_page()
                    else:
                        continue
            
        if not page_processed:
            print(f"Failed to process page {page_num} after all retries")
            browser.close()
            return total_companies
        
        browser.close()
        page_num += 1
        time.sleep(3)
        
        # Limit to 50 pages for safety
        if page_num > 50:
            print("Reached page limit (50)")
            return total_companies
    
    return total_companies

def save_to_csv(companies, filename):
    """Saves company data to a CSV file"""
    os.makedirs('data', exist_ok=True)
    
    fieldnames = ['name', 'address', 'activity', 'manager', 'company_size', 'bin', 'status', 'link']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(companies)
    
    print(f"Data saved to {filename}")
    print(f"Total companies in this batch: {len(companies)}")

def merge_region_files(region_name):
    """Merges all CSV files for a region into one"""
    import glob
    
    pattern = f"data/{region_name.lower()}_companies_*.csv"
    files = glob.glob(pattern)
    
    if not files:
        return
    
    all_companies = []
    fieldnames = ['name', 'address', 'activity', 'manager', 'company_size', 'bin', 'status', 'link']
    
    for file in sorted(files):
        with open(file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            all_companies.extend(list(reader))
    
    output_file = f"data/{region_name.lower()}_all_companies.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_companies)
    
    print(f"Merged {len(files)} files into {output_file}")
    print(f"Total companies: {len(all_companies)}")
    
    # Clean up individual files
    for file in files:
        os.remove(file)

def main():
    with sync_playwright() as p:
        while True:
            # Get initial proxy
            proxy_config = get_next_proxy()
            browser, context = create_browser_context(p, proxy_config)
            
            if not browser or not context:
                print("Failed to create initial browser context, trying another proxy...")
                time.sleep(5)
                continue
                
            page = context.new_page()
            
            try:
                # Get all region links
                print("Getting region links...")
                region_links = get_region_links(page)
                
                if not region_links:
                    print("Failed to get region links, retrying with different proxy...")
                    browser.close()
                    continue
                
                print(f"Found {len(region_links)} regions")
                browser.close()
                
                # Process each region
                for region in region_links:
                    print(f"\nProcessing region: {region['name']}")
                    print(f"URL: {region['url']}")
                    
                    total_companies = get_companies_from_region(p, region['url'], region['name'])
                    print(f"Finished processing {region['name']}, total companies: {total_companies}")
                    
                    # Merge files for this region
                    merge_region_files(region['name'])
                    
                    # Short delay between regions
                    time.sleep(5)
                
                break  # Success, exit the loop
                
            except Exception as e:
                print(f"Critical error: {e}")
                browser.close()
                time.sleep(5)
                continue

if __name__ == "__main__":
    main() 