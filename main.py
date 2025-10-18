import fetchActivities as FetchActivities
import logging
import configparser
import datetime

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
file_handler = logging.FileHandler("tmp.log", mode="a")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

config = configparser.ConfigParser()
config.read('config.ini')

Token = config.get('account', 'Token')
days_ahead = config.getint('settings', 'days_ahead')
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
    'Token': Token
}



def main():
    Avaliable_Activities = FetchActivities.fetchActivityDetail(headers, FetchActivities.fetchActivityLibList(headers))
    sorted_activities = sorted(Avaliable_Activities, key=lambda x: x['start_dt'])
    logger.info(f"Total available activities (sorted): {sorted_activities}")
    #print(len(sorted_activities))
    deltaTime=datetime.timedelta(days=days_ahead)
    logger.info("----- Upcoming Activities -----")
    for activity in sorted_activities:
        if activity['start_dt'] - datetime.datetime.now() < deltaTime:
            logger.debug(activity)
            logger.info(f"{activity["activityName"]}\n{activity['start_dt'].strftime('%m.%d %H:%M')} - {activity['end_dt'].strftime('%m-%d %H:%M')}\nid: {activity['activityId']}\n")
    logger.info("----- End of Activities -----")
    logger.info(f"Total Upcoming Activities in next {days_ahead} days: {len(sorted_activities)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")