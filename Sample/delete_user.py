import pymysql

conn = pymysql.connect(host='localhost', user='root', password='withmeproject', db='my_test', port=3306, charset='utf8')

cursor = conn.cursor()
sql = "delete from user;"
cursor.execute(sql)
conn.commit()
conn.close()
