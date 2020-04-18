import pymysql
from datetime import datetime, timedelta

conn = pymysql.connect(host='localhost', user='root', password='withmeproject', database='my_test', autocommit=True, cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')

curs = conn.cursor()
# 3일이 넘은 게시글 (~ 4일 전) 게시글 삭제
before_3 = (datetime.today() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")

# 게시글 선택
sql = "select * from board2 where date < %s;"
curs.execute(sql, (before_3))
buffer1 = curs.fetchall()

# 게시글 삭제
sql = "delete from board2 where date < %s;"
curs.execute(sql, (before_3))

buffer2 = []
# 댓글 선택
sql = "select * from comment2 where inx=%s;"
for i in buffer1 :
    curs.execute(sql, (i['inx']))
    abc = curs.fetchall()
    buffer2.append(abc)

# 댓글 삭제
for i in buffer2 :
    for j in i :
        sql = "delete from comment2 where inx=%s;"
        curs.execute(sql, (j['inx']))
print('게시글 댓글 삭제 완료')
conn.close()

# save 테이블 있는 db 연결
conn = conn = pymysql.connect(host='localhost', user='root', password='withmeproject', database='log', autocommit=True, cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')
curs = conn.cursor()

sql = "insert into board2Save values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
for i in buffer1 :
    curs.execute(sql, (i['inx'], i['writer'], i['active'], i['title'], i['content'], i['start_time'], i['end_time'], i['max_count'], i['date'], i['vote_category1'], i['vote_category2'], i['vote_entry1'], i['vote_entry2'], i['party_entry'], i['good_entry'], i['good']))

sql = "insert into comment2Save values(%s, %s, %s, %s, %s);"
for i in buffer2 :
    for j in i :
        curs.execute(sql, (j['inx'], j['commenter'], j['comment_content'], j['comment_time'], j['active']))
print('게시글 댓글 Save 완료')
conn.close()
