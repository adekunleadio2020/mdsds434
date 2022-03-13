from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from google.cloud import bigquery
import json
import uvicorn


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()
ALLOWED_ORIGINS = '*'    # or 'foo.com', etc.

origins = [
    "https://8080-cs-685192381812-default.cs-us-central1-pits.cloudshell.dev",
    "https://accounts.google.com",
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"],
)

client = bigquery.Client(project="msds434-339120")


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# handle CORS preflight requests
@app.options('/{rest_of_path:path}')
async def preflight_handler(request: Request, rest_of_path: str) -> Response:
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    response.headers['Sec-Fetch-Mode'] = 'no-cors'
    print("preflight_handler")
    return response

# set CORS headers
@app.middleware("http")
async def add_CORS_header(request: Request, call_next):
    response = await call_next(request)
    response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    response.headers['Sec-Fetch-Mode'] = 'no-cors'
    print("add_CORS_header")
    return response

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/")
async def root(token: str = Depends(oauth2_scheme),\
     date: str ='2022-02-03', open: int=385, high:int=393, low:int=376, close:int=376, adjclose:str='381.85', volume:int=1024394,name:str='MDB'):
    """Add two numbers together"""

    date=date

    query = """
        SELECT
        *
        FROM
        ML.PREDICT(MODEL `msds434-339120.lake.stocks_model`,
            (
            SELECT 
            PARSE_DATE('%Y-%m-%d',  '{date}') AS Date,
            {open} AS Open,
            {high} AS High,
            {low} AS Low,
            {close} AS Close,
            '{adjclose}' AS AdjClose,
            {volume} AS Volume,
            '{name}' AS Name
            ))"""

    query =query.format(date=date, open=open,high=high, low=low, close=close, adjclose=adjclose,volume=volume,name=name)
    query_job = client.query(query)

    results = query_job.result()  # Waits for job to complete.
    df = results.to_dataframe()
    json_obj = df.to_json(orient='records')

    return json_obj

    #return query


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")

# var = 1
# var = var


