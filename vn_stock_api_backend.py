from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Mocked CafeF data (replace with scraping in production)
vn_data = {
    "TCB.VN": { "eps": 4500, "pe": 10.2, "pb": 1.3 },
    "VCB.VN": { "eps": 5000, "pe": 12.1, "pb": 1.4 },
    "HPG.VN": { "eps": 1800, "pe": 27.5, "pb": 3.2 },
    "VNM.VN": { "eps": 3700, "pe": 18.9, "pb": 2.1 },
}

@app.route("/vietnam", methods=["GET"])
def get_vn_stock():
    ticker = request.args.get("ticker", "").upper()
    data = vn_data.get(ticker)
    if not data:
        return jsonify({"error": f"No data found for {ticker}"}), 404
    return jsonify({ "ticker": ticker, **data })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
