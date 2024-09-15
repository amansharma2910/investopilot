import os
import io
import requests
from PyPDF2 import PdfReader

from fastapi import FastAPI, Depends, Form, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import ai
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
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import uuid

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


@app.get("/all-stocks")
async def all_stocks(session: session.SessionContainer = Depends(verify_session())):
    api_url = "https://financialmodelingprep.com/api/v3/symbol/NASDAQ"
    api_key = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")

    response = requests.get(f"{api_url}?apikey={api_key}")
    
    if response.status_code == 200:
        all_stocks = response.json()
        simplified_stocks = [
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "price": stock["price"]
            }
            for stock in all_stocks
        ]
        
        return {"stocks": simplified_stocks}
    else:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to fetch stocks data"})


@app.post("/stocks")
async def add_stock(request: Request, session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    data = await request.json()
    if len(data) > 0 and len(data) < 5:
        stocks = dbc.update_stocks(user_id, data)
        return {"stock": stocks}
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid data"})


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


@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    filing_type: str = Form(...),  # Either "10-K" or "10-Q"
    session: session.SessionContainer = Depends(verify_session())
):
    user_id = session.get_user_id()
    
    # Check if the file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(status_code=400, content={"message": "Only PDF files are accepted"})
    
    # Read the PDF content
    content = await file.read()
    pdf_reader = PdfReader(io.BytesIO(content))
    
    # Extract text from all pages
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    # Split the text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(text)
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    
    # Store in Supabase
    for chunk in texts:
        embedding = embeddings.embed_query(chunk)
        supabase.table("documents").insert({
            "id": str(uuid.uuid4()),
            "content": chunk,
            "embedding": embedding,
            "metadata": {
                "filename": file.filename,
                "filing_type": filing_type,
                "user_id": user_id
            },
            "user_id": user_id
        }).execute()
    
    return {"filename": file.filename, "message": "File uploaded, parsed, vectorized, and stored successfully"}


@app.get("/stock-predictions")
async def stock_predictions(session: session.SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    stocks = dbc.get_stocks(user_id)
    predictions = ai.get_stock_predictions(user_id, stocks)
    return {"predictions": predictions}
