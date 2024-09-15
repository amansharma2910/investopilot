import os
from fastapi import FastAPI, Depends


from fastapi.responses import JSONResponse
from supertokens_python import get_all_cors_headers, init, SupertokensConfig, InputAppInfo
from supertokens_python.recipe import session, emailpassword, dashboard
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer


from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request


load_dotenv()


app = FastAPI()

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