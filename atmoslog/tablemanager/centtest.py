def logsToCents(logs):
	cents = 0
	if logs > 100000000:
		diff = logs - 100000000
		cents = cents + ((logs-100000000) * 1.5 / 10000)
		logs = logs - diff
		print(logs)
		print(cents)
	if logs > 10000000:
		diff = logs - 10000000
		cents = cents + ((logs-10000000) * 3 / 10000)
		logs = logs - diff
		print(logs)
		print(cents)
	cents = cents + (logs * 6 / 10000)
	return cents