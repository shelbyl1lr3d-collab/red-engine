import os, json, hmac, hashlib, time, urllib.parse
from datetime import datetime

class BinanceExchange:
    def __init__(self, engine):
        self.engine = engine
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.base_url = os.getenv("BINANCE_API_URL", "https://api.binance.com")
        self.withdrawals_disabled = True

    def is_configured(self):
        return bool(self.api_key) and bool(self.api_secret)

    def _sign(self, params):
        query = urllib.parse.urlencode(params)
        signature = hmac.new(self.api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method, path, params=None, signed=False):
        import requests
        url = f"{self.base_url}{path}"
        headers = {"X-MBX-APIKEY": self.api_key}
        params = params or {}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params = self._sign(params)

        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=15)
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                resp = requests.post(url, headers=headers, data=params, timeout=15)

            if resp.status_code == 200:
                return resp.json()
            return {"error": f"Binance API {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    def get_price(self, symbol="BTCUSDT"):
        return self._request("GET", "/api/v3/ticker/price", {"symbol": symbol})

    def get_balance(self):
        return self._request("GET", "/api/v3/account", signed=True)

    def get_asset_balance(self, asset="USDT"):
        account = self.get_balance()
        if "error" in account:
            return account
        for bal in account.get("balances", []):
            if bal["asset"] == asset:
                return {"asset": asset, "free": bal["free"], "locked": bal["locked"]}
        return {"asset": asset, "free": "0", "locked": "0"}

    def market_buy(self, symbol="BTCUSDT", quote_quantity=None):
        if self.is_configured() == False:
            return {"error": "Binance not configured"}
        params = {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
        }
        if quote_quantity:
            params["quoteOrderQty"] = str(quote_quantity)
            params["newOrderRespType"] = "FULL"
        return self._request("POST", "/api/v3/order", params, signed=True)

    def market_sell(self, symbol="BTCUSDT", quantity=None):
        if self.is_configured() == False:
            return {"error": "Binance not configured"}
        params = {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
        }
        if quantity:
            params["quantity"] = str(quantity)
            params["newOrderRespType"] = "FULL"
        return self._request("POST", "/api/v3/order", params, signed=True)

    # --- Sub-account management ---
    def create_sub_account(self, account_name):
        """Create a Binance sub-account for an AI agent."""
        params = {"subAccountString": account_name}
        return self._request("POST", "/sapi/v1/sub-account/virtualSubAccount", params, signed=True)

    def get_sub_accounts(self):
        return self._request("GET", "/sapi/v1/sub-account/list", signed=True)

    def transfer_to_sub(self, sub_email, asset="USDT", amount=0):
        """Transfer funds from master to sub-account."""
        params = {
            "toEmail": sub_email,
            "asset": asset,
            "amount": str(amount)
        }
        return self._request("POST", "/sapi/v1/sub-account/transfer/subToSub", params, signed=True)

    def get_sub_balance(self, sub_email):
        params = {"email": sub_email}
        return self._request("GET", "/sapi/v1/sub-account/assets", params, signed=True)

    # --- Automated trading loop ---
    def auto_dca(self, symbol="BTCUSDT", amount_usd=10, interval_hours=24):
        """Dollar-cost average into a core asset."""
        result = self.market_buy(symbol, amount_usd)
        self.engine.log(f"Auto DCA: ${amount_usd} → {symbol}")
        return result

    def route_revenue_to_liquidity(self, amount_usd):
        """Route revenue into USDT and core assets."""
        results = []
        # 40% USDT
        # 30% BTC
        # 20% BNB
        # 10% ETH
        splits = [("USDT", 0.4), ("BTCUSDT", 0.3), ("BNBUSDT", 0.2), ("ETHUSDT", 0.1)]
        for sym, pct in splits:
            amt = round(amount_usd * pct, 2)
            if amt < 1:
                continue
            if sym == "USDT":
                results.append({"asset": sym, "amount": amt, "status": "held as USDT"})
            else:
                r = self.market_buy(sym, amt)
                results.append({"asset": sym, "amount": amt, "result": r.get("status", "executed") if isinstance(r, dict) else "error"})
        self.engine.log(f"Revenue routed: ${amount_usd} split across core assets")
        return {"routed": amount_usd, "splits": results}

    def get_trading_fees(self):
        return self._request("GET", "/sapi/v1/asset/tradeFee", signed=True)

    def get_open_orders(self, symbol=None):
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/api/v3/openOrders", params, signed=True)

    def cancel_order(self, symbol, order_id):
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/api/v3/order", params, signed=True)
