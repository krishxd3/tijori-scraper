import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

TIJORI_URL = "https://www.tijorifinance.com/ideas-dashboard/promoter-buying/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; scraper for promoter buying)"
}

def fetch_promoter_buying():
    r = requests.get(TIJORI_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

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
        mc, sector = "", ""
        for chip in chips:
            label = chip.get_text()
            if 'cap' in label.lower():
                mc = label
            else:
                sector = label
        data.append({
            "company": company_name,
            "ticker": ticker,
            "market_cap": mc,
            "sector": sector
        })
    return data

if __name__ == "__main__":
    results = fetch_promoter_buying()
    output = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "promoter_buying": results
    }
    with open("promoter_buying.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(results)} promoter buying entries.")

