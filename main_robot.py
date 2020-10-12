import logging
import sys

from robot_manager.worker.irc.animation_worker import AnimationWorker

logger = logging.getLogger("RobotMain")


def main():
    global robot_worker

    robot_worker = AnimationWorker()
    robot_worker.connect_robot()
    logger.info("Robot Worker is up and running.")


if __name__ == '__main__':
    global robot_worker
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
        robot_worker.exit_gracefully()
