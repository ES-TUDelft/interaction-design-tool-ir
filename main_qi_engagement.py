import logging
import sys

from robot_manager.worker.qi.engagement_worker import EngagementWorker

logger = logging.getLogger("QIEngagementMain")


def main():
    global engagement_worker

    engagement_worker = EngagementWorker()
    engagement_worker.connect_robot()
    engagement_worker.run()
    logger.info("Engagement Worker is up and running.")


if __name__ == '__main__':
    global engagement_worker
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(filename)s:%(lineno)4d: %(message)s",
                        stream=sys.stdout)
    try:
        main()
    except KeyboardInterrupt as e:
        logger.warning("Keyboard interrupt: {}".format(e))
    except Exception as e:
        logger.error("Exception: {}".format(e))
    finally:
        logger.info("Disconnecting...")
        engagement_worker.exit_gracefully()
