coverage:
	coverage run --source dj_timetravel_postgres runtests.py
	coverage report -m
	coverage html
	chromium-browser htmlcov/index.html