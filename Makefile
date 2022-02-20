install:
	pip install --upgrade pip && pip install -r requirements.txt

test:
	python -m pytest -vv test_hello.py
	python -m pytest -vv test_main.py

format:
	black *.py

run:
	python main.py

run-stock-advisor:
	python stockAdvisor.py

run-stock-advisor-on-cloud-run:
	gcloud run deploy msds434 --source . --project msds434-339120

run-uvicorn:
	uvicorn main:app --reload

lint:
	pylint --disable=R,C *.py

killweb:
	sudo killall uvicorn

set-job-env:
	export PROJECT=msds434-339120
	gcloud config set project $$PROJECT

	#Create Cloud Storage Bucket
	gsutil mb -c regional -l us-central1 gs://$$PROJECT
	
	#Create the BigQuery Dataset
	bq mk lake

run-job:
	
	export PROJECT=msds434-339120
	
	gcloud config set project $$PROJECT

	python stock.py $$PROJECT MDB

	#Run the Apache Beam Pipeline
	python data_ingestion.py --project=$$PROJECT --region=us-central1 --runner=DataflowRunner \
	--staging_location=gs://$$PROJECT/staging --temp_location gs://$$PROJECT/temp  \
	--input gs://$$PROJECT/data_files/stocks.csv --save_main_session

	#--template_location gs://$$PROJECT/templates/stocks \
	
all: install lint test