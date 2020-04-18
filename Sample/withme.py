from flask import Flask, render_template, request, redirect, url_for, session, escape, flash, jsonify
from flask_paginate import Pagination, get_page_args
from datetime import datetime
import itertools
import pymysql
import random
import time
import ssl
import os
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import json

import urllib.request
import urllib.parse
from config import BaseConfig
from utils import *

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

def set_db():
	conn = pymysql.connect(host='localhost', user='root', password='withmeproject', database='my_test', autocommit=True, cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')
	return conn

@app.route('/',defaults={'page':0}, methods=['POST','GET'])
@app.route('/<int:page>')
def home(page):
	if 'username' in session :
		sql = "select count(*) from board2;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()

		total_cnt = curs.fetchone()
		total_cnt = total_cnt.pop('count(*)')
		per_page=10
		if total_cnt % 10 == 0 :
			total_page=int(total_cnt/per_page) -1
		else : 
			total_page=int(total_cnt/per_page)

		sql = "select * from board2 order by date desc limit %s offset %s;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql,(per_page,page*per_page))
		conn.close()

		data = curs.fetchall()

		btn_show = []
		current_entry = []
		date = [[], []]
		vote_show = [[], []]
		vote_entry = [[], []]
		vote=[[], []]

		now = datetime.now()
		for x in range(len(data)):
			date[0].append(data[x]['date'])
			date[0].append('')
			date[0][x*2+1] = (now-date[0][x*2]).seconds
			date[0][x*2] = (now-date[0][x*2]).days
			
			if data[x]['vote_entry1'] == None :
				vote[0].append(0)
			else :
				vote[0].append(len(data[x]['vote_entry1'].strip().split(',')) - 1)
			if data[x]['vote_entry2'] == None :
				vote[1].append(0)
			else :
				vote[1].append(len(data[x]['vote_entry2'].strip().split(',')) - 1)

			current_count = list(filter(None,list(str(data[x]['party_entry']).strip().split(','))))
			if 'None' in current_count:
				current_count.remove('None')
			if session.get('username') in current_count:
				btn_show.append(1)
			else:
				btn_show.append(0)
			current_entry.append(len(current_count))

			vote_count1 = list(filter(None,list(str(data[x]['vote_entry1']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count1.remove('None')
			if session.get('username') in vote_count1:
				vote_show[0].append(1)
			else:
				vote_show[0].append(0)
			vote_entry[0].append(len(vote_count1))

			vote_count2 = list(filter(None,list(str(data[x]['vote_entry2']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count2.remove('None')
			if session.get('username') in vote_count2:
				vote_show[1].append(1)
			else:
				vote_show[1].append(0)
			vote_entry[1].append(len(vote_count2))

        # 댓글
		sql = "select * from comment2;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()
		data2 = curs.fetchall()

		for i in range(len(data2)) :
			date[1].append(data2[i]['comment_time'])
			date[1].append('')
			date[1][i*2+1] = (now-date[1][i*2]).seconds
			date[1][i*2] = (now-date[1][i*2]).days
        
		sql = "select inx from board2 where find_in_set(%s, good_entry)"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		index = curs.fetchall()
		conn.close()
		return render_template('index.html', total_cnt=total_cnt, total_page=total_page, page=page, username=session.get('username'), btn_show=btn_show, current_entry=current_entry, vote_show=vote_show, vote_entry=vote_entry, board=data, comment=data2, date=date, liked=index, vote=vote)
	else:
		return render_template('signin.html')
		
@app.route('/search', methods=['POST', 'GET'])
def search() :
	if request.method == 'POST' and 'username' in session :
		search = request.form['search']
		if search == None:
			return redirect(url_for('home'))
		sql = "select * from board2 where title like %s or content like %s order by date desc;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql,('%' + search + '%', '%' + search + '%'))
		conn.close()

		data = curs.fetchall()

		btn_show = []
		current_entry = []
		date = [[], []]
		vote_show = [[], []]
		vote_entry = [[], []]
		vote=[[], []]

		now = datetime.now()
		for x in range(len(data)):
			date[0].append(data[x]['date'])
			date[0].append('')
			date[0][x*2+1] = (now-date[0][x*2]).seconds
			date[0][x*2] = (now-date[0][x*2]).days
			
			if data[x]['vote_entry1'] == None :
				vote[0].append(0)
			else :
				vote[0].append(len(data[x]['vote_entry1'].strip().split(',')) - 1)
			if data[x]['vote_entry2'] == None :
				vote[1].append(0)
			else :
				vote[1].append(len(data[x]['vote_entry2'].strip().split(',')) - 1)

			current_count = list(filter(None,list(str(data[x]['party_entry']).strip().split(','))))
			if 'None' in current_count:
				current_count.remove('None')
			if session.get('username') in current_count:
				btn_show.append(1)
			else:
				btn_show.append(0)
			current_entry.append(len(current_count))

			vote_count1 = list(filter(None,list(str(data[x]['vote_entry1']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count1.remove('None')
			if session.get('username') in vote_count1:
				vote_show[0].append(1)
			else:
				vote_show[0].append(0)
			vote_entry[0].append(len(vote_count1))

			vote_count2 = list(filter(None,list(str(data[x]['vote_entry2']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count2.remove('None')
			if session.get('username') in vote_count2:
				vote_show[1].append(1)
			else:
				vote_show[1].append(0)
			vote_entry[1].append(len(vote_count2))

        # 댓글
		sql = "select * from comment2;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()
		data2 = curs.fetchall()

		for i in range(len(data2)) :
			date[1].append(data2[i]['comment_time'])
			date[1].append('')
			date[1][i*2+1] = (now-date[1][i*2]).seconds
			date[1][i*2] = (now-date[1][i*2]).days
        
		sql = "select inx from board2 where find_in_set(%s, good_entry)"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		index = curs.fetchall()
		conn.close()
		return render_template('search.html', username=session.get('username'), btn_show=btn_show, current_entry=current_entry, vote_show=vote_show, vote_entry=vote_entry, board=data, comment=data2, date=date, liked=index, vote=vote)
	else:
		return render_template('signin.html')

@app.route('/qna', methods=['POST'])
def qna():
	if request.method == 'POST' and 'username' in session:
		sql = "insert into qna(writer, content, time) values(%s, %s, %s);"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (session.get('username'),request.form['content'],datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
		conn.close()
		return redirect(url_for('user'))
	else:
		return redirect(url_for('home'))

@app.route('/info')
def info():
	return render_template('info.html')

@app.route ('/ranking', methods=['POST', 'GET'])
def ranking() :
	if 'username' in session :
		sql = "select * from board2 where active!=1 and date(date)>= date(subdate(now(),interval 7 day))  order by good desc limit 10;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()
		data = curs.fetchall()

		btn_show = []
		current_entry = []
		date = [[], []]
		vote_show = [[], []]
		vote_entry = [[], []]
		vote=[[], []]

		username=session.get('username')

		now = datetime.now()
		for x in range(len(data)):
			date[0].append(data[x]['date'])
			date[0].append('')
			date[0][x*2+1] = (now-date[0][x*2]).seconds
			date[0][x*2] = (now-date[0][x*2]).days
			
			if data[x]['vote_entry1'] == None :
				vote[0].append(0)
			else :
				vote[0].append(len(data[x]['vote_entry1'].strip().split(',')) - 1)
			if data[x]['vote_entry2'] == None :
				vote[1].append(0)
			else :
				vote[1].append(len(data[x]['vote_entry2'].strip().split(',')) - 1)

			current_count = list(filter(None,list(str(data[x]['party_entry']).strip().split(','))))
			if 'None' in current_count:
				current_count.remove('None')
			if session.get('username') in current_count:
				btn_show.append(1)
			else:
				btn_show.append(0)
			current_entry.append(len(current_count))

			vote_count1 = list(filter(None,list(str(data[x]['vote_entry1']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count1.remove('None')
			if session.get('username') in vote_count1:
				vote_show[0].append(1)
			else:
				vote_show[0].append(0)
			vote_entry[0].append(len(vote_count1))

			vote_count2 = list(filter(None,list(str(data[x]['vote_entry2']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count2.remove('None')
			if session.get('username') in vote_count2:
				vote_show[1].append(1)
			else:
				vote_show[1].append(0)
			vote_entry[1].append(len(vote_count2))

        # 댓글
		sql = "select * from comment2;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()
		data2 = curs.fetchall()

		for i in range(len(data2)) :
			date[1].append(data2[i]['comment_time'])
			date[1].append('')
			date[1][i*2+1] = (now-date[1][i*2]).seconds
			date[1][i*2] = (now-date[1][i*2]).days
        
		sql = "select inx from board2 where find_in_set(%s, good_entry)"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		index = curs.fetchall()
		conn.close()
		return render_template('ranking.html', username=username, btn_show=btn_show, current_entry=current_entry, vote_show=vote_show, vote_entry=vote_entry, board=data, comment=data2, date=date, liked=index, vote=vote)
	else:
		return render_template('signin.html')

@app.route('/write_comment', methods = ['POST'])
def write_comment():
	if request.method == 'POST' and 'username' in session:
		index_comment = request.form['index_comment']
		comment       = request.form['comment']
		comment_time  = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

		sql  = "select active, writer, party_entry, vote_entry1, vote_entry2 from board2 where inx = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (index_comment))
		conn.close()
		data = curs.fetchone()
		active = data['active']
		writer = data['writer']
		party_entry  = data['party_entry']
		vote_entry1 = data['vote_entry1']
		vote_entry2 = data['vote_entry2']
		active = data['active']

		if active == 1 :
			if session.get('username') == writer:
				who = 1
			else:
				if party_entry != None:
					party_entry = list(filter(None,party_entry.split(',')))
					if session.get('username') in party_entry:
						who = 0
					else:
						who = -1
				else:
					who = -1
		elif active == 2 :
			who = -1
		elif active == 3 :
			if vote_entry1 != None :
				vote_entry1 = list(filter(None,vote_entry1.split(',')))
				if session.get('username') in vote_entry1:
					who = 2
				elif vote_entry2 != None :
					vote_entry2 = list(filter(None,vote_entry2.split(',')))
					if session.get('username') in vote_entry2:
						who = 3
					else :
						who = -1
				else :
					who = -1
			elif vote_entry2 != None :
				vote_entry2 = list(filter(None,vote_entry2.split(',')))
				if session.get('username') in vote_entry2 :
					who = 3
				else :
					who = -1
			else :
				who = -1

		sql = "insert into comment2 values(%s, %s, %s, %s, %s)"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql,(index_comment, session.get('username'), comment, comment_time, who))
		conn.close()
		'''
		sql = "update comment2 set active=%s where inx=%s and commenter=%s;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (who, index_comment, session.get('username')))
		conn.close()
		'''
		return {'result':'done', 'who':who, 'msg':comment, 'active':active}

@app.route('/myboard', methods=['POST', 'GET'])
def myboard():
	if 'username' in session :
		sql = "select * from board2 where writer=%s;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql,session.get('username'))
		conn.close()

		data = curs.fetchall()[::-1]

		btn_show = []
		current_entry = []
		date = [[], []]
		vote_show = [[], []]
		vote_entry = [[], []]
		vote=[[], []]

		now = datetime.now()
		for x in range(len(data)):
			date[0].append(data[x]['date'])
			date[0].append('')
			date[0][x*2+1] = (now-date[0][x*2]).seconds
			date[0][x*2] = (now-date[0][x*2]).days
			
			if data[x]['vote_entry1'] == None :
				vote[0].append(0)
			else :
				vote[0].append(len(data[x]['vote_entry1'].strip().split(',')) - 1)
			if data[x]['vote_entry2'] == None :
				vote[1].append(0)
			else :
				vote[1].append(len(data[x]['vote_entry2'].strip().split(',')) - 1)

			current_count = list(filter(None,list(str(data[x]['party_entry']).strip().split(','))))
			if 'None' in current_count:
				current_count.remove('None')
			if session.get('username') in current_count:
				btn_show.append(1)
			else:
				btn_show.append(0)
			current_entry.append(len(current_count))

			vote_count1 = list(filter(None,list(str(data[x]['vote_entry1']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count1.remove('None')
			if session.get('username') in vote_count1:
				vote_show[0].append(1)
			else:
				vote_show[0].append(0)
			vote_entry[0].append(len(vote_count1))

			vote_count2 = list(filter(None,list(str(data[x]['vote_entry2']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count2.remove('None')
			if session.get('username') in vote_count2:
				vote_show[1].append(1)
			else:
				vote_show[1].append(0)
			vote_entry[1].append(len(vote_count2))

        # 댓글
		sql = "select * from comment2;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()
		data2 = curs.fetchall()

		for i in range(len(data2)) :
			date[1].append(data2[i]['comment_time'])
			date[1].append('')
			date[1][i*2+1] = (now-date[1][i*2]).seconds
			date[1][i*2] = (now-date[1][i*2]).days
        
		sql = "select inx from board2 where find_in_set(%s, good_entry)"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		index = curs.fetchall()
		conn.close()
		return render_template('myboard.html', username=session.get('username'), btn_show=btn_show, current_entry=current_entry, vote_show=vote_show, vote_entry=vote_entry, board=data, comment=data2, date=date, liked=index, vote=vote)
	else:
		return render_template('signin.html')

@app.route('/board_delete',methods=['POST'])
def board_delete():
	if request.method=='POST':
		inx=request.form['index_board']
		sql="delete from board2 where inx=%s"
		conn=set_db()
		curs=conn.cursor()
		curs.execute(sql,inx)
		conn.close()
		return {'state':'done'}

@app.route('/bookmark', methods=['POST', 'GET'])
def bookmark():
	if 'username' in session :
		sql = "select * from board2 where find_in_set(%s, party_entry);"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		conn.close()

		data = curs.fetchall()[::-1]

		btn_show = []
		current_entry = []
		date = [[], []]
		vote_show = [[], []]
		vote_entry = [[], []]
		vote=[[], []]

		now = datetime.now()
		for x in range(len(data)):
			date[0].append(data[x]['date'])
			date[0].append('')
			date[0][x*2+1] = (now-date[0][x*2]).seconds
			date[0][x*2] = (now-date[0][x*2]).days
			
			if data[x]['vote_entry1'] == None :
				vote[0].append(0)
			else :
				vote[0].append(len(data[x]['vote_entry1'].strip().split(',')) - 1)
			if data[x]['vote_entry2'] == None :
				vote[1].append(0)
			else :
				vote[1].append(len(data[x]['vote_entry2'].strip().split(',')) - 1)

			current_count = list(filter(None,list(str(data[x]['party_entry']).strip().split(','))))
			if 'None' in current_count:
				current_count.remove('None')
			if session.get('username') in current_count:
				btn_show.append(1)
			else:
				btn_show.append(0)
			current_entry.append(len(current_count))

			vote_count1 = list(filter(None,list(str(data[x]['vote_entry1']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count1.remove('None')
			if session.get('username') in vote_count1:
				vote_show[0].append(1)
			else:
				vote_show[0].append(0)
			vote_entry[0].append(len(vote_count1))

			vote_count2 = list(filter(None,list(str(data[x]['vote_entry2']).strip().split(','))))
			if 'None' in vote_count1:
				vote_count2.remove('None')
			if session.get('username') in vote_count2:
				vote_show[1].append(1)
			else:
				vote_show[1].append(0)
			vote_entry[1].append(len(vote_count2))

        # 댓글
		sql = "select * from comment2;"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql)
		conn.close()
		data2 = curs.fetchall()

		for i in range(len(data2)) :
			date[1].append(data2[i]['comment_time'])
			date[1].append('')
			date[1][i*2+1] = (now-date[1][i*2]).seconds
			date[1][i*2] = (now-date[1][i*2]).days
        
		sql = "select inx from board2 where find_in_set(%s, good_entry)"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		index = curs.fetchall()
		conn.close()
		return render_template('bookmark.html', username=session.get('username'), btn_show=btn_show, current_entry=current_entry, vote_show=vote_show, vote_entry=vote_entry, board=data, comment=data2, date=date, liked=index, vote=vote)
	else:
		return render_template('signin.html')

@app.route('/free_liked', methods=['POST', 'GET'])
def free_liked():
	if request.method == 'POST' and 'username' in session:
		inx = request.form['heart_index']

		sql = "select good_entry, good from board2 where inx = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (inx))
		conn.close()
		data = curs.fetchone()

		userliker = data['good_entry']
		good = data['good']

		if userliker != None:
			userliker = list(filter(None, userliker.split(',')))
			if not session.get('username') in userliker:
				good += 1
				userliker.append(session.get('username') + ',')
				userliker = str(','.join(userliker))
				sql = "update board2 set good_entry=%s,good=%s where inx=%s"
				conn = set_db()
				curs = conn.cursor()
				curs.execute(sql, (userliker,good,inx))
				conn.close()
				return {'state':'done','good':good}
		else:
			good += 1
			sql = "update board2 set good_entry=%s,good=%s where inx=%s"
			conn = set_db()
			curs = conn.cursor()
			curs.execute(sql, (session.get('username')+',',good,inx))
			conn.close()
			return {'state':'done','good':good}
	else:
		return redirect(url_for('freepage'))

@app.route('/free_disliked', methods=['POST', 'GET'])
def free_disliked():
	if request.method == 'POST' and 'username' in session:
		inx = request.form['heart_index']

		sql = "select good_entry, good from board2 where inx=%s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (inx))
		conn.close()
		data = curs.fetchone()

		userliker = data['good_entry']
		good = data['good']

		if userliker != None:
			userliker = list(filter(None, userliker.split(',')))
			if session.get('username') in userliker:
				userliker.remove(session.get('username'))
				if not userliker:
					good -= 1
					sql = "update board2 set good_entry=NULL,good=%s where inx=%s"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (good, inx))
					conn.close()
					return {'state':'done','good':good}
				else:
					good -= 1
					userliker = str(','.join(userliker)) + ','
					sql = "update board2 set good_entry=%s, good=%s where inx=%s"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (userliker, good, inx))
					conn.close()
					return {'state':'done','good':good}
			else:
				return {'state':'None'}
		else:
			return {'state':'None'}
	else:
		return redirect(url_for('home'))

@app.route('/reverify1',methods=['POST', 'GET'])
def reverify1():
	if 'username' in session:
		return render_template('delete_reverify.html')
	else:
		return redirect(url_for('home'))

@app.route('/delete/reverify',methods=['POST'])
def delete_reverify():
	if request.method=='POST' and 'username' in session:
		uid=request.form['re_v_id']
		pwd=request.form['re_v_pwd']

		if uid==session.get('username'):
			sql = "select * from user where id = %s and pwd = %s"
			conn = set_db()
			curs=conn.cursor()
			curs.execute(sql,(session.get('username'),pwd))
			conn.close()
			result=curs.fetchone()
			if result:
				sql="delete from user where id=%s;"
				conn = set_db()
				curs=conn.cursor()
				curs.execute(sql,session.get('username'))
				conn.close()
				session.pop('username', None)
				session.pop('email', None)

				flash('회원 탈퇴 완료','danger')
				return redirect(url_for('home'))
			else:
				return render_template('delete_reverify.html')
		else:
			return render_template('delete_reverify.html')
	else:
		return redirect(url_for('home'))

@app.route('/reverify2',methods=['POST', 'GET'])
def reverify2():
	if 'username' in session:
		return render_template('change_reverify.html')
	else:
		return redirect(url_for('home'))

@app.route('/change/reverify',methods=['POST'])
def change_reverify():
	if request.method=='POST' and 'username' in session:
		uid=request.form['re_v_id']
		pwd=request.form['re_v_pwd']

		if uid == session.get('username'):
			sql = "select id from user where id = %s and pwd = %s"
			conn = set_db()
			curs=conn.cursor()
			curs.execute(sql,(session.get('username'),pwd))
			conn.close()
			result=curs.fetchone()
			if result:
				return render_template('change.html')
			else:
				return render_template('change_reverify.html')
		else:
			return render_template('change_reverify.html')
	else:
		return redirect(url_for('home'))

@app.route('/change',methods=['POST'])
def change():
	if request.method=='POST' and 'username' in session:
		pa=request.form['pass']
		sql="update user set pwd=%s where id=%s"
		conn = set_db()
		curs=conn.cursor()
		curs.execute(sql,(pa,session.get('username')))
		conn.close()
		flash('정보 변경 완료!','info')
		return redirect(url_for('user'))
	else:
		return redirect(url_for('home'))

@app.route('/entry', methods = ['POST'])
def entry():
	if request.method == 'POST' and 'username' in session:
		index_board  = request.form['index_board']

		sql = "select writer, party_entry from board2 where inx = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (index_board))
		conn.close()
		data = curs.fetchone()

		writer = data['writer']
		entry = data['party_entry']

		if session.get('username') != writer:
			if entry != None:
				entry = list(filter(None,entry.split(',')))
				if not session.get('username') in entry:
					# 참가 완료
					entry.append(session.get('username') + ',')
					entry = str(','.join(entry))

					sql = "update board2 set party_entry=%s where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (entry, index_board))
					conn.close()

					sql = "update comment2 set active=0 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))

					return {'state':'done'}
				else:
					# 이미 참가함
					return {'state':'None'}
			else: # entry = None
				# 첫번째  참가
				sql = "update board2 set party_entry=%s where inx=%s;"
				conn = set_db()
				curs = conn.cursor()
				curs.execute(sql, (session.get('username')+',', index_board))
				conn.close()

				sql = "update comment2 set active=0 where inx=%s and commenter=%s;"
				conn = set_db()
				curs = conn.cursor()
				curs.execute(sql, (index_board, session.get('username')))
				conn.close()
				return {'state':'done'}

		return '',204

@app.route('/cancel_entry', methods = ['POST'])
def cancel_entry():
	if request.method == 'POST' and 'username' in session:
		index_board = request.form['index_board']

		sql = "select party_entry from board2 where inx = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (index_board))
		conn.close()
		data = curs.fetchone()

		entry = data['party_entry']

		if entry != None:
			entry = list(filter(None,entry.split(',')))
			if session.get('username') in entry:
				# entry 안에 id 가 있을 경우
				entry.remove(session.get('username'))
				if not entry:
					sql = "update board2 SET party_entry = NULL where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, index_board)
					conn.close()

					sql = "update comment2 set active=-1 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))

					return {'state':'done'}
				else:
					entry = str(','.join(entry)) + ','
					sql = "update board2 set party_entry=%s where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (entry, index_board))
					conn.close()

					sql = "update comment2 set active=-1 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))

					return {'state':'done'}
			else:
				#아무것도 수행안함
				return {'state':'None'}
		else: # entry = None
			# 아무것도 수행 안함
			return {'state':'None'}

		return '',204

@app.route('/user', methods = ['GET'])
def user():
	if 'username' in session:
		sql = "select id,email,sex,signup from user where id = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, session.get('username'))
		conn.close()
		userdata = curs.fetchone()

		if userdata['sex'] == 1:
			sex = '남자'
		else:
			sex = '여자'
		signup_data = userdata['signup'].strftime('%Y-%m-%d')
		items = {'아이디':userdata['id'], '이메일':userdata['email'], '성별':sex, '가입일':signup_data}
		return render_template('user.html', items=items)
	else:
		return redirect(url_for('home'))
    
@app.route('/write_party', methods = ['POST', 'GET'])
def write_party():
	if request.method == 'POST' and 'username' in session:
		title 	   = request.form['title']
		content    = request.form['content']
		max_count  = request.form['max_count']
		start 	   = "{0} {1}".format(request.form['start_date'], request.form['start_time'])
		start_time = datetime.strptime(start, "%Y-%m-%d %H:%M")
		end	   = "{0} {1}".format(request.form['end_date'], request.form['end_time'])
		end_time   = datetime.strptime(end, "%Y-%m-%d %H:%M")
		date 	   = datetime.today().strftime("%Y-%m-%d %H:%M")

		sql = "insert into board2(writer, active, title, content, start_time, end_time, max_count, date) values(%s, 1, %s, %s, %s, %s, %s, %s);"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (session.get('username'), title, content, start_time, end_time, max_count, date))
		conn.close()
		return redirect(url_for('home'))
	else:
		return render_template('signin.html')

@app.route('/write_free', methods = ['POST', 'GET'])
def write_free():
	if request.method == 'POST' and 'username' in session:
		content    = request.form['content']
		date 	   = datetime.today().strftime("%Y-%m-%d %H:%M")

		sql = "insert into board2(writer, active, content, date) values(%s, 2, %s, %s);"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (session.get('username'), content, date))
		conn.close()
		return redirect(url_for('home'))
	else:
		return render_template('signin.html')

@app.route('/write_vote', methods = ['POST', 'GET'])
def write_vote():
    if request.method == 'POST' and 'username' in session:
        content        = request.form['content']
        vote_category1 = request.form['vote_category1']
        vote_category2 = request.form['vote_category2']
        date 	       = datetime.today().strftime("%Y-%m-%d %H:%M")

        sql = "insert into board2(writer, active, content, date, vote_category1, vote_category2) values(%s, 3, %s, %s, %s, %s);"
        conn = set_db()
        curs = conn.cursor()
        curs.execute(sql, (session.get('username'), content, date, vote_category1, vote_category2))
        conn.close()
        return redirect(url_for('home'))
    else:
        return render_template('signin.html')

@app.route('/signin',methods = ['POST', 'GET'])
def signin():
	if request.method == 'POST':
		id = request.form['userID']
		pwd = request.form['userPWD']

		sql = "select id from user where id = %s and pwd = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (id, pwd))
		conn.close()
		account = curs.fetchone()

		if account:
			sql = "select id from user where id=%s and active=0;"
			conn = set_db()
			curs = conn.cursor()
			curs.execute(sql, (id))
			conn.close()
			auth_account = curs.fetchone()

			if auth_account: # 이메일 인증 X
				flash('이메일 인증을 해주세요!', 'warning')
				return redirect(url_for('home'))
			else: # 인증 완료
				session['username'] = id
				return redirect(url_for('home'))
		else:
			flash('아이디 또는 비밀번호가 틀렸습니다!', 'danger')
			return redirect(url_for('home'))
	else:
		return render_template('signin.html')

@app.route('/signup',methods = ['POST', 'GET'])
def signup():
	if request.method == 'POST' and 'userID' in request.form and 'userPWD' in request.form:
		if request.form['userPWD'] == request.form['userRePWD']:
			id     = request.form['userID']
			pwd    = request.form['userPWD']
			email  = request.form['email']
			sex    = request.form['sex']
			birth  = request.form['birth']
			time   = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

			sql = "select * from user where id = %s"
			conn = set_db()
			curs = conn.cursor()
			curs.execute(sql, (id))
			conn.close()
			account = curs.fetchone()

			sql = "select * from user where email = %s"
			conn = set_db()
			curs = conn.cursor()
			curs.execute(sql, (email))
			conn.close()
			email_exist = curs.fetchone()

			if account:
				# Account already exists!
				flash('아이디가 이미 존재합니다!')
				return redirect(url_for('signup'))
			elif (len(pwd) >= 20) or (len(id) >= 21) or (len(id) <= 5) or (len(pwd) <= 5):
				flash('아이디 또는 패스워드 길이를 확인해주세요!')
				return redirect(url_for('signup'))
			elif email_exist:
				flash('이미 존재하는 이메일입니다!')
				return redirect(url_for('signup'))
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				# Invalid email address!
				flash('이메일을 다시 확인해주세요!')
				return redirect(url_for('signup'))
			elif not re.match(r'[A-Za-z0-9]+', id):
				# Username must contain only characters and numbers!
				flash('영어 또는 숫자로 입력해주세요!')
				return redirect(url_for('signup'))
			elif not id or not pwd or not email:
				# Please fill out the form!
				flash('양식을 다시 확인해주세요!')
				return redirect(url_for('signup'))
			else:
				# success
				if not check_email_validation(email):
					flash('이메일이 유효하지 않습니다!')
					return redirect(url_for('signup'))
				else:
					session['email'] = email
					send_confirmation_mail(email, id)

					sql = "insert into user(id, pwd, email, signup, sex, birth) values(%s, %s, %s, %s, %s, %s)"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (id, pwd, email, time, sex, birth))
					conn.close()

					flash('회원가입에 성공했습니다!', 'success')
					return redirect(url_for('home'))
		else:
			flash('다시 입력해주세요!')
			return redirect(url_for('home'))
	else:
		return render_template('signup.html')

@app.route('/vote_entry1',methods=['POST','GET'])
def vote_entry1():
    if request.method == 'POST' and 'username' in session:
        vote_entry=request.form['before']
        sql = "select vote_entry1, vote_entry2 from board2 where inx = %s"
        conn = set_db()
        curs = conn.cursor()
        curs.execute(sql, vote_entry)
        conn.close()
        data = curs.fetchone()
        entry = data['vote_entry1']
		
        if data['vote_entry1'] == None :
            vote1 = 1
        else :
            vote1 = len(data['vote_entry1'].strip().split(','))
        if data['vote_entry2'] == None :
            vote2 = 0
        else :
            vote2 = len(data['vote_entry2'].strip().split(',')) - 1

        if entry != None:
            entry = list(filter(None, entry.split(',')))
            if not session.get('username') in entry :
                entry.append(session.get('username') + ',')
                entry = str(','.join(entry))
                sql="update board2 set vote_entry1=%s where inx=%s"
                conn = set_db()
                curs = conn.cursor()
                curs.execute(sql,(entry,vote_entry))
                conn.close()

                sql = "update comment2 set active=2 where inx=%s and commenter=%s;"
                conn = set_db()
                curs = conn.cursor()
                curs.execute(sql, (vote_entry, session.get('username')))
                conn.close()

                return {'state':'done', 'vote1':vote1, 'vote2':vote2}
        else:
            sql = "update board2 set vote_entry1=%s where inx=%s"
            conn = set_db()
            curs = conn.cursor()
            curs.execute(sql, (session.get('username')+',',vote_entry))
            conn.close()

            sql = "update comment2 set active=2 where inx=%s and commenter=%s;"
            conn = set_db()
            curs = conn.cursor()
            curs.execute(sql, (vote_entry, session.get('username')))
            conn.close()

            return {'state':'done', 'vote1':vote1, 'vote2':vote2}
        return {'state':'done'}
    else:
        return redirect(url_for('home'))

@app.route('/vote_entry2',methods=['POST','GET'])
def vote_entry2():
    if request.method == 'POST' and 'username' in session:
        vote_entry=request.form['after']
        sql = "select vote_entry1, vote_entry2 from board2 where inx = %s"
        conn = set_db()
        curs = conn.cursor()
        curs.execute(sql, vote_entry)
        conn.close()
        data = curs.fetchone()
        entry = data['vote_entry2']

        if data['vote_entry1'] == None :
            vote1 = 0
        else :
            vote1 = len(data['vote_entry1'].strip().split(',')) -1
        if data['vote_entry2'] == None :
            vote2 = 1
        else :
            vote2 = len(data['vote_entry2'].strip().split(','))

        if entry != None:
            entry = list(filter(None, entry.split(',')))
            if not session.get('username') in entry:
                entry.append(session.get('username') + ',')
                entry = str(','.join(entry))
                sql="update board2 set vote_entry2=%s where inx=%s"
                conn = set_db()
                curs = conn.cursor()
                curs.execute(sql,(entry,vote_entry))
                conn.close()

                sql = "update comment2 set active=3 where inx=%s and commenter=%s;"
                conn = set_db()
                curs = conn.cursor()
                curs.execute(sql, (vote_entry, session.get('username')))
                conn.close()

                return {'state':'done', 'vote1':vote1, 'vote2':vote2}
        else:
            sql = "update board2 set vote_entry2=%s where inx=%s"
            conn = set_db()
            curs = conn.cursor()
            curs.execute(sql, (session.get('username')+',',vote_entry))
            conn.close()

            sql = "update comment2 set active=3 where inx=%s and commenter=%s;"
            conn = set_db()
            curs = conn.cursor()
            curs.execute(sql, (vote_entry, session.get('username')))
            conn.close()

            return {'state':'done', 'vote1':vote1, 'vote2':vote2}
        return {'state':'done'}
    else:
        return redirect(url_for('home'))

@app.route('/cancel_vote_entry',methods=['POST','GET'])
def cancel_vote_entry():
	if request.method == 'POST' and 'username' in session:
		index_board = request.form['index_board']

		sql = "select vote_entry1, vote_entry2 from board2 where inx = %s"
		conn = set_db()
		curs = conn.cursor()
		curs.execute(sql, (index_board))
		conn.close()
		data = curs.fetchone()

		entry1 = data['vote_entry1']
		entry2 = data['vote_entry2']

		if entry1 != None :
			if session.get('username') in entry1 :
				if data['vote_entry2'] == None :
					vote2 = 0
				else :
					vote2 = len(data['vote_entry2'].strip().split(',')) - 1
				vote1 = len(data['vote_entry1'].strip().split(',')) - 2
				entry1 = list(filter(None,entry1.split(',')))
				entry1.remove(session.get('username'))

				if not entry1:
					sql = "update board2 SET vote_entry1 = NULL where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, index_board)
					conn.close()

					sql = "update comment2 set active=-1 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))
					conn.close()

					return {'state':'done', 'vote1':vote1, 'vote2':vote2}
				else:
					entry1 = str(','.join(entry1)) + ','
					sql = "update board2 set vote_entry1=%s where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (entry1, index_board))
					conn.close()

					sql = "update comment2 set active=-1 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))
					conn.close()

					return {'state':'done', 'vote1':vote1, 'vote2':vote2}

		if entry2 != None :
			if session.get('username') in entry2 and entry2 != None :
				if data['vote_entry1'] == None :
					vote1 = 0
				else :
					vote1 = len(data['vote_entry1'].strip().split(',')) - 1
				vote2 = len(data['vote_entry2'].strip().split(',')) - 2
				entry2 = list(filter(None,entry2.split(',')))
				entry2.remove(session.get('username'))

				if not entry2:
					sql = "update board2 SET vote_entry2 = NULL where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, index_board)
					conn.close()

					sql = "update comment2 set active=-1 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))
					conn.close()

					return {'state':'done', 'vote1':vote1, 'vote2':vote2}
				else:
					entry2 = str(','.join(entry2)) + ','
					sql = "update board2 set vote_entry2=%s where inx=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (entry2, index_board))
					conn.close()

					sql = "update comment2 set active=-1 where inx=%s and commenter=%s;"
					conn = set_db()
					curs = conn.cursor()
					curs.execute(sql, (index_board, session.get('username')))
					conn.close()

					return {'state':'done', 'vote1':vote1, 'vote2':vote2}
			else :
				return {'state':'done'}

			return {'state':'done'}

		return '', 204

@app.route('/confirm/<token>')
def confirm_email(token):
	try:
		data = confirm_token(token)
	except:
		flash('이메일 인증 토큰이 만료되었습니다!', 'danger')
		return redirect(url_for('home'))

	# DB user.activate = True
	sql = "update user set active=%s where id=%s"
	conn = set_db()
	curs = conn.cursor()
	curs.execute(sql, (1, data['username']))
	conn.close()
	flash('이메일 인증에 성공했습니다!!', 'primary')

	return redirect(url_for('signin'))

@app.route('/resend')
def resend_confirmation():
	send_confirmation_mail(session['email'], session['username'])

@app.route("/logout", methods=['POST'])
def logout():
	if request.method == 'POST':
		session.pop('username', None)
		session.pop('email', None)
		flash('로그아웃 처리 성공!', 'info')
		return redirect(url_for('home'))

if __name__ == "__main__":
    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context.load_cert_chain('ssl/cert.pem', 'ssl/key.pem')
    app.run(host='0.0.0.0', port=80) #ssl_context=context
    #app.run(host='202.182.127.157', port=5000, debug=True)

