from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random

# Состояния игры
WAITING_PLAYERS, IN_GAME = range(2)

game_data = {
    "players": [],
    "state": WAITING_PLAYERS,
    "roles": {},
    "votes": {},
}

# Команда /start для начала игры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает игру и объясняет игрокам, как присоединиться."""
    await update.message.reply_text(
        "Добро пожаловать в игру 'Мафия'! Напишите /join, чтобы присоединиться к игре. "
        "Когда все будут готовы, организатор может написать /startgame для начала. "
        "Чтобы узнать свою роль после начала игры, используйте /myrole, а чтобы завершить игру - /endgame."
    )

# Присоединение к игре
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Позволяет игроку присоединиться к игре. Только доступно до начала игры."""
    if game_data["state"] != WAITING_PLAYERS:
        await update.message.reply_text("Игра уже началась, нельзя присоединиться.")
        return

    player = update.message.from_user.username
    if player not in game_data["players"]:
        game_data["players"].append(player)
        await update.message.reply_text(f"@{player} присоединился к игре!")
    else:
        await update.message.reply_text(f"@{player}, вы уже в игре.")

# Начало игры
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает игру, если набралось достаточно игроков, и распределяет роли."""
    if len(game_data["players"]) < 2:
        await update.message.reply_text("Недостаточно игроков для начала игры. Нужно минимум 4.")
        return

    game_data["state"] = IN_GAME
    await assign_roles(context)
    await update.message.reply_text(
        "Игра началась! Роли были распределены. Ночь наступила, мафия выбирает жертву. "
        "Чтобы узнать свою роль, используйте /myrole."
    )

# Распределение ролей
async def assign_roles(context: ContextTypes.DEFAULT_TYPE):
    """Распределяет роли среди игроков и уведомляет каждого о его роли."""
    roles = ["мафия", "мафия", "мирный", "мирный", "доктор", "детектив"]
    random.shuffle(roles)

    for player in game_data["players"]:
        role = roles.pop() if roles else "мирный"
        game_data["roles"][player] = role

        # Отправляем роль игроку в личные сообщения
        try:
            user_id = await get_user_id(context, player)
            if user_id:
                await context.bot.send_message(chat_id=user_id, text=f"Ваша роль: {role}.")
        except Exception as e:
            print(f"Ошибка при отправке роли игроку {player}: {e}")

async def get_user_id(context: ContextTypes.DEFAULT_TYPE, username: str):
    """Получает user_id по имени пользователя (если доступно в чате)."""
    for member in context.bot_data.get("chat_members", []):
        if member.username == username:
            return member.id
    return None

# Проверка роли игрока
async def my_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Позволяет игроку узнать свою роль."""
    player = update.message.from_user.username
    role = game_data["roles"].get(player)

    if role:
        await update.message.reply_text(f"Ваша роль: {role}. Вы можете использовать свою роль для действий в игре.")
    else:
        await update.message.reply_text("Вы не участвуете в игре. Напишите /join, чтобы присоединиться до начала игры.")

# Завершение игры
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершает игру, сбрасывая все данные."""
    game_data.clear()
    game_data.update({"players": [], "state": WAITING_PLAYERS, "roles": {}, "votes": {}})
    await update.message.reply_text(
        "Игра завершена! Спасибо за участие. Чтобы начать новую игру, используйте /start."
    )

# Основной метод
if __name__ == "__main__":
    TOKEN = "7582599877:AAGGx990kIV9qZUja67Nhcl6IfpRerrg28s"

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("startgame", start_game))
    application.add_handler(CommandHandler("myrole", my_role))
    application.add_handler(CommandHandler("endgame", end_game))

    print("Бот запущен...")

    # Запуск бота
    application.run_polling()
