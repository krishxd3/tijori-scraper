from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def fetch_promoter_buying():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://www.tijorifinance.com/ideas-dashboard/promoter-buying/"
    print(f"Loading {url} ...")
    driver.get(url)

    # --- Optionally scroll & wait for lazy-load (some JS tables require this!)
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(18)  # Total wait ~22s, more than before

    # --- Dump a large chunk to logs for debugging!
    print("="*20, "PAGE HTML PREVIEW", "="*20)
    print(driver.page_source[:12000])  # Bada chunk for search/debug
    print("="*60)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    promoter_data = []

    # --- Try table-based scraping (use browser inspect to confirm):
    table = soup.find('table')
    if table:
        print("🔎 Found <table> tag, parsing rows...")
        rows = table.find_all('tr')[1:]  # skip thead/header
        for row in rows:
            cells = row.find_all('td')
            # Make sure table row is valid and looks like the expected data row
            if len(cells) >= 4:
                company = cells[0].get_text(strip=True)
                ticker = cells[1].get_text(strip=True)
                market_cap = cells[2].get_text(strip=True)
                sector = cells[3].get_text(strip=True)
                promoter_data.append({
                    "company": company,
                    "ticker": ticker,
                    "market_cap": market_cap,
                    "sector": sector
                })
        print(f"🟢 Parsed {len(promoter_data)} entries via table <tr>")
    else:
        # --- Fallback: Try card/div-based block (older layout/backup only)
        print("🔵 No <table> found, trying fallback card selectors...")
        cards = soup.find_all('div', {'class': 'MuiBox-root'})  # Update if needed
        print(f"DEBUG: Found {len(cards)} 'MuiBox-root' cards")
        for card in cards:
            title_elem = card.find('span', {'class': 'MuiTypography-root'})
            if not title_elem: continue
            company_name = title_elem.get_text(strip=True)
            ticker_elem = card.find('span', {'class': 'MuiTypography-caption'})
            ticker = ticker_elem.get_text(strip=True) if ticker_elem else ""
            chips = card.find_all("div", {"class": "MuiChip-label"})
            market_cap, sector = "", ""
            for chip in chips:
                label = chip.get_text()
                if 'cap' in label.lower():
                    market_cap = label
                else:
                    sector = label
            promoter_data.append({
                "company": company_name,
                "ticker": ticker,
                "market_cap": market_cap,
                "sector": sector
            })
        print(f"🟡 Parsed {len(promoter_data)} entries via fallback cards")

    driver.quit()
    print(f"✅ Final scraped {len(promoter_data)} promoter buying entries.")
    return promoter_data

if __name__ == "__main__":
    results = fetch_promoter_buying()
    scraped_at = datetime.now().isoformat() + "Z"
    scraped_data = {
        "scraped_at": scraped_at,
        "promoter_buying": results
    }
    with open("promoter_buying.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(results)} promoter buying entries to promoter_buying.json")



