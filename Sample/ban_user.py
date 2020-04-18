import hashlib
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='withmeproject',db='my_test', charset='utf8')
print('ID를 입력하세요', end='')
id=input()
result=hashlib.sha256(id.encode())
hashid=result.hexdigest()
print('최종확인 (y/n) : ', end='')
a=input()
if a=='y':
    sql="update user set id=%s where id=%s"
    curs=conn.cursor()
    curs.execute(sql,(hashid,id))
    conn.commit()
    conn.close()
else:
    exit()

