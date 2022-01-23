install:
	pip install --upgrade pip && pip install -r requirements.txt

test:
	python -m pytest -vv test_hello.py
	python -m pytest -vv test_main.py

format:
	black *.py

run:
	python main.py

run-uvicorn:
	uvicorn main:app --reload

lint:
	pylint --disable=R,C *.py

killweb:
	sudo killall uvicorn

all: install lint test