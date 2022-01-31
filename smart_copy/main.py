from sys import stdout

from loguru import logger

from console import main

DEBUG = False
if __name__ == '__main__':
    logger.remove()
    logger.add(stdout, level="TRACE" if DEBUG else "INFO")
    main()
