import os
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.bot_token and self.chat_id)
        self.position_start_time = None
        self.bot = None

        if not self.enabled:
            print("ℹ️ Telegram notifications disabled")
            return

        try:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
            print("✅ Telegram notifications enabled")
        except ImportError:
            print("⚠️ python-telegram-bot not installed")
            self.enabled = False
        except Exception as e:
            print(f"⚠️ Telegram initialization failed: {e}")
            self.enabled = False

    async def clear_messages(self):
        """Clear chat by sending separator message"""
        if not self.enabled or not self.bot:
            print("🧹 Chat cleared")
            return
        
        try:
            separator_msg = "🧹" * 20 + "\n🤖 NEW SESSION\n" + "🧹" * 20
            await self.bot.send_message(chat_id=self.chat_id, text=separator_msg)
        except Exception as e:
            print(f"❌ Clear messages error: {e}")

    async def send_message(self, message):
        """Send message to Telegram or print to console"""
        if not self.enabled or not self.bot:
            print(f"📱 {message}")
            return
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"❌ Telegram error: {e}\n📱 {message}")

    async def trade_opened(self, symbol, price, size, side):
        """Notify when trade opens"""
        self.position_start_time = datetime.now()
        
        direction_emoji = "📈" if side == "Buy" else "📉"
        position_value = size * price
        msg = (
            f"🔔 {direction_emoji} OPENED {symbol}\n"
            f"📍 {side.upper()}\n"
            f"⏰ {self.position_start_time:%H:%M:%S}\n"
            f"💰 ${price:.4f}\n"
            f"📊 {size}\n"
            f"💵 ${position_value:.2f} USDT"
        )
        await self.send_message(msg)

    async def trade_closed(self, symbol, pnl_pct, pnl_usd, reason="Signal"):
        """Notify when trade closes"""
        close_time = datetime.now()
        duration_str = "N/A"
        earn_per_hour = 0

        if self.position_start_time:
            minutes = (close_time - self.position_start_time).total_seconds() / 60
            if minutes < 60:
                duration_str = f"{int(minutes)}m"
            else:
                hours = int(minutes // 60)
                mins = int(minutes % 60)
                duration_str = f"{hours}h {mins}m"
            
            earn_per_hour = (pnl_usd * 60) / minutes if minutes > 0 else 0
            self.position_start_time = None

        is_profit = pnl_pct > 0
        status_emoji = "✅ 💰" if is_profit else "❌ 📉"
        profit_status = "PROFIT" if is_profit else "LOSS"

        reason_icons = {
            "Signal": "🎯", 
            "Reverse Signal": "🔄", 
            "Loss Limit": "🚨",
            "Bot Stop": "⏹️", 
            "Take Profit": "💰", 
            "Stop Loss": "🛡️", 
            "Trailing Stop": "🔒",
            "Profit Protection": "🛡️💰"
        }
        icon = reason_icons.get(reason, "📝")

        msg = (
            f"{status_emoji} CLOSED {symbol} - {profit_status}\n"
            f"{icon} {reason}\n"
            f"⏰ {close_time:%H:%M:%S}\n"
            f"⏱️ {duration_str}\n"
            f"📈 {pnl_pct:+.2f}%\n"
            f"💵 ${pnl_usd:+.2f} USDT\n"
            f"📊 ${earn_per_hour:+.2f}/hour"
        )
        await self.send_message(msg)

    async def profit_lock_activated(self, symbol, pnl_pct, trailing_pct):
        """Notify when profit lock activated"""
        msg = (
            f"🔒 💎 PROFIT LOCK ACTIVATED!\n"
            f"📊 {symbol}\n"
            f"📈 +{pnl_pct:.2f}%\n"
            f"🎯 Trailing: {trailing_pct:.1f}%\n"
            f"⏰ {datetime.now():%H:%M:%S}"
        )
        await self.send_message(msg)

    async def position_switched(self, symbol, from_side, to_side, size, pnl_pct, pnl_usd):
        """Notify when position switched"""
        msg = (
            f"🔄 ⚡ POSITION SWITCHED!\n"
            f"📊 {symbol}\n"
            f"🔀 {from_side} → {to_side}\n"
            f"📈 {size}\n"
            f"📉 {pnl_pct:.2f}% (${pnl_usd:.2f})\n"
            f"⏰ {datetime.now():%H:%M:%S}"
        )
        await self.send_message(msg)

    async def error_notification(self, error_msg):
        """Notify about errors"""
        msg = f"⚠️ ERROR\n❌ {error_msg}\n⏰ {datetime.now():%H:%M:%S}"
        await self.send_message(msg)

    async def bot_started(self, symbol, balance):
        """Notify when bot starts"""
        await self.clear_messages()
        
        msg = (
            f"🤖 BOT STARTED\n"
            f"📊 {symbol}\n"
            f"💰 ${balance:.2f} USDT\n"
            f"⏰ {datetime.now():%H:%M:%S}"
        )
        await self.send_message(msg)

    async def bot_stopped(self):
        """Notify when bot stops"""
        msg = f"⏹️ BOT STOPPED\n⏰ {datetime.now():%H:%M:%S}"
        await self.send_message(msg)