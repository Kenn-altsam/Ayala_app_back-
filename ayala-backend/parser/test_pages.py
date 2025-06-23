from playwright.sync_api import sync_playwright
import time

def test_pages():
    """Test what's available on different pages"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Test pages 1-10 to see what's available
        for page_num in range(1, 11):
            url = f"https://statsnet.co/states/kz/almaty?page={page_num}"
            print(f"\n🔍 Testing page {page_num}: {url}")
            
            try:
                page.goto(url, timeout=30000)
                time.sleep(2)
                
                # Check for company elements
                company_elements = page.locator('li.flex.flex-col.border-b.py-2').all()
                print(f"   📋 Found {len(company_elements)} companies")
                
                if len(company_elements) == 0:
                    print(f"   🚫 No companies found on page {page_num}")
                    
                    # Check if page exists or shows error
                    page_title = page.title()
                    print(f"   📄 Page title: {page_title}")
                    
                    # Check for any error messages
                    try:
                        error_message = page.locator('text="404"').first
                        if error_message.count() > 0:
                            print(f"   ❌ 404 error detected on page {page_num}")
                    except:
                        pass
                    
                    # Check for "no results" type messages
                    try:
                        no_results = page.locator('text="не найдено"').first
                        if no_results.count() > 0:
                            print(f"   ❌ 'No results found' message detected")
                    except:
                        pass
                    
                    break
                else:
                    # Get first company name as sample
                    try:
                        first_company = company_elements[0].locator('h2').first.inner_text()
                        print(f"   📝 First company: {first_company[:50]}...")
                    except:
                        print(f"   📝 Could not get company name")
                        
            except Exception as e:
                print(f"   ❌ Error loading page {page_num}: {e}")
                break
        
        browser.close()

if __name__ == "__main__":
    test_pages() 