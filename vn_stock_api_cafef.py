from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

def scrape_cafef_vietnam_stock(ticker):
    try:
        url = f"https://s.cafef.vn/hose/{ticker.lower()}.chn"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        price_tag = soup.select_one("#content div.price div span#PriceQuote")
        price = float(price_tag.text.replace(",", "").strip()) if price_tag else None

        data = {"ticker": ticker.upper(), "price": price}
        valuation_table = soup.select_one("div#stock-valuation table")
        if not valuation_table:
            return {"error": "Valuation table not found"}

        for row in valuation_table.select("tr"):
            cells = row.select("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True).replace(",", "")
                if label == "EPS":
                    data["eps"] = float(value)
                elif "P/E" in label:
                    data["pe"] = float(value)
                elif "P/B" in label:
                    data["pb"] = float(value)

        if all(k in data for k in ["eps", "pe", "pb", "price"]):
            return data
        return {"error": f"Incomplete data for {ticker}", **data}
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
