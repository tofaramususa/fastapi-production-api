# This is the file where we start by connecting to the database first
import asyncio
import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.database.session import ping
import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        await ping()
    except Exception as e:
        logger.error(e)
        raise e


async def init_firebase() -> None:
    try:
        logger.info("Initializing firebase")
        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized")
    except Exception as e:
        logger.error(e)


async def main() -> None:
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initialising")
    # await init_firebase()


if __name__ == "__main__":
    asyncio.run(main())
