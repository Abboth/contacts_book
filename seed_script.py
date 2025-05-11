import asyncio
from datetime import datetime
import logging
from src.core.connection import async_sessionmanager
from src.mail_services.models import EmailTemplates
from src.users.models import Role

logging.basicConfig(level=logging.INFO)

async def seed_data():
    async with async_sessionmanager.session() as db:
        try:
            roles = [
                Role(id=1, role_name="admin"),
                Role(id=2, role_name="moderator"),
                Role(id=3, role_name="user")
            ]

            for role in roles:
                await db.merge(role)

            templates = [
                EmailTemplates(id=1, name="draft", subject="draft", created_at=datetime.now())
            ]

            for template in templates:
                await db.merge(template)

            await db.commit()
            logging.info("Seed data added successfully!")

        except Exception as e:
            await db.rollback()
            logging.info(f"Error seeding data: {e}")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
