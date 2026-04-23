import logging

def setup_logging():
    logging.basicConfig(
        # deploy using logging.INFO
        # DEBUG < INFO < WARNING < ERROR < CRITICAL
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )