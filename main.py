import os
from flask import Flask, request, jsonify
import datetime
import pymysql
import passwd
application = Flask(__name__)

pw = passwd.Passwd()

def mysql_conn():
    try:
        global conn, curs
        # db연결
        conn = pymysql.connect(
            host="localhost", 
            user="root", 
            passwd=pw.passwd, 
            db="jungang_meal", 
            charset='utf8')
        #curs생성
        curs = conn.cursor()
    except:
        print("db연결 중 오류가 발생했습니다. mysql_del")

def mysql_lunch(day):
    #중식
    mysql_conn()
    sql=("""SELECT meal FROM `week_meal_2`""")
    curs.execute(sql)
    n = 0
    while n < day+1:
        lunch = curs.fetchone()
        n = n+1
    conn.commit()
    conn.close()

    return lunch

def mysql_dinner(day):
    #석식
    mysql_conn()
    sql=("""SELECT meal FROM `week_meal_3`""")
    curs.execute(sql)
    n = 0
    while n < day+1:
        dinner = curs.fetchone()
        n = n+1
    conn.commit()
    conn.close()

    return dinner

def mysql_sc(month):
    #학사일정
    mysql_conn()
    sql=("""SELECT * FROM `sc_schedule` WHERE `month` LIKE '%s' ORDER BY `month` DESC""" %month)
    try:
        curs.execute(sql)
        schedule = curs.fetchone()
        schedule = schedule[1]
        conn.commit
        conn.close()
    except:
        schedule = "%s: 해당월의 정보가 없습니다.\n학년도 시작 이후 정보가 업데이트 될 예정입니다."%month
    
    return schedule

@application.route('/')
def Home():
    page = "Algorithm Factory api server"
    return page

@application.route('/log')
def log():
    logf = open("log.log", 'r')
    logr = logf.read()
    logf.close()
    return logr

@application.route('/schedule', methods=['POST'])
def schedule():
    msg = ''
    dataReceive = ''
    dataReceive = request.get_json()
    content = dataReceive['action']
    params = content['params']
    scm_data = params['schedule']
    dt = datetime.datetime.now()

    if scm_data == "이번달":
        month=dt.strftime("%y")+str(dt.month)
        schedule = mysql_sc(month)

        msg = dt.strftime("%Y년 %m월")+"의 학사일정 입니다."

        dataSend = {
            "version" : "2.0",
            "data" : {
                "scmonth" : msg,
                "schedule" : schedule,
            }
        }
    
    elif scm_data == "다음달":
        month=dt.month+1
        if month < 13:
            month = dt.strftime("%y")+str(month)
        else:
            year = str(dt.year+1)
            month = year[2:]+str(month-12)
        schedule = mysql_sc(month)

        msg = "20%s년 %s월의 학사일정 입니다."%(month[:2],month[2:])

        dataSend = {
            "version" : "2.0",
            "data" : {
                "scmonth" : msg,
                "schedule" : schedule,
            }
        }

    #사용자가 월을 직접 입력하는 경우
    elif scm_data[0] == "n":
        today_mon = dt.month
        today_y = dt.year
        mon_data = scm_data[1:]

        if mon_data == "1월" or mon_data == "2월":
            # 한 해의 학년도는 2월에 종료됨
            #ex: 2019년 12월에 2월 정보를 요청 -> 19년 2월이 아닌 2020년 2월 정보 제공

            if today_mon > 2:
                year = str(today_y+1)
                month = year[2:]+mon_data[0:-1]
            else:
                year = str(today_y-1)
                month = year[2:]+mon_data[0:-1]
        
        #1,2월에 3~12월 요청시 해당 학년도의 정보를 제공하기 위함
        #ex: 2020년 1월에 11월 정보 요청 -> 2019년 11월 정보 제공
        elif today_mon > 2:
            month = dt.strftime("%y")+mon_data[0:-1]
        else:
            year = str(today_y-1)
            month = year[2:]+mon_data[0:-1]

        msg = "20%s년 %s월의 학사일정 입니다."%(month[:2], mon_data[0:-1])
        schedule = mysql_sc(month)

        dataSend = {
            "version" : "2.0",
            "data" : {
                "scmonth" : msg,
                "schedule" : schedule,
            }
        }

    else:
        dataSend = {
            "version" : "2.0",
            "data" : {
                "scmonth" : "죄송합니다.",
                "schedule" : "오류가 발생하였습니다. 잠시 후 다시 시도하거나, 관리자에게 문의해주세요.",
            }
        }

    return jsonify(dataSend)

@application.route('/meal', methods=['POST'])
def Meal():
    msg = ''
    dataReceive = ''
    dataReceive = request.get_json()
    content = dataReceive['action']
    params = content['params']
    day_data = params['meal_day']
    dt = datetime.datetime.now()

    if day_data == "오늘":
        day = dt.weekday()
        if day == 6:
            lunch = mysql_lunch(0)
            dinner = mysql_dinner(0)
        else:
            lunch = mysql_lunch(day+1)
            dinner = mysql_dinner(day+1)
        msg = "[중식]\n" + str(lunch[0]) + "\n[석식]\n" + str(dinner[0])+"\n※위 식단은 학교나 시장 사정에 의하여 변경될 수 있습니다."
        dataSend = {
            "version" : "2.0",
            "data" : {
                "day" : "오늘의 식단입니다.",
                "meal" : msg,
            }
        }

    elif day_data == "내일":
        day = dt.weekday()
        if day == 6:
            lunch = mysql_lunch(1)
            dinner = mysql_dinner(1)
        elif day == 5:
            lunch = mysql_lunch(0)
            dinner = mysql_dinner(0)
        else:
            lunch = mysql_lunch(day+2)
            dinner = mysql_dinner(day+2)

        msg = "[중식]\n" + str(lunch[0]) + "\n[석식]\n" + str(dinner[0])+"\n※위 식단은 학교나 시장 사정에 의하여 변경될 수 있습니다."
        dataSend = {
            "version" : "2.0",
            "data" : {
                "day" : "내일의 식단입니다.",
                "meal" : msg,
            }
        }
    
    #요일을 직접 입력하는 경우
    elif day_data[1:] == "요일":        
        if day_data == "월요일":
            sel_day = 1
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)

        elif day_data == "화요일":
            sel_day = 2
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)

        elif day_data == "수요일":
            sel_day = 3
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)

        elif day_data == "목요일":
            sel_day = 4
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)

        elif day_data == "금요일":
            sel_day = 5
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)
        
        elif day_data == "토요일":
            sel_day = 6
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)

        elif day_data == "일요일":
            sel_day = 0
            lunch = mysql_lunch(sel_day)
            dinner = mysql_dinner(sel_day)
        
        else:
            print("Error")

        msg = "[중식]\n" + str(lunch[0]) + "\n[석식]\n" + str(dinner[0])+"\n※위 식단은 학교나 시장 사정에 의하여 변경될 수 있습니다."
        
        day = dt.weekday()

        #이미 지나간 요일일 경우 안내
        #토요일에 월요일의 정보를 요청 -> 이미 제공된 급식 정보임을 안내
        if day+1 > sel_day:
            past_msg = "[안내] 이미 제공된 " +day_data+ "의 식단을 표시중입니다.\n다음주의 식단 정보는 일요일에 업데이트되니 참고 바랍니다.\n\n"
        else:
            past_msg = ""

        dataSend = {
            "version" : "2.0",
            "data" : {
                "day" : day_data + "의 식단입니다.",
                "meal" : past_msg + msg,
            }
        }

    else:
        dataSend = {
            "version" : "2.0",
            "data" : {
                "day" : "죄송합니다.",
                "meal" : "오류가 발생하였습니다. 잠시 후 다시 시도하거나, 관리자에게 문의해주세요.",
            }
        }
    return jsonify(dataSend)

if __name__ == "__main__":
    application.run(host='0.0.0.0')