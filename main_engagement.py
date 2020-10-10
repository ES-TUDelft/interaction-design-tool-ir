import logging
import sys

from data_manager.controller.db_stream_controller import DBStreamController
from robot_manager.worker.irc.engagement_worker import EngagementWorker

ROBOT_NAME = "NAO"
ROBOT_REALM = None

logger = logging.getLogger("EngagementMain")


def main():
    global engagement_worker

    robot_name = ROBOT_NAME
    robot_realm = ROBOT_REALM

    db_stream_controller = DBStreamController()
    conn_data = db_stream_controller.find_one(coll=db_stream_controller.interaction_collection, data_key="connectRobot")
    if conn_data:
        try:
            robot_name = conn_data["connectRobot"]["robotName"]
            robot_realm = conn_data["connectRobot"]["robotRealm"]
        except Exception as e_m:
            logger.error("Error while extracting robot props: {} | {}".format(conn_data, e_m))

    engagement_worker = EngagementWorker(robot_name=robot_name, robot_realm=robot_realm)
    engagement_worker.connect_robot()
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
