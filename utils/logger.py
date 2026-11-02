
import logging
import os


def setup_logger():

    log_directory = "logs"

    os.makedirs(log_directory, exist_ok=True)

    log_file = os.path.join(
        log_directory,
        "inventory.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        force=True
    )

    return logging.getLogger("inventory-service")
