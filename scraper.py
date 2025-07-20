from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def fetch_promoter_buying():
    # Set Chrome options for headless mode (no UI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Start Chrome with WebDriver Manager
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # Load page and wait for JS to render
    url = "https://www.tijorifinance.com/ideas-dashboard/promoter-buying/"
    driver.get(url)
    time.sleep(5)  # Wait for data to load (increase if needed)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = []
    cards = soup.find_all('div', {'class': 'MuiBox-root'})
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



