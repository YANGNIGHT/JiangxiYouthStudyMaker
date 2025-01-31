import json
import random
import secrets
from json import JSONDecodeError

import requests
import time
import xlrd
from anti_useragent import UserAgent
from tqdm import tqdm

# 是否包含subOrg参数，即是否为三级团组织，详见README，默认为否，即四级团组织
need_subOrg = False
# 随机暂停提交秒数 0 为不暂停
stop = 1.0


def makeHeader(openid=""):
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Connection': 'close',
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': 'JSESSIONID=' + secrets.token_urlsafe(40),
        'Host': 'www.jxqingtuan.cn',
        'Origin': 'http://www.jxqingtuan.cn',
        'Referer': 'http://www.jxqingtuan.cn/html/h5_index.html',
        'User-Agent': UserAgent(platform="iphone").wechat,
        'X-Requested-With': 'XMLHttpRequest'
    }


def getCourse():
    url = "http://www.jxqingtuan.cn/pub/vol/volClass/current"
    CourseJson = requests.get(url, headers=makeHeader()).json()
    Course = CourseJson.get("result")
    try:
        print("课程id：" + Course.get("id"))
        print("课程名称：" + Course.get("title"))
        return Course.get("id")
    except:
        print("查询课程致未知错误")
        exit()


def getStudy(course, nid, subOrg, cardNo, openid=""):
    course = str(int(course))
    url = "http://www.jxqingtuan.cn/pub/vol/volClass/join?accessToken=" + openid
    if need_subOrg:
        data = {"course": course, "subOrg": subOrg, "nid": nid, "cardNo": cardNo}
    else:
        data = {"course": course, "subOrg": None, "nid": nid, "cardNo": cardNo}
    try:
        res = json.loads(
            (requests.post(url=url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                           headers=makeHeader(openid))).text)
        if res.get("status") == 200:
            # print(cardNo + "大学习成功！")
            return
        else:
            print(cardNo + "提交大学习失败错误：" + res.text)
    except JSONDecodeError or UnboundLocalError:
        print(cardNo + "提交大学习导致严重未知错误：" + res.text)


if __name__ == '__main__':
    Course = getCourse()
    data = xlrd.open_workbook(r'192.xlsx')
    dataSheets = data.sheets()[0]
    row = dataSheets.nrows
    print("开始批量提交!")
    for i in tqdm(range(row)):
        rowData = dataSheets.row_values(i)
        studyData = []
        for a, b in enumerate(rowData):
            studyData.append(b)
        if need_subOrg:
            getStudy(Course, studyData[2], studyData[1], studyData[0], studyData[3])
        else:
            getStudy(Course, studyData[2], "", studyData[0], studyData[3])
        time.sleep(random.uniform(0, stop))
    print("批量提交完毕!")
