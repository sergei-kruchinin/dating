# create_db_once.py
import asyncio

from src.config.database import init_db


async def main():
    # Инициализация базы данных
    await init_db()
    print("Database has been initialized.")


if __name__ == "__main__":
    asyncio.run(main())