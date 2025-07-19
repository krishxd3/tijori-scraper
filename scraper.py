from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_promoter_buying():
    print("Fetching promoter buying data from Tijori Finance...")
    session = HTMLSession()
    try:
        response = session.get("https://www.tijorifinance.com/ideas-dashboard/promoter-buying/")
        response.html.render(timeout=30, sleep=3)

        soup = BeautifulSoup(response.html.html, "html.parser")
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

        return data
    except Exception as e:
        print("Error during scraping:", str(e))
        return []

if __name__ == "__main__":
    results = fetch_promoter_buying()
    scraped_data = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "promoter_buying": results
    }
    with open("promoter_buying.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(results)} promoter buying entries to promoter_buying.json")


