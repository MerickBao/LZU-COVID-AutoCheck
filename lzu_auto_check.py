#!/usr/bin/env python
# -*-coding:utf-8-*-

import time
import os
import sys
import requests
import json
import random
import re
from lxml import etree

session = requests.session()


def getSubmit(auToken, dailyCookie, info, FilledInfo):
    subApi = 'http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/submit'
    subHeaders = {
        'Authorization': str(auToken),
        'Cookie': 'iPlanetDirectoryPro='+str(dailyCookie)
    }
    FilledInfo = FilledInfo['data'][0]
    info_data = info['data']['list'][0]
    sfzx = info_data['sfzx'] if info_data['sfzx'] else FilledInfo['sfzx'],
    info_data = {
        "bh": info_data['bh'],  # 编号
        "xykh": info_data['xykh'],  # 校园卡号
        "twfw": "0",  # 体温范围(0为小于37.3摄氏度)
        "jkm": "0", # 健康码(0为绿码)
        "sfzx": "1",  # 是否在校(0离校，1在校)
        "sfgl": "0",  # 是否隔离(0正常，1隔离)
        "szsf": info_data['szsf'] if info_data['szsf'] else "",  # 所在省份（没有打过卡或在校则为空）
        "szds": info_data['szds'] if info_data['szds'] else "",  # 所在地级市（没有打过卡或在校则为空）
        "szxq": info_data['szxq'] if info_data['szxq'] else "",  # 所在县/区（没有打过卡或在校则为空）
        "sfcg": info_data['sfcg'] if info_data['sfcg'] else "0",  # 是否出国（没有则为否）
        "cgdd": info_data['cgdd'] if info_data['cgdd'] else "",  # 出国地点（没有则无）
        "gldd": "",  # 隔离地点
        "jzyy": "",  # 就诊医院
        "bllb": "0",  # 是否被列入(疑似/确诊)病例(0没有，其它为疑似/确诊)
        "sfjctr": "0",  # 是否接触他人(0否，1是)
        "jcrysm": "",  # 接触人员说明
        "xgjcjlsj": "", # 相关接触经历时间
        "xgjcjldd": "", # 相关接触经历地点
        "xgjcjlsm": "", # 相关接触经历说明
        "zcwd": "0.0", # 早晨温度(体温)
        "zwwd": "0.0", # 中午温度(体温)
        "wswd": "0.0", # 晚上温度(体温)
        "sbr": info_data['sbr'], # 上报人
        "sjd": info['data']['sjd'], # 时间段
        "initLng": "", # 初始经度/定位ip?（似乎暂未启用，后续可能会启用）
        "initLat": "", # 初始纬度/定位地址?（似乎暂未启用，后续可能会启用）
        "dwfs": "" # 定位方式（似乎暂未启用，后续可能会启用）
    }

    res = session.post(subApi, info_data, headers=subHeaders).text
    return json.loads(res), info_data


def getST(dailyCookie):
    stApi = 'http://my.lzu.edu.cn/api/getST'
    stHeaders = {
        'Cookie': 'iPlanetDirectoryPro='+str(dailyCookie)
    }
    stData = {
        'service': 'http://127.0.0.1'
    }
    stRes = session.post(stApi, stData, headers=stHeaders)
    stDic = json.loads(stRes.text)

    if stDic['state'] == 1:
        return str(stDic['data'])
    else:
        print("Error Getting ST-Token!")
        raise Exception("Error Getting ST-Token!")


def getAuthToken(stToken, cardID, dailyCookie):
    auApi = 'http://appservice.lzu.edu.cn/dailyReportAll/api/auth/login?st=' + \
        str(stToken)+'&PersonID='+str(cardID)
    auHeader = {
        'Cookie': 'iPlanetDirectoryPro='+str(dailyCookie)
    }
    auRes = session.get(auApi, headers=auHeader)
    auDic = json.loads(auRes.text)

    if auDic['code'] == 1:
        return str(auDic['data']['accessToken'])
    else:
        print("Getting AU-Token Failed!")
        raise Exception("Getting AU-Token Failed!")


def getSeqMD5(cardID, auToken, dailyCookie):
    seqMD5Api = 'http://appservice.lzu.edu.cn/dailyReportAll/api/encryption/getMD5'
    seqMD5Header = {
        'Authorization': str(auToken),
        'Cookie': 'iPlanetDirectoryPro='+str(dailyCookie)
    }
    seqMD5Data = {
        'cardId': str(cardID)
    }
    seqMD5Res = session.post(seqMD5Api, seqMD5Data, headers=seqMD5Header)
    seqMD5Dic = json.loads(seqMD5Res.text)

    if seqMD5Dic['code'] == 1:
        return str(seqMD5Dic['data'])
    else:
        print("Getting card-Enc-MD5 Failed!")
        raise Exception("Getting card-Enc-MD5 Failed!")


def getSeqInfo(cardID, cardMD5, auToken):
    seqInfoApi = 'http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/getInfo'
    seqInfoHeader = {
        'Authorization': str(auToken)
    }
    seqInfoData = {
        'cardId': str(cardID),
        'md5': str(cardMD5)
    }
    seqInfoRes = session.post(seqInfoApi, seqInfoData, headers=seqInfoHeader)
    seqInfoDic = json.loads(seqInfoRes.text)

    return seqInfoDic


def getFilledInfo(cardID, cardMD5, auToken):
    FilledInfoApi = 'http://appservice.lzu.edu.cn/dailyReportAll/api/grtbJcxxtb/getInfo'
    FilledInfoHeader = {
        'Authorization': str(auToken)
    }
    FilledInfoData = {
        'cardId': str(cardID),
        'md5': str(cardMD5)
    }
    FilledInfoRes = session.post(
        FilledInfoApi, FilledInfoData, headers=FilledInfoHeader)
    FilledInfoDic = json.loads(FilledInfoRes.text)
    if FilledInfoDic['code'] == 1:
        return FilledInfoDic
    else:
        print("Error Getting Sequence-Number!")
        raise Exception("Error Getting Sequence-Number!")


def getDailyToken(user, password):
    login_url = 'http://my.lzu.edu.cn:8080/login?service=http://my.lzu.edu.cn'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40',
    }
    response = session.get(login_url, headers=header)
    tree = etree.HTML(response.text)
    lt = tree.xpath("//*[@id='loginForm']/div[3]/div[2]/input[2]/@value")
    execution = tree.xpath("//*[@id='loginForm']/div[3]/div[2]/input[3]/@value")
    eventId = tree.xpath("//*[@id='loginForm']/div[3]/div[2]/input[4]/@value")
    formData = {
        'username': user,
        'password': password,
        'lt': lt,
        'execution': execution,
        '_eventId': eventId
    }
    response = session.post(login_url, formData,
                            headers=header, allow_redirects=False)
    if response.status_code != 302:
        print("Wrong password or user! Please make sure you set related values correctly.")
        raise Exception("Wrong password or user! Please make sure you set related values correctly.")
    else:
        wrongurl = response.headers['location']
        if not "/?" in wrongurl:
            wrongurl = wrongurl.replace("?","/?")
        response = session.post(wrongurl, headers=header)
        if not (user.isdigit() and len(user) == 12):
            user = ''.join(re.findall(r"var personId = '(.+?)';", response.text))
        dayCok = requests.utils.dict_from_cookiejar(session.cookies)['iPlanetDirectoryPro']
        return dayCok, user


def submitCard():
    timeStamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    print("***************************")
    print(timeStamp, "正在打卡中...")

    cardID = os.environ['CARDID']
    passwd = os.environ['PASSWORD']
    sendKey = os.environ['SENDKEY']
    # server酱接口
    serverchanUrl = 'https://sctapi.ftqq.com/' + sendKey + '.send'

    dayCok, cardID = getDailyToken(cardID, passwd)
    ST = getST(dayCok)
    AuToken = getAuthToken(ST, cardID, dayCok)
    MD5 = getSeqMD5(cardID, AuToken, dayCok)
    info = getSeqInfo(cardID, MD5, AuToken)
    FilledInfo = getFilledInfo(cardID, MD5, AuToken)

    if info['code'] != 1:
        print(str(timeStamp)+" 未知错误，无法打卡!")
        serverchanParameters = {
            'title': ' 打卡失败！！！，请手动尝试。',
            'desp': '### ' + str(timeStamp) + ' 未知错误，无法打卡!'
        }
        requests.get(serverchanUrl, serverchanParameters)
        raise Exception(str(timeStamp)+" 未知错误，无法打卡!")
    response, _ = getSubmit(AuToken, dayCok, info, FilledInfo)
    if response['code'] == 1:
        print(str(timeStamp) + " 打卡成功，" + str(response) + "，疫情期间，记得保持身体健康哦!")
        serverchanParameters = {
            'title': ' 健康打卡成功',
            'desp': '### ' + str(timeStamp) + ' 疫情期间，记得保持身体健康哦！'
        }
        requests.get(serverchanUrl, serverchanParameters)
    else:
        print(str(timeStamp) + "打卡失败, " + str(response) + "，请提交相关问题到issue中!")
        serverchanParameters = {
            'title': ' 打卡失败！！！，请手动尝试。',
            'desp': '### ' + str(timeStamp) + " 打卡失败, " + str(response) + "，请提交相关问题到issue中，或者检查是否同步源仓库到最新!"
        }
        requests.get(serverchanUrl, serverchanParameters)
        raise Exception(str(timeStamp) + "打卡失败, " + str(response) + "，请提交相关问题到issue中!")


if __name__ == "__main__":

    # Delete for test
    if not os.environ['CARDID']:
        raise Exception("未设置变量CARDID，请检查！")
    if not os.environ['PASSWORD']:
        raise Exception("未设置变量PASSWORD，请检查！")
    if not os.environ['SENDKEY']:
        raise Exception('未设置变量SENDKEY，请检查！')

    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'delayrand':
            delay = random.randint(0,1200)
            print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "随机延迟"+ str(delay) +"秒")
            time.sleep(delay)
        submitCard()
    except Exception:
        if len(sys.argv) > 1 and sys.argv[1] == 'delayrand':
            print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "第一次尝试失败, 再次尝试中...")
            try:
                delay = random.randint(0,120)
                print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "随机延迟"+ str(delay) +"秒")
                time.sleep(delay)
                submitCard()
            except Exception:
                print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "第二次尝试失败, 再次尝试中...")
                try:
                    delay = random.randint(0,120)
                    print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "随机延迟"+ str(delay) +"秒")
                    time.sleep(delay)
                    submitCard()
                except Exception:
                    print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "第三次尝试失败, 再次尝试中...")
                    delay = random.randint(0,120)
                    print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "随机延迟"+ str(delay) +"秒")
                    time.sleep(delay)
                    submitCard()
        else:
            print(time.strftime("%Y-%m-%d %H:%M", time.localtime()), "打卡失败, 请检查相关工作流配置, 或者等待一段时间后再次运行! 如有疑问请提交相关问题到issue中")
            exit(1)