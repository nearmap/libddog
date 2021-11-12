import logging


def enable_logging(force: bool = True) -> None:
    # WARN is a high enough level that we don't have to worry about filtering
    # out log messages from underlying libraries like urllib3 which otherwise
    # can be noisy
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        level=logging.WARN,
        force=force,
    )
