from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def fetch_promoter_buying():
    # --- Chrome options for headless, bot-resistant mode
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

    # --- Start Chrome with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://www.tijorifinance.com/ideas-dashboard/promoter-buying/"
    print(f"Loading {url} ...")
    driver.get(url)

    # --- Wait loop: check every 3 sec, up to max 25s
    max_wait = 25
    for waited in range(0, max_wait, 3):
        time.sleep(3)
        if "promoter buying" in driver.page_source.lower() or "Promoter Buying" in driver.page_source:
            print(f"🟢 Detected key text after {waited+3}s.")
            break
    else:
        print("🔴 Table data not detected after wait.")

    # --- Print a chunk of HTML for debug if needed
    print("="*20 + " HTML CHUNK " + "="*20)
    print(driver.page_source[:4000])  # Increase/decrease if needed
    print("="*20 + " END " + "="*20)

    # --- Now parse the table or company card structure
    soup = BeautifulSoup(driver.page_source, "html.parser")

    promoter_data = []

    # 🟩 Try main table-based scraping (Be adaptive: sites change structure!)
    table = soup.find('table')
    if table:
        print("🔎 Found TABLE element, using <tr> rows for parsing.")
        rows = table.find_all('tr')[1:]  # skip header row
        for row in rows:
            cells = row.find_all('td')
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
    else:
        # 🟦 Fallback for older card-based layout (may no longer be used)
        print("No <table> found, trying DIVs fallback...")
        # Replace the selector below if you inspect new classes!
        cards = soup.find_all('div', {'class': 'MuiBox-root'})
        print(f"Found {len(cards)} cards with selector 'MuiBox-root'")
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

    driver.quit()
    print(f"✅ Scraped {len(promoter_data)} promoter buying entries.")
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


