import datetime
import requests

from main import fetchActivityLibList, fetchActivityDetail, headers


class DummyResp:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.HTTPError(f"Status: {self.status_code}")


def test_fetch_activity_lib_list(monkeypatch):
    sample = {"list": [{"activityLibraryId": "lib1", "name": "Lib One"}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        return DummyResp(sample)

    monkeypatch.setattr('main.session.post', fake_post)
    lst = fetchActivityLibList(headers)
    assert isinstance(lst, list)
    assert len(lst) == 1
    assert lst[0]['activityLibraryId'] == 'lib1'


def test_fetch_activity_detail(monkeypatch):
    # prepare fake activities response
    now = datetime.datetime.now()
    start = (now + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    end = (now + datetime.timedelta(days=1, hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    sample = {
        "activities": [
            {
                "activityId": "a1",
                "activityName": "Test Activity",
                "classHour": 2,
                "activityLon": 0.0,
                "activityLat": 0.0,
                "statusName": "SIGNUPING",
                "startTime": start,
                "endTime": end,
                "enrollStartTime": start,
                "enrollEndTime": end,
            }
        ]
    }

    def fake_post(url, headers=None, timeout=None):
        return DummyResp(sample)

    monkeypatch.setattr('main.session.post', fake_post)
    libs = [{"activityLibraryId": "lib1", "name": "Lib One"}]
    activities = fetchActivityDetail(headers, libs)
    assert isinstance(activities, list)
    assert len(activities) == 1
    act = activities[0]
    assert act['activityId'] == 'a1'
    assert act['activityName'] == 'Test Activity'
    assert act['start_dt'] is not None
