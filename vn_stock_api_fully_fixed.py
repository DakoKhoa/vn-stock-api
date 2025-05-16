from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Simulated dynamic Vietnam stock data source
def get_mock_vn_data(ticker):
    # Just simulate some behavior based on suffix or prefix
    base_data = {
        "eps": 4000,
        "pe": 11.5,
        "pb": 1.3,
        "price": 36000
    }
    if not ticker.endswith(".VN"):
        return None
    # simulate different price by hashing
    unique_offset = sum([ord(c) for c in ticker]) % 1000
    base_data["price"] += unique_offset
    return { "ticker": ticker, **base_data }

@app.route("/vietnam", methods=["GET"])
def get_vn_stock():
    ticker = request.args.get("ticker", "").upper()
    data = get_mock_vn_data(ticker)
    if not data:
        return jsonify({"error": f"No data found for {ticker}"}), 404
    return jsonify(data)

@app.route("/global", methods=["GET"])
def get_global_stock():
    ticker = request.args.get("ticker", "").upper()
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics,financialData,price"
    try:
        r = requests.get(url)
        data = r.json()
        res = data.get("quoteSummary", {}).get("result", [{}])[0]

        eps = res.get("defaultKeyStatistics", {}).get("trailingEps", {}).get("raw")
        pe = res.get("defaultKeyStatistics", {}).get("trailingPE", {}).get("raw")
        pb = res.get("defaultKeyStatistics", {}).get("priceToBook", {}).get("raw")
        price = res.get("price", {}).get("regularMarketPrice", {}).get("raw")

        if None in (eps, pe, pb, price):
            return jsonify({"error": "Missing global data"}), 400

        return jsonify({ "ticker": ticker, "eps": eps, "pe": pe, "pb": pb, "price": price })

    except Exception as e:
        return jsonify({"error": f"Global data fetch error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
