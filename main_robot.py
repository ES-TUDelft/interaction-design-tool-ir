import logging
import sys

from es_common.utils.db_helper import DBHelper
from robot_manager.robot_worker import RobotWorker

ROBOT_NAME = "NAO"
ROBOT_REALM = None

logger = logging.getLogger("RobotMain")


def main():
    global robot_worker

    robot_name = ROBOT_NAME
    robot_realm = ROBOT_REALM

    db_helper = DBHelper()
    conn_data = db_helper.find_one(coll=db_helper.interaction_collection, data_key="connectRobot")
    if conn_data:
        try:
            robot_name = conn_data["connectRobot"]["robotName"]
            robot_realm = conn_data["connectRobot"]["robotRealm"]
        except Exception as e_m:
            logger.error("Error while extracting robot props: {} | {}".format(conn_data, e_m))

    robot_worker = RobotWorker(robot_name=robot_name, robot_realm=robot_realm)
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