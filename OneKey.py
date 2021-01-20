#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/1/9 下午4:35
# @Author : YuHui Li(MerylLynch)
# @File : OneKey.py
# @Comment : Created By Liyuhui,下午4:35
# @Completed : No
# @Tested : No
# conding:utf-8

import time
from argparse import ArgumentParser
import json
import requests
import urllib3

urllib3.disable_warnings()

try:
    import lxml
except Exception as ex:
    import os
    os.system('pip install lxml')
    import lxml

from lxml.html import etree  # 爬取网页的功能模块

s = requests.session()


def get_cas_info():
    result = {}
    loginurl = "https://sso.stu.edu.cn/login?service=https%3A%2F%2Fmy.stu.edu.cn%2Fhealth-report%2Finit-stu-user"
    h1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    }
    r = s.get(loginurl, headers=h1, verify=False)
    dom = etree.HTML(r.content)
    try:
        result["lt"] = dom.xpath('//input[@name="lt"]')[0].get("value")  # 这里又从0开始了
        result["execution"] = dom.xpath('//input[@name="execution"]')[0].get("value")
    except:
        print("lt、execution参数获取失败！")
    return result


def login(result, user, psw):
    loginurl = "https://sso.stu.edu.cn/login?service=https%3A%2F%2Fmy.stu.edu.cn%2Fhealth-report%2Finit-stu-user"
    h2 = {
        "Referer": loginurl,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Origin": "https://sso.stu.edu.cn",
        "Content-Length": "119",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "username": user,
        "password": psw,
        "lt": result["lt"],
        "execution": result["execution"],
        "_eventId": "submit"
    }
    resp = s.post(loginurl, headers=h2, data=body, verify=False)
    cookie = requests.utils.dict_from_cookiejar(s.cookies)
    return cookie


def cookie2string(cookie):
    s = ""
    for key in cookie:
        s += f"{key}={cookie[key]};"
    return s


def post_report_form(result, cookie):
    request_url = "https://my.stu.edu.cn/health-report/report/saveReport.do"

    cookie_str = cookie2string(cookie)
    request_header = {
        "Referer": f"https://my.stu.edu.cn/health-report/report/report.do?_t={int(time.time() * 1000)}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Origin": "https://my.stu.edu.cn",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Cookie": cookie_str
    }

    body = {
        'health': '良好',
        'familyHealth': '良好',
        'importantPersonType': 4,
        'dailyReport.afternoorBodyHeat': 36.4,
        'dailyReport.forenoonBodyHeat': 36.5,
        'dailyReport.hasCough': False,
        'dailyReport.hasShortBreath': False,
        'dailyReport.hasWeak': False,
        'dailyReport.hasFever': False,
        'dailyReport.exception': None,
        'dailyReport.treatment': None,
        'dailyReport.conclusion': None,
        'watchingInfoOutofStu.address': None,
        'watchingInfoOutofStu.startDate': None,
        'watchingInfoOutofStu.comment': None,
    }
    response = s.post(request_url, headers=request_header, data=body, verify=False)
    return response


def main():
    parser = ArgumentParser()
    parser.add_argument("-user", type=str)
    parser.add_argument("-password", type=str)
    args = parser.parse_args()

    # Step One, Get CAS
    try:
        result = get_cas_info()
        print("Step 1/3: Get CAS Protocal Info Done!")
    except Exception:
        print("Step 1/3: Get CAS Protocal Info Failed!")
        return


    # Step Two, Get Cookie
    try:
        cookie = login(result, user=args.user, psw=args.password)

        # Check Cookie Keys
        for key in ['CASTGC', '_UT_', 'uuid', 'JSESSIONID']:
            if key not in cookie:
                raise Exception('Cookie Missing!')
        print("Step 2/3: Login via SSO Success!")

    except Exception as ex:
        print("Step 2/3: Login via SSO Failed!")

    # Step Three, Submit Form
    try:
        resp = post_report_form(result, cookie)

        obj = json.loads(resp.content)
        if obj['success'] != True:
            raise Exception('Success=False')
        print(f"Step 3/3: Submit Health Report Done! {(obj)}")
    except Exception as ex:
        print("Step 3/3: Submit Health Report Failed!")

    print('Execution Done! HAVE A GOOD DAY')

if __name__ == "__main__":
    main()
