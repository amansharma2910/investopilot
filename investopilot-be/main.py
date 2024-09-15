import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import db_crud as dbc
import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

from supertokens_python import get_all_cors_headers, init, SupertokensConfig, InputAppInfo
from supertokens_python.recipe import session, emailpassword, dashboard
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe.session.framework.fastapi import verify_session

from supabase import create_client, Client

from dotenv import load_dotenv


load_dotenv()


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

init(
    supertokens_config=SupertokensConfig(
        connection_uri=os.getenv("SUPERTOKENS_CONNECTION_URL"),
        api_key=os.getenv("SUPERTOKENS_API_KEY")
    ),
    app_info=InputAppInfo(
        app_name="InvestoPilot",
        api_domain="http://localhost:8000",
        website_domain="http://localhost:3000"
    ),
    framework="fastapi",
    recipe_list=[
        session.init(), 
        emailpassword.init(),
        dashboard.init(),
    ],
)

app.add_middleware(get_middleware())
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)

@app.get("/")
async def root():
    return {"message": "Hello Visitor. Head over to /docs to see the API documentation."}


@app.get("/stocks")
async def stocks(session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    stocks = dbc.get_stocks(user_id)
    return {"stocks": stocks}


@app.post("/stocks")
async def add_stock(request: Request, session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    data = await request.json()
    if len(data) > 0 and len(data) < 5:
        stocks = dbc.update_stocks(user_id, data)
        return {"stock": stocks}
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid data"})

 
@app.get("/insights")
async def insights(session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    stocks = dbc.get_stocks(user_id)
    insights = ai.get_insights(stocks)
    return {"insights": insights}


@app.post("/openai-key")
async def openai_key(request: Request, session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    data = await request.json()
    if "key" in data:
        dbc.update_openai_key(user_id, data["key"])
        return {"message": "Key updated"}
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid data"})


@app.get("/openai-key")
async def check_openai_key(session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    has_key = dbc.check_openai_key(user_id)
    has_key = True
    return {"key": has_key}
    