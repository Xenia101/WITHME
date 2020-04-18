'''
	function tools for email validation
'''
#-*- coding:utf-8 -*-
import smtplib
from validate_email import validate_email
from itsdangerous import URLSafeTimedSerializer
from flask import Flask, url_for, render_template
from config import BaseConfig

SECRET_KEY = BaseConfig.SECRET_KEY
SALT = BaseConfig.SECURITY_PASSWORD_SALT
MAIL_SERVER = BaseConfig.MAIL_SERVER

def generate_confirmation_token(email, username):
	serializer = URLSafeTimedSerializer( SECRET_KEY )
	print('serializer', serializer)
	return serializer.dumps({'email':email, 'username':username}, salt=SALT)

def confirm_token(token, expiration=3600):
	serializer = URLSafeTimedSerializer( SECRET_KEY )
	try:
		result = serializer.loads(token, salt=SALT, max_age=expiration)
	except:
		return False
	return result

def check_email_validation(email):
	print('email', email)
	# valid = validate_email(email, verify=True)
	# verify option is for checking if that email exists
	# default is False
	# default just examine wether the input email format is correct
	valid = validate_email(email)
	print('valid', valid)
	return valid

def send_mail(email, template):
	username = 'withme.team.akk@gmail.com'
	password = 'withme!1234'
#	_from = 'withme.team.akk@gmail.com'
	_from = 'WITHME'
	_to  = email

	subject = "Subject: [WITHME] 회원님! WITHME의 회원가입을 환영합니다!"
	main_msg = '''
WITHME의 회원이 되어 주셔서 감사합니다!
회원님께서는 최초의 이메일 인증 이후 로그인하여 WITHME를 사용하실 수 있습니다.
아래 링크를 통해 인증을 완료하고 로그인 하여 WITHME를 사용해주세요!
'''

	msg = "\r\n".join([
	  "From: " + _from,
	  "To: " + email,
	  subject,
	  "",main_msg,
	  template
	  ])
	msg = msg.encode('utf-8')
	server = smtplib.SMTP( MAIL_SERVER )
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail(_from, _to, msg)
	server.quit()
	return


def send_confirmation_mail(email, username):
	token = generate_confirmation_token(email, username)
	confirm_url = url_for('confirm_email', token=token, _external=True)
	html = render_template('activate.html', confirm_url=confirm_url)
	send_mail(email, html)
	return

