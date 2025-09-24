import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import random
from config import TELEGRAM_BOT_TOKEN
from database import Database
from currency_api import CurrencyAPI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FinanceBot:
    def __init__(self):
        self.db = Database()
        self.currency_api = CurrencyAPI("09edf8b2bb246e1f801cbfba")
        # Состояния для учета расходов
        self.expense_states = {}

        # Советы по экономии
        self.economy_tips = [
            "💡 Ведите бюджет и следите за своими расходами.",
            "💡 Откладывайте часть доходов на сбережения.",
            "💡 Покупайте товары по скидке или на распродажах."
        ]

    def get_main_keyboard(self):
        """Основная клавиатура с 4 кнопками"""
        keyboard = [
            [KeyboardButton("📋 Регистрация в боте")],
            [KeyboardButton("💱 Курс валют")],
            [KeyboardButton("💡 Советы по экономии")],
            [KeyboardButton("💰 Личные финансы")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def get_back_keyboard(self):
        """Клавиатура с кнопкой 'Назад'"""
        keyboard = [[KeyboardButton("🔙 Назад")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        message = (
            f"🎉 Привет, {user.first_name}! 👋\n\n"
            f"Я - ваш персональный финансовый ассистент 🤖\n\n"
            f"📊 С моей помощью вы сможете:\n"
            f"• Узнавать актуальные курсы валют\n"
            f"• Получать полезные советы по экономии\n"
            f"• Вести учет своих расходов\n\n"
            f"Нажмите на кнопки внизу, чтобы начать работу!"
        )

        await update.message.reply_text(message, reply_markup=self.get_main_keyboard())

    async def register_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Регистрация пользователя"""
        user = update.effective_user
        telegram_id = user.id

        if self.db.user_exists(telegram_id):
            message = "✅ Вы уже зарегистрированы в боте!"
        else:
            success = self.db.register_user(
                telegram_id=telegram_id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username
            )
            if success:
                message = "🎉 Успешная регистрация! Добро пожаловать в финансовый помощник!"
            else:
                message = "❌ Произошла ошибка при регистрации."

        await update.message.reply_text(message, reply_markup=self.get_main_keyboard())

    async def show_currency_rates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ курсов валют"""
        try:
            # Получаем курсы USD
            rates = self.currency_api.get_exchange_rates("USD")

            if rates:
                usd_to_rub = rates['rates'].get('RUB', 0)
                usd_to_eur = rates['rates'].get('EUR', 0)

                # Получаем курсы EUR
                eur_rates = self.currency_api.get_exchange_rates("EUR")
                eur_to_rub = eur_rates['rates'].get('RUB', 0) if eur_rates else 0

                message = (
                    "💱 Актуальные курсы валют:\n\n"
                    f"🇺🇸 1 USD = {usd_to_rub:.2f} RUB\n"
                    f"🇪🇺 1 EUR = {eur_to_rub:.2f} RUB\n"
                    f"🇺🇸 1 USD = {usd_to_eur:.4f} EUR\n\n"
                    f"Дата обновления: {rates['last_update']}"
                )
            else:
                message = "❌ Не удалось получить курсы валют. Попробуйте позже."

        except Exception as e:
            logger.error(f"Ошибка при получении курсов: {e}")
            message = "❌ Произошла ошибка при получении курсов валют."

        await update.message.reply_text(message, reply_markup=self.get_main_keyboard())

    async def send_economy_tip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправка случайного совета по экономии"""
        tip = random.choice(self.economy_tips)
        await update.message.reply_text(tip, reply_markup=self.get_main_keyboard())

    async def start_expense_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало учета расходов"""
        user_id = update.effective_user.id

        # Сбрасываем состояние пользователя
        self.expense_states[user_id] = {
            'step': 1,
            'data': {}
        }

        message = "Введите название первой категории расходов (например: транспорт, питание и т.д.):"
        await update.message.reply_text(message, reply_markup=self.get_back_keyboard())

    async def handle_expense_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода расходов"""
        user_id = update.effective_user.id
        text = update.message.text

        # Проверяем, находится ли пользователь в состоянии ввода расходов
        if user_id not in self.expense_states:
            await update.message.reply_text(
                "Нажмите на кнопки внизу для работы с ботом",
                reply_markup=self.get_main_keyboard()
            )
            return

        state = self.expense_states[user_id]

        if text == "🔙 Назад":
            # Выход из режима ввода расходов
            del self.expense_states[user_id]
            await update.message.reply_text(
                "Вы вышли из режима учета расходов.",
                reply_markup=self.get_main_keyboard()
            )
            return

        step = state['step']
        data = state['data']

        if step == 1:
            # Ввод первой категории
            data['category1'] = text
            state['step'] = 2
            message = f"Введите расходы для категории '{text}':"
            await update.message.reply_text(message, reply_markup=self.get_back_keyboard())

        elif step == 2:
            # Ввод суммы первой категории
            try:
                amount = float(text)
                data['amount1'] = amount
                state['step'] = 3
                message = "Введите название второй категории расходов:"
                await update.message.reply_text(message, reply_markup=self.get_back_keyboard())
            except ValueError:
                await update.message.reply_text(
                    "Пожалуйста, введите числовое значение расхода.",
                    reply_markup=self.get_back_keyboard()
                )

        elif step == 3:
            # Ввод второй категории
            data['category2'] = text
            state['step'] = 4
            message = f"Введите расходы для категории '{text}':"
            await update.message.reply_text(message, reply_markup=self.get_back_keyboard())

        elif step == 4:
            # Ввод суммы второй категории
            try:
                amount = float(text)
                data['amount2'] = amount
                state['step'] = 5
                message = "Введите название третьей категории расходов:"
                await update.message.reply_text(message, reply_markup=self.get_back_keyboard())
            except ValueError:
                await update.message.reply_text(
                    "Пожалуйста, введите числовое значение расхода.",
                    reply_markup=self.get_back_keyboard()
                )

        elif step == 5:
            # Ввод третьей категории
            data['category3'] = text
            state['step'] = 6
            message = f"Введите расходы для категории '{text}':"
            await update.message.reply_text(message, reply_markup=self.get_back_keyboard())

        elif step == 6:
            # Ввод суммы третьей категории
            try:
                amount = float(text)
                data['amount3'] = amount

                # Сохраняем расходы в базу данных
                success = self.db.save_expenses(
                    telegram_id=user_id,
                    category1=data['category1'],
                    amount1=data['amount1'],
                    category2=data['category2'],
                    amount2=data['amount2'],
                    category3=data['category3'],
                    amount3=amount
                )

                if success:
                    summary = (
                        f"✅ Ваши расходы сохранены:\n\n"
                        f"1. {data['category1']}: {data['amount1']} руб.\n"
                        f"2. {data['category2']}: {data['amount2']} руб.\n"
                        f"3. {data['category3']}: {amount} руб.\n\n"
                        f"Общий расход: {data['amount1'] + data['amount2'] + amount} руб."
                    )
                else:
                    summary = "❌ Произошла ошибка при сохранении расходов."

                # Очищаем состояние
                del self.expense_states[user_id]

                await update.message.reply_text(summary, reply_markup=self.get_main_keyboard())

            except ValueError:
                await update.message.reply_text(
                    "Пожалуйста, введите числовое значение расхода.",
                    reply_markup=self.get_back_keyboard()
                )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений от кнопок"""
        text = update.message.text
        user = update.effective_user

        if text == "📋 Регистрация в боте":
            await self.register_user(update, context)

        elif text == "💱 Курс валют":
            await self.show_currency_rates(update, context)

        elif text == "💡 Советы по экономии":
            await self.send_economy_tip(update, context)

        elif text == "💰 Личные финансы":
            await self.start_expense_tracking(update, context)

        else:
            # Обработка ввода расходов (если пользователь в состоянии учета расходов)
            await self.handle_expense_input(update, context)


# Создаем экземпляр бота и запускаем
def main():
    bot_instance = FinanceBot()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_message))

    # Запуск бота
    logger.info("Бот запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()