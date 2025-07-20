from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def fetch_promoter_buying():
    # 1. Chrome options for maximum headless reliability
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")           # For newer Chrome (can also try "--headless" if problem)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    # Optional: add a "normal" user-agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

    # 2. Setup Selenium with chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://www.tijorifinance.com/ideas-dashboard/promoter-buying/"
    print(f"Loading {url} ...")
    driver.get(url)
    
    # 3. Wait longer, but check if data is present sooner
    max_wait = 25   # max seconds to wait for table data
    found_data = False

    for wait_time in range(5, max_wait+1, 2):
        time.sleep(2)
        html = driver.page_source
        # You can tune this string to something unique to the actual table/data when present
        if "MuiChip-label" in html or "promoter buying" in html.lower():
            found_data = True
            print(f"Data found in page HTML after {wait_time}s")
            break
        print(f"Still waiting... ({wait_time}s)")
    if not found_data:
        print("WARNING: Data table not found in page HTML after full wait!")

    # 4. Dump first 2000 chars of HTML for workflow log debugging
    print("="*25 + " PAGE HTML SAMPLE " + "="*25)
    print(driver.page_source[:2000])    # You can comment this out once your code works reliably
    print("="*62)

    # 5. Now parse as before:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = []
    cards = soup.find_all('div', {'class': 'MuiBox-root'})
    print(f"DEBUG: Found {len(cards)} potential company cards via MuiBox-root selector")
    for card in cards:
        title_elem = card.find('span', {'class': 'MuiTypography-root'})
        if not title_elem:
            continue
        company_name = title_elem.get_text(strip=True)
        ticker_elem = card.find('span', {'class': 'MuiTypography-caption'})
        ticker = ticker_elem.get_text(strip=True) if ticker_elem else ""
        chips = card.find_all("div", {"class": "MuiChip-label"})
        market_cap = ""
        sector = ""
        for chip in chips:
            label = chip.get_text()
            if 'cap' in label.lower():
                market_cap = label
            else:
                sector = label
        data.append({
            "company": company_name,
            "ticker": ticker,
            "market_cap": market_cap,
            "sector": sector
        })

    driver.quit()
    print(f"DEBUG: Returning {len(data)} companies")
    return data

if __name__ == "__main__":
    results = fetch_promoter_buying()
    scraped_data = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "promoter_buying": results
    }
    with open("promoter_buying.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(results)} promoter buying entries to promoter_buying.json")

