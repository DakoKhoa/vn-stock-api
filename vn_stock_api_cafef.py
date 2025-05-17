
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

def safe_float(value):
    try:
        return float(value)
    except:
        return None

def scrape_cafef_vietnam_stock(ticker):
    try:
        url = f"https://cafef.vn/du-lieu/HOSE/{ticker.upper()}.chn"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract price from <div class="current-price"><strong>80.00</strong></div>
        price_tag = soup.select_one("div.current-price > strong")
        price = safe_float(price_tag.text.replace(",", "").strip()) if price_tag else None

        data = {"ticker": ticker.upper(), "price": price}

        # Basic mock fallback for EPS/PE/PB
        data["eps"] = 3000
        data["pe"] = 10.5
        data["pb"] = 1.7

        return data if price else {"error": "Price not found", **data}

    except Exception as e:
        return {"error": str(e)}

@app.route("/vietnam", methods=["GET"])
def get_vn():
    ticker = request.args.get("ticker", "").upper()
    result = scrape_cafef_vietnam_stock(ticker)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
