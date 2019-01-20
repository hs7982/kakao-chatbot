import urllib.request
import pymysql
import datetime
from bs4 import BeautifulSoup as bs
import passwd

pw = passwd.Passwd()

#학교 기본정보 코드
eduCode = 'pen.go.kr'
schoolCode = 'C100000478'

#중식, 석식 코드
lunch = '2'
dinner = '3'

def mysql_del():
    try:
        # db연결
        conn = pymysql.connect(host="localhost", user="root", passwd=pw.passwd, db="jungang_meal", charset='utf8')
        #curs생성
        curs = conn.cursor()
    except:
        print("db연결 중 오류가 발생했습니다. mysql_del")
    #데티어 비우기
    try:
        sql=("""TRUNCATE `week_meal_2`""")
        curs.execute(sql)
        conn.commit()
        sql=("""TRUNCATE `week_meal_3`""")
        curs.execute(sql)
        conn.commit()
        conn.close()
        print("기존 DB데이터를 비웠습니다.")
    except:
        print("db를 비우는 중 오류가 발생하였습니다.")

def mysql_in(day, meal, when):
    print("DB에 저장중입니다."+when+","+str(day))
    # db연결
    conn = pymysql.connect(host="localhost", user="root", passwd=pw.passwd, db="jungang_meal", charset='utf8')
    day = str(day)
    #curs생성
    curs = conn.cursor()

    #데티어 생성
    sql=("""INSERT INTO week_meal_"""+when+"""(day, meal) VALUES ('"""+ day + "', '" + meal + """')""")
    curs.execute(sql)
    conn.commit()
    conn.close()

def nies_parser(eduCode, schoolCode, when):
    now = datetime.datetime.now()
    print("NIES에서 주간 급식정보를 가져옵니다."+when)
    url = 'http://stu.'+ eduCode +'/sts_sci_md01_001.do?schulCode='+ schoolCode +'&schulCrseScCode=4&schMmealScCode='+ when +'&schYmd='+now.strftime('%Y.%m.%d')
    print(url)
    req = urllib.request.urlopen(url, timeout=3)
    soup = bs(req, 'html.parser')
    print("데이터 처리중..."+when)
    meal = soup.find_all('td', {'class':'textC'})[7:14]
    
    #0=일, 1=월, 2=화 ... 6=토
    today = 0
    while today < 7:
        menu = str(meal[today])
        menu = menu.replace('<td class="textC">', '').replace('</td>', '').replace('<br/>', '\n').replace('(중앙)','').replace('&amp;','&').replace('(중앙','').replace('(증앙)','').replace('<td class="textC last">','')
        for n in range(18, 0, -1):
            menu = menu.replace(str(n)+".", "")
        
        #정보가 없을경우
        if menu == '' or menu == ' ':
            menu = '급식 정보가 없습니다.\n'
        
        #db로 저장
        mysql_in(today, menu, when)

        today = today+1
print("NIES 급식 크롤러를 시작합니다.")
mysql_del()
nies_parser(eduCode, schoolCode, lunch)
nies_parser(eduCode, schoolCode, dinner)
print("성공")