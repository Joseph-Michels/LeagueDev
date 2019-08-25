import app.riot_requester_util as req_util
from pprint import pprint
from time import sleep
from datetime import datetime

T = 30

statuses = req_util.safe_request("NA", "status")
sleep(T)

while True:
	next_statuses = req_util.safe_request("NA", "status")

	if statuses != next_statuses:
		# if status is different, check and display exactly what changed

		# new statuses?
		for status in next_statuses:
			if status not in statuses:
				print(f"\a[{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}] NEW STATUS")
				print(status)

		# ended statuses?
		for status in statuses:
			if status not in next_statuses:
				print(f"\a[{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}] END STATUS")
				print(status)

		statuses = next_statuses
	
	sleep(T)