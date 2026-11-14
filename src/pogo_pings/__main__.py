import logging

from pogo_pings.config import APP_ENV, LOG_LEVEL

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    logger.info("PoGO Pings started")
    logger.debug("Debug logging is enabled")

    print(f"Running in {APP_ENV} mode")


if __name__ == "__main__":
    main()
