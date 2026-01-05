import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import Config
from data_fetcher import DataFetcher
from pattern_detector import (
    SmartMoneyDetector,
    ElliotWaveDetector,
    SupportResistanceDetector
)
from signal_generator import SignalGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingBot:

    def __init__(self):
        self.user_asset = {}  # chat_id → asset key

    # -------------------------
    # Keyboards
    # -------------------------
    def asset_keyboard(self):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🛢 USOIL", callback_data="asset_USOIL"),
                InlineKeyboardButton("₿ BTC", callback_data="asset_BTC"),
                InlineKeyboardButton("⟠ ETH", callback_data="asset_ETH"),
            ]
        ])

    def action_keyboard(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Analysis", callback_data="analysis")],
            [InlineKeyboardButton("🔔 Signals", callback_data="signals")],
            [InlineKeyboardButton("📈 S/R Levels", callback_data="levels")],
            [InlineKeyboardButton("🔁 Change Asset", callback_data="change_asset")]
        ])

    # -------------------------
    # /start command
    # -------------------------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 *Multi-Asset Smart Trading Bot*\n\nSelect an asset:",
            reply_markup=self.asset_keyboard(),
            parse_mode="Markdown"
        )

    # -------------------------
    # Button handler
    # -------------------------
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id

        try:
            # -------------------------
            # Asset selection
            # -------------------------
            if query.data.startswith("asset_"):
                asset = query.data.split("_")[1]
                self.user_asset[chat_id] = asset

                await query.edit_message_text(
                    f"✅ Selected *{asset}*\n\nChoose an action:",
                    reply_markup=self.action_keyboard(),
                    parse_mode="Markdown"
                )
                return

            if query.data == "change_asset":
                await query.edit_message_text(
                    "Select an asset:",
                    reply_markup=self.asset_keyboard()
                )
                return

            # -------------------------
            # Load asset config
            # -------------------------
            asset = self.user_asset.get(chat_id, Config.DEFAULT_ASSET)
            asset_cfg = Config.ASSETS[asset]

            df = DataFetcher(asset_cfg).get_ohlcv()
            if df is None or df.empty:
                await query.message.reply_text("❌ Market data unavailable")
                return

            # -------------------------
            # Analysis pipeline
            # -------------------------
            smc = SmartMoneyDetector(df).detect_all_patterns()
            waves = ElliotWaveDetector(df).detect_waves()
            levels = SupportResistanceDetector(df).detect_levels()
            signals = SignalGenerator(df, smc, waves, levels).generate_signals()

            # -------------------------
            # ANALYSIS
            # -------------------------
            if query.data == "analysis":
                text = (
                    f"*{asset} Analysis ({asset_cfg['timeframe']})*\n\n"
                    f"Price: {df['close'].iloc[-1]:.2f}\n"
                    f"Order Blocks: {len(smc['order_blocks'])}\n"
                    f"FVGs: {len(smc['fvgs'])}\n"
                    f"Elliott Waves: {len(waves)}"
                )

            # -------------------------
            # SIGNALS
            # -------------------------
            elif query.data == "signals":
                if not signals:
                    text = f"❌ No valid {asset} signals right now"
                else:
                    s = signals[0]
                    text = (
                        f"🚨 *{asset} {s['type']} SIGNAL*\n\n"
                        f"Entry: {s['entry']:.2f}\n"
                        f"SL: {s['sl']:.2f}\n"
                        f"TP: {s['target']:.2f}\n"
                        f"RR: {s['rr']}\n"
                        f"Bias: {s['strength']}"
                    )

            # -------------------------
            # SUPPORT / RESISTANCE (FIXED)
            # -------------------------
            elif query.data == "levels":

                def fmt(level_list):
                    if not level_list:
                        return "—"
                    return "\n".join(
                        f"• {lvl['price']:.2f} ({lvl['strength']})"
                        for lvl in level_list
                    )

                text = (
                    f"*{asset} Support & Resistance*\n\n"
                    f"*HTF Support*\n{fmt(levels.get('HTF_support'))}\n\n"
                    f"*HTF Resistance*\n{fmt(levels.get('HTF_resistance'))}\n\n"
                    f"*LTF Support*\n{fmt(levels.get('LTF_support'))}\n\n"
                    f"*LTF Resistance*\n{fmt(levels.get('LTF_resistance'))}"
                )

            else:
                text = "Unknown action"

            # -------------------------
            # Send response
            # -------------------------
            try:
                await query.edit_message_text(text, parse_mode="Markdown")
            except Exception:
                await query.message.reply_text(text, parse_mode="Markdown")

        except Exception:
            logger.exception("Callback error")
            await query.message.reply_text("❌ Internal error occurred")

# -------------------------
# App entry point
# -------------------------
def main():
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    bot = TradingBot()
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button_handler))

    logger.info("Multi-Asset Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
