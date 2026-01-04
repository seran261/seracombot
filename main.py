import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import Config
from data_fetcher import DataFetcher
from pattern_detector import SmartMoneyDetector, ElliotWaveDetector, SupportResistanceDetector
from signal_generator import SignalGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USOILBot:

    def __init__(self):
        self.config = Config()
        self.fetcher = DataFetcher(self.config.USOIL_SYMBOL)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📊 Analysis", callback_data="analysis")],
            [InlineKeyboardButton("🔔 Signals", callback_data="signals")],
            [InlineKeyboardButton("📈 S/R Levels", callback_data="levels")]
        ]
        await update.message.reply_text(
            "🤖 *USOIL Smart Money Bot*\n\nChoose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        df = self.fetcher.get_ohlcv("1h")
        if df is None or df.empty:
            await query.edit_message_text("❌ Market data unavailable")
            return

        smc = SmartMoneyDetector(df).detect_all_patterns()
        waves = ElliotWaveDetector(df).detect_waves()
        levels = SupportResistanceDetector(df).detect_levels()
        signals = SignalGenerator(df, smc, waves, levels).generate_signals()

        if query.data == "analysis":
            await query.edit_message_text(
                f"*USOIL Analysis (1H)*\n\n"
                f"Price: ${df['close'].iloc[-1]:.2f}\n"
                f"Order Blocks: {len(smc['order_blocks'])}\n"
                f"FVGs: {len(smc['fvgs'])}\n"
                f"Elliott Waves: {len(waves)}",
                parse_mode="Markdown"
            )

        elif query.data == "signals":
            if not signals:
                await query.edit_message_text("❌ No valid signals found")
                return

            s = signals[0]
            await query.edit_message_text(
                f"🚨 *{s['type']} SIGNAL*\n\n"
                f"Entry: {s['entry']:.2f}\n"
                f"Stop Loss: {s['sl']:.2f}\n"
                f"Target: {s['target']:.2f}\n"
                f"Risk/Reward: {s['rr']:.2f}\n"
                f"Strength: {s['strength']}%",
                parse_mode="Markdown"
            )

        elif query.data == "levels":
            await query.edit_message_text(
                f"*Support & Resistance*\n\n"
                f"S1: {levels['s1']:.2f}\n"
                f"S2: {levels['s2']:.2f}\n"
                f"R1: {levels['r1']:.2f}\n"
                f"R2: {levels['r2']:.2f}",
                parse_mode="Markdown"
            )

def main():
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    bot = USOILBot()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.button_handler))

    logger.info("USOIL Telegram Bot Running...")
    application.run_polling()

if __name__ == "__main__":
    main()
