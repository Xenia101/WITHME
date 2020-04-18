class BaseConfig():
	"""Base configuration."""
	# main config
	SECRET_KEY = 'withme!1234'
	SECURITY_PASSWORD_SALT = 'withme!1234'
	DB_PATH = 'sqlite:///my_test.db'
	MAIL_SERVER = 'smtp.gmail.com:587'

