import json
from datetime import datetime

try:
    import tijori  # Change this import if the library has a different name
except ImportError:
    print("Error: tijori library not found. Install it with 'pip install tijori'")
    exit(1)

def fetch_promoter_buying():
    try:
        # Function name may differ; check the library's docs for the correct one.
        data = tijori.promoter_buying()
        return data if data else []
    except Exception as e:
        print(f"Error fetching data from tijori: {e}")
        return []

if __name__ == "__main__":
    result = fetch_promoter_buying()
    output = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "promoter_buying": result
    }
    with open("promoter_buying.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(result)} promoter buying entries.")
