
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

def scrape_cafef_accurate(ticker):
    try:
        url = f"https://cafef.vn/du-lieu/hose/{ticker.lower()}.chn"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract price
        price_tag = soup.select_one("div.r_block_left span.price")
        price = safe_float(price_tag.text.replace(",", "").strip()) if price_tag else None

        data = {"ticker": ticker.upper(), "price": price}

        # Extract EPS, PE, PB from <li> blocks
        info_section = soup.select("div.v_box li")
        for li in info_section:
            text = li.get_text(strip=True)
            if "EPS cơ bản" in text:
                value = li.find("strong")
                data["eps"] = safe_float(value.text.strip()) if value else None
            elif "P/E" in text:
                value = li.find("strong")
                data["pe"] = safe_float(value.text.strip()) if value else None
            elif "P/B" in text:
                value = li.find("strong")
                data["pb"] = safe_float(value.text.strip()) if value else None

        if all(k in data and data[k] is not None for k in ["price", "eps", "pe", "pb"]):
            return data
        else:
            return {"error": "Some fields missing", **data}

    except Exception as e:
        return {"error": str(e)}

@app.route("/vietnam", methods=["GET"])
def get_vn():
    ticker = request.args.get("ticker", "").upper()
    result = scrape_cafef_accurate(ticker)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
