import os

class Config:
	try:
		with open("credentials/form_key.txt", 'r') as f:
			SECRET_KEY = os.environ.get('SECRET_KEY') or f.readline().rstrip()
	except FileNotFoundError:
		raise FileNotFoundError('Missing form key.')
	