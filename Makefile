coverage:
	coverage combine
	coverage erase
	python commands.py remove_container djtt
	python commands.py run_container djtt
	python commands.py remove_migrations tests/project1
	coverage run -p --branch --source dj_timetravel_postgres commands.py run_tests tests/project1

	python commands.py remove_container djtt
	python commands.py run_container djtt
	python commands.py remove_migrations tests/project2
	coverage run -p --branch --source dj_timetravel_postgres commands.py run_tests tests/project2

	python commands.py remove_container djtt
	coverage combine
	coverage report -m
	coverage html
	chromium-browser htmlcov/index.html
