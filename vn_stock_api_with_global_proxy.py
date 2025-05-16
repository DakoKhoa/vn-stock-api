from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Static Vietnam data (simulate CafeF)
vn_data = {
    "TCB.VN": { "eps": 4500, "pe": 10.2, "pb": 1.3, "price": 35000 },
    "VCB.VN": { "eps": 5000, "pe": 12.1, "pb": 1.4, "price": 43000 },
    "HPG.VN": { "eps": 1800, "pe": 27.5, "pb": 3.2, "price": 21000 },
    "VNM.VN": { "eps": 3700, "pe": 18.9, "pb": 2.1, "price": 82000 }
}

@app.route("/vietnam", methods=["GET"])
def get_vn_stock():
    ticker = request.args.get("ticker", "").upper()
    data = vn_data.get(ticker)
    if not data:
        return jsonify({"error": f"No data found for {ticker}"}), 404
    return jsonify({ "ticker": ticker, **data })

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
