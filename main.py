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

@application.route('/')
def Home():
    page = "Algorithm Factory api server"
    return page

@application.route('/meal', methods=['POST'])
def Meal():
    msg = ''
    dataReceive = ''
    dataReceive = request.get_json()
    content = dataReceive['action']
    params = content['params']
    day_data = params['meal_day']

    if day_data == "오늘":
        dt = datetime.datetime.now()
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
        dt = datetime.datetime.now()
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
        
        dt = datetime.datetime.now()
        day = dt.weekday()
        if day+1 > sel_day:
            past_msg = "[안내] 이미 제공된 " +day_data+ "의 식단을 표시중입니다.\n다음주의 식단 정보는 일요일에 업데이트되니 참고 바랍니다.\n\n"
        else:
            past_msg = ""
        
        print(day_data)
        print("오늘"+str(day+1))
        print("요청"+str(sel_day))

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