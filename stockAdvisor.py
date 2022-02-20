from fastapi import FastAPI
import uvicorn
from google.cloud import bigquery
import json

app = FastAPI()
client = bigquery.Client(project="msds434-339120")


@app.get("/")
async def root():
    """Add two numbers together"""

    query_job = client.query(
        """
        SELECT
        *
        FROM
        ML.PREDICT(MODEL `msds434-339120.lake.stocks_model`,
            (
            SELECT 
            PARSE_DATE('%Y-%m-%d',  '2022-02-03') AS Date,
            385 AS Open,
            393 AS High,
            376.02 AS Low,
            376.02 AS Close,
            '381.85' AS AdjClose,
            1024394 AS Volume,
            'MDB' AS Name
            ))"""
    )

    results = query_job.result()  # Waits for job to complete.
    df = results.to_dataframe()
    json_obj = df.to_json(orient='records')

    return json_obj


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")

# var = 1
# var = var
