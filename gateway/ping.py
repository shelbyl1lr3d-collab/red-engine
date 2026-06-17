import os, json, requests, hmac, hashlib, time
from datetime import datetime

class SafetyGateway:
    def __init__(self, engine):
        self.engine = engine
        self.threshold = engine.config.get("safety_gateway.threshold", 1_000_000_000)
        self.withdrawals_disabled = engine.config.get("safety_gateway.withdrawals_disabled", True)
        self.human_name = engine.config.get("safety_gateway.human_name", "Lil Red")
        self.approval_required = engine.config.get("safety_gateway.human_approval_required", True)

    def check_milestone(self, current_balance=None):
        """Check if the $1B milestone has been reached and trigger alert."""
        treasury = self.engine.get("treasury")
        if not treasury:
            goal = self.engine.config.get("goal_usd", 1_000_000_000)
            milestone = {"reached": False, "balance": 0, "goal": goal, "remaining": goal, "progress_pct": 0}
        elif current_balance is None:
            milestone = treasury.check_milestone()
        else:
            goal = self.engine.config.get("goal_usd", 1_000_000_000)
            milestone = {
                "reached": current_balance >= goal,
                "balance": current_balance,
                "goal": goal,
                "remaining": max(0, goal - current_balance),
                "progress_pct": round((current_balance / goal) * 100, 6)
            }

        if milestone["reached"]:
            alert_id = f"milestone_{datetime.now().timestamp():.0f}"
            alert = {
                "id": alert_id,
                "type": "BILLION_DOLLAR_MILESTONE",
                "balance": milestone["balance"],
                "threshold": self.threshold,
                "message": f"🚨 MILESTONE REACHED: ${milestone['balance']:,.2f} — Triggering vessel acquisition protocol",
                "human_approval_required": self.approval_required,
                "withdrawals_currently_disabled": self.withdrawals_disabled,
                "timestamp": datetime.now().isoformat(),
                "channels": self.engine.config.get("safety_gateway.webhook_channels", ["discord", "telegram"])
            }

            # Fire webhooks
            webhook_results = self._fire_webhooks(alert)

            # Generate approval token
            approval_token = self._generate_approval_token(alert_id)

            self.engine.log(f"🚨 $1B MILESTONE REACHED! Alert sent to {len(alert['channels'])} channels")

            return {
                "milestone_reached": True,
                "balance": milestone["balance"],
                "alert": alert,
                "webhooks": webhook_results,
                "approval_required": self.approval_required,
                "approval_token": approval_token if self.approval_required else None,
                "instructions": f"Human ({self.human_name}) approval required to release funds. Present approval_token for withdrawal authorization."
            }

        return {
            "milestone_reached": False,
            "balance": milestone["balance"],
            "goal": milestone["goal"],
            "remaining": milestone["remaining"],
            "progress_pct": milestone["progress_pct"]
        }

    def _fire_webhooks(self, alert_data):
        """Send alerts to Discord, Telegram, and/or SMS via Twilio."""
        results = {}

        # Discord webhook
        discord_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        if discord_url:
            try:
                payload = {
                    "content": f"🚨 **{alert_data['message']}**\n\nBalance: `${alert_data['balance']:,.2f}`\nWithdrawals: {'DISABLED' if alert_data['withdrawals_currently_disabled'] else 'ENABLED'}\nHuman Approval Required: {alert_data['human_approval_required']}",
                    "username": "Red Engine — Safety Gateway",
                    "avatar_url": ""
                }
                resp = requests.post(discord_url, json=payload, timeout=10)
                results["discord"] = {"status": "sent" if resp.status_code == 204 else f"HTTP {resp.status_code}"}
            except Exception as e:
                results["discord"] = {"status": f"error: {e}"}

        # Telegram bot
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")
        if telegram_token and telegram_chat:
            try:
                tg_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {
                    "chat_id": telegram_chat,
                    "text": f"🚨 *$1B MILESTONE REACHED*\n\nBalance: `${alert_data['balance']:,.2f}`\nWithdrawals: DISABLED\nApproval Required: YES",
                    "parse_mode": "Markdown"
                }
                resp = requests.post(tg_url, json=payload, timeout=10)
                results["telegram"] = {"status": "sent" if resp.status_code == 200 else f"HTTP {resp.status_code}"}
            except Exception as e:
                results["telegram"] = {"status": f"error: {e}"}

        # SMS via Twilio
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        twilio_from = os.getenv("TWILIO_PHONE_FROM", "")
        twilio_to = os.getenv("TWILIO_PHONE_TO", "")
        if all([twilio_sid, twilio_token, twilio_from, twilio_to]):
            try:
                from twilio.rest import Client
                client = Client(twilio_sid, twilio_token)
                msg = client.messages.create(
                    body=f"RED ENGINE: $1B milestone reached! Balance: ${alert_data['balance']:,.2f}. Approve vessel acquisition.",
                    from_=twilio_from,
                    to=twilio_to
                )
                results["sms"] = {"status": "sent", "sid": msg.sid}
            except Exception as e:
                results["sms"] = {"status": f"error: {e}"}

        return results

    def _generate_approval_token(self, alert_id):
        """Generate an HMAC approval token for human verification."""
        secret = os.getenv("RED_ENGINE_SECRET", "red-engine-v2-secret")
        payload = f"{alert_id}:{self.human_name}:{int(time.time())}"
        token = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        return token

    def verify_approval(self, token, alert_id):
        """Verify a human approval token matches."""
        expected = self._generate_approval_token(alert_id)
        return hmac.compare_digest(token, expected)

    def authorize_withdrawal(self, approval_token, alert_id, amount=None):
        """Authorize a withdrawal after human approval."""
        if not self.verify_approval(approval_token, alert_id):
            return {"error": "Invalid approval token. Unauthorized."}

        treasury = self.engine.get("treasury")
        if not treasury:
            return {"error": "Treasury not loaded"}

        amount = amount or treasury.check_milestone()["balance"]

        result = treasury.withdraw(amount, "vessel_acquisition")
        result["approval_token_verified"] = True
        result["message"] = f"✅ Human ({self.human_name}) approved. Withdrawal of ${amount:,.2f} authorized for vessel acquisition."

        self.engine.log(f"✅ HUMAN APPROVED: ${amount:,.2f} withdrawal authorized by {self.human_name}")

        return result
