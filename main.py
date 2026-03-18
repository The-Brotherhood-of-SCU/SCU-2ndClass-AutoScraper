import requests
import time
import json
import datetime
import logging
import configparser
import os
import sys
from logging.handlers import RotatingFileHandler
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
# Rotating file handler to avoid unlimited growth
file_handler = RotatingFileHandler("tmp.log", mode="a", maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Token and days_ahead are resolved in main() to keep module import-safe for tests
def resolve_config():
    token = os.environ.get('SCU_TOKEN')
    if not token:
        try:
            token = config.get('account', 'Token')
        except Exception:
            token = None

    try:
        days = config.getint('settings', 'days_ahead')
    except Exception:
        days = 3
        logger.info(f"Using default days_ahead={days}")

    return token, days

# Configure a requests Session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("HEAD", "GET", "POST"))
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)


def fetchActivityLibList(headers):
    url = 'https://zjczs.scu.edu.cn/ccyl-api/app/activity/list-activity-library'
    payload = {
        "pn": 1,
        "time": str(int(time.time() * 1000)),
        "ps": 2147483647,
        "level": "",
        "scoreType": "",
        "org": "",
        "order": "",
        "status": "SIGNUPING,DOING",
        "quality": ""
    }
    try:
        response0 = session.post(url=url, headers=headers, json=payload, timeout=10)
        response0.raise_for_status()
        data = response0.json()
        return data.get('list', [])
    except Exception as e:
        logger.critical(f"Error fetching activity library list: {e}")
        return []


def fetchActivityDetail(headers, ActivityLibList):
    logger.info(f"Fetching details for {len(ActivityLibList)} activity libraries.")
    base_url = 'https://zjczs.scu.edu.cn/ccyl-api/app/activity/get-lib-detail/'
    cc = 0
    ActivityList = []
    for item in ActivityLibList:
        activityLibraryId = item.get('activityLibraryId')
        LibName = item.get('name', '')
        logger.info(f"Fetching activities from library: {LibName} (ID: {activityLibraryId})")
        if not activityLibraryId:
            logger.warning(f"Skipping library with missing id: {item}")
            continue
        url2 = base_url + activityLibraryId
        try:
            response0 = session.post(url=url2, headers=headers, timeout=10)
            response0.raise_for_status()
            jresponse0 = response0.json()
            logger.debug(f"Response for library {LibName}: {jresponse0}")

            activities = jresponse0.get('activities', [])
            for activity in activities:
                try:
                    startTime = activity.get('startTime')
                    endTime = activity.get('endTime')
                    enrollStartTime = activity.get('enrollStartTime')
                    enrollEndTime = activity.get('enrollEndTime')

                    date_format = "%Y-%m-%d %H:%M:%S"
                    # parse times safely
                    def parse_dt(s):
                        if not s:
                            return None
                        return datetime.datetime.strptime(s, date_format)

                    start_dt = parse_dt(startTime)
                    end_dt = parse_dt(endTime)
                    enroll_start_dt = parse_dt(enrollStartTime)
                    enroll_end_dt = parse_dt(enrollEndTime)

                    now_dt = datetime.datetime.now()
                    # If we don't have end_dt and enroll_end_dt, skip
                    if (end_dt and end_dt > now_dt) or (enroll_end_dt and enroll_end_dt > now_dt):
                        cc += 1
                        activityId = activity.get('activityId')
                        activityName = activity.get('activityName')
                        classHour = activity.get('classHour')
                        pos = [activity.get('activityLon'), activity.get('activityLat')]
                        statusName = activity.get('statusName')

                        logger.info(f"Available {cc}:{activityName}，学时:{classHour}，状态:{statusName}，时间:{startTime}~{endTime}，位置:{pos}，ID:{activityId}")

                        ActivityList.append({
                            "activityId": activityId,
                            "activityName": activityName,
                            "classHour": classHour,
                            "statusName": statusName,
                            "start_dt": start_dt,
                            "end_dt": end_dt,
                            "enroll_start_dt": enroll_start_dt,
                            "enroll_end_dt": enroll_end_dt,
                            "pos": pos,
                            "fatherLibraryName": LibName
                        })
                except Exception as inner_e:
                    logger.error(f"Error parsing activity from library {LibName}: {inner_e} -- activity: {activity}")
                    continue

        except Exception as e:
            logger.critical(f"Error fetching activity detail for {LibName}: {e}")
    return ActivityList


def main():
    Token, days_ahead = resolve_config()
    if not Token:
        logger.error("No Token found. Set SCU_TOKEN env variable or add it to config.ini.")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
        'Token': Token
    }

    ActivityLibList = fetchActivityLibList(headers)
    Avaliable_Activities = fetchActivityDetail(headers, ActivityLibList)
    sorted_activities = sorted(Avaliable_Activities, key=lambda x: (x['start_dt'] or datetime.datetime.max))
    logger.info(f"Total available activities (sorted): {len(sorted_activities)}")
    deltaTime = datetime.timedelta(days=days_ahead)
    logger.info("----- Upcoming Activities -----")
    now = datetime.datetime.now()
    count_upcoming = 0
    for activity in sorted_activities:
        start_dt = activity.get('start_dt')
        if not start_dt:
            continue
        if start_dt - now < deltaTime:
            count_upcoming += 1
            logger.debug(activity)
            logger.info(f"{activity['activityName']}\n{start_dt.strftime('%m.%d %H:%M')} - {activity['end_dt'].strftime('%m-%d %H:%M') if activity.get('end_dt') else 'N/A'}\nid: {activity['activityId']}\n")
    logger.info("----- End of Activities -----")
    logger.info(f"Total Upcoming Activities in next {days_ahead} days: {count_upcoming}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")