import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.config import BOT_TOKEN
from bot.db import init_db
from bot.handlers.common import router as common_router
from bot.handlers.tasks import router as tasks_router


async def set_commands(bot: Bot) -> None:
    """
    Регистрирует список команд бота, который Telegram показывает в меню.
    Это помогает пользователю увидеть доступные команды.
    """
    commands = [
        BotCommand(command="start", description="Запустить бота и показать помощь"),
        BotCommand(command="add", description="Добавить новую задачу"),
        BotCommand(command="list", description="Показать список задач"),
        BotCommand(command="list_csv", description="Получить задачи в CSV-файле"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    """
    Главная асинхронная функция:
    - настраивает логирование;
    - проверяет наличие токена;
    - инициализирует базу данных;
    - создаёт объект бота и диспетчер;
    - регистрирует обработчики и команды;
    - запускает бесконечный цикл опроса (polling).
    """
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        # Для безопасности токен берётся из переменной окружения.
        # Это позволяет не хранить секретный ключ в коде.
        raise RuntimeError(
            "Не задан токен бота. "
            "Установите переменную окружения BOT_TOKEN перед запуском."
        )

    # Инициализируем (создаём при необходимости) базу данных и таблицу tasks.
    await init_db()

    # Начиная с aiogram 3.7, parse_mode нужно передавать через DefaultBotProperties.
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем маршрутизаторы с обработчиками команд.
    dp.include_router(common_router)
    dp.include_router(tasks_router)

    # Регистрируем команды, чтобы они отображались в интерфейсе Telegram.
    await set_commands(bot)

    logging.info("Бот запущен. Ожидание сообщений...")
    # Стартуем опрос обновлений от Telegram.
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем основную асинхронную функцию.
    asyncio.run(main())

