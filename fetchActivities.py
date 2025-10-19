import requests
import time
import json
import datetime
import logging


logger = logging.getLogger("my_logger")

#session = requests.Session()



def fetchActivityLibList(headers):
    url='https://zjczs.scu.edu.cn/ccyl-api/app/activity/list-activity-library'
    #{ "pn": 1, "time": "1760769825192", "ps": 10, "level": "", "scoreType": "", "org": "", "order": "", "status": "SIGNUPING", "quality": "" }
    #1760769978.8043609
    payloads=[{
        "pn": 1,
        "time": str(int(time.time()*1000)),
        "ps": 2147483647,
        "level": "",
        "scoreType": "",
        "org": "",
        "order": "updateTime",
        "status": "SIGNUPING",
        "quality": ""
    },
    {
        "pn": 1,
        "time": str(int(time.time()*1000)),
        "ps": 2147483647,
        "level": "",
        "scoreType": "",
        "org": "",
        "order": "updateTime",
        "status": "DOING",
        "quality": ""
    }]

    ActivityLibList = []
    seen = set()
    for idx, payload in enumerate(payloads, start=1):
        try:
            logger.info(f"Requesting activity library list (payload #{idx}, status={payload.get('status','')})")
            response = requests.post(url=url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            lst = data.get('list', [])
            if not isinstance(lst, list):
                logger.warning(f"Unexpected list format for payload #{idx}: {type(lst)}")
                continue

            for item in lst:
                aid = item.get('activityLibraryId')
                if aid is None:
                    continue
                if aid in seen:
                    continue
                seen.add(aid)
                ActivityLibList.append(item)

            logger.info(f"Payload #{idx} returned {len(lst)} items, merged so far: {len(ActivityLibList)} unique entries.")
        except Exception as e:
            logger.error(f"Error fetching activity library list for payload #{idx}: {e}")

    logger.info(f"Merged activity libraries: {len(ActivityLibList)} unique entries.")
    return ActivityLibList

def fetchActivityDetail(headers,ActivityLibList):
    logger.info(f"Fetching details for {len(ActivityLibList)} activity libraries.")
    url='https://zjczs.scu.edu.cn/ccyl-api/app/activity/get-lib-detail/'
    cc=0
    ActivityList=[]
    for item in ActivityLibList:
        activityLibraryId=item['activityLibraryId']
        LibName=item['name']
        logger.info(f"Fetching activities from library: {LibName} (ID: {activityLibraryId})")
        url2=url+activityLibraryId
        try:
            response0=requests.post(url=url2, headers=headers)
            jresponse0=response0.json()
            logger.debug(f"Response for library {LibName}: {jresponse0}")

            for activity in jresponse0['activities']:
                startTime=activity['startTime']
                endTime=activity['endTime']
                enrollStartTime=activity['enrollStartTime']
                enrollEndTime=activity['enrollEndTime']
                #尽管存在enrollEndTime，但实际上允许报名的时间貌似是由endTime决定的

                #"startTime": "2025-10-19 07:30:00"
                #"endTime": "2025-10-19 22:00:00"
                date_format = "%Y-%m-%d %H:%M:%S"
                start_dt = datetime.datetime.strptime(startTime, date_format)
                end_dt = datetime.datetime.strptime(endTime, date_format)
                enroll_start_dt = datetime.datetime.strptime(enrollStartTime, date_format)
                enroll_end_dt = datetime.datetime.strptime(enrollEndTime, date_format)
                now_dt = datetime.datetime.now()
                if end_dt > now_dt or enroll_end_dt > now_dt: #filter possible activities
                    cc+=1
                    #save key info
                    activityId=activity['activityId']
                    activityName=activity['activityName']
                    classHour=activity['classHour']
                    #signStatus=[activity['isSignIn'], activity['isSignOut']]
                    pos=[activity['activityLon'], activity['activityLat']]
                    statusName=activity['statusName'] #报名中，进行中，已结束
                    
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
                        "fatherLibraryName":LibName
                    })

                    #ActivityList.append([activityId, activityName, classHour, statusName, start_dt, end_dt, enroll_start_dt, enroll_end_dt, pos])
                    # 0 activityId,1 activityName,2 classHour,3 statusName,4 start_dt,5 end_dt,6 enroll_start_dt,7 enroll_end_dt,8 pos

            
        except Exception as e:
            logger.critical(f"Error fetching activity detail for {LibName}: {e}")
            #logger.critical("Response content:", response0.text)
    return ActivityList

if __name__ == "__main__":
    pass
