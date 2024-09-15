import os
from typing import List, Dict
from supabase import create_client, Client
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from sqlalchemy.orm import Session
import requests
import db_crud as dbc

from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def get_user_documents(db: Session, user_id: str) -> SupabaseVectorStore:
    user = dbc.get_or_create_user(db, user_id)
    os.environ["OPENAI_API_KEY"] = user.openai_key
    embeddings = OpenAIEmbeddings()
    vector_store = SupabaseVectorStore(
        supabase, 
        embeddings, 
        table_name="documents",
        query_name="match_documents"
    )
    
    # Create a filter to only retrieve documents for the specific user
    filter_dict = {"user_id": user_id}
    
    # Return a filtered version of the vector store
    return vector_store.as_retriever(search_kwargs={"filter": filter_dict})


def fetch_stock_information(stock_symbol: str) -> Dict:
    url = f"https://realstonks.p.rapidapi.com/stocks/{stock_symbol}"

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "realstonks.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def fetch_news_articles(stock_name: str) -> List[Dict]:
    subscription_key = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
    search_url = "https://api.bing.microsoft.com/v7.0/news/search"
    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params = {
        "q": f"{stock_name} news",
    }
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results["value"]

def analyze_sentiment(db: Session, user_id: str, vector_store: SupabaseVectorStore, news_articles: List[Dict], stock_symbol: str) -> str:
    user = dbc.get_or_create_user(db, user_id)
    os.environ["OPENAI_API_KEY"] = user.openai_key
    llm = ChatOpenAI(temperature=0)
    
    # Combine 10-K information and news articles
    context = "\n".join([article["description"] for article in news_articles])
    
    prompt_template = """
    You are a financial analyst tasked with predicting the stock price movement for {stock_symbol}.
    
    Based on the company's financial documents and recent news, analyze the following:
    1. The company's financial health from their 10-K and 10-Q filings.
    2. Recent news and market sentiment.
    
    Recent news and context:
    {context}
    
    Using this information, predict whether the stock price of {stock_symbol} is likely to rise or fall in the short term.
    Provide a concise explanation for your prediction.
    
    Your response should be in the following format:
    Prediction: [Floating point value between 0 and 1, with 1 strongly suggesting a price increase and 0 strongly suggesting a price decrease]
    Explanation: [Your explanation here]
    
    Human: Based on the above information, what is your prediction for {stock_symbol} stock?
    
    AI: Let me analyze the information and provide a prediction.
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["stock_symbol", "context"]
    )
    
    chain_type_kwargs = {"prompt": PROMPT}
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        chain_type_kwargs=chain_type_kwargs
    )
    
    result = qa.run({"stock_symbol": stock_symbol, "context": context})
    return result

def predict_stock_movement(db: Session, user_id: str, stock_symbol: str) -> Dict:
    vector_store = get_user_documents(db, user_id)
    stock_info = fetch_stock_information(stock_symbol)
    news_articles = fetch_news_articles(stock_info.get("symbolName"))
    print(f"\n\n\n\n\nNews articles: {news_articles}\n\n\n\n\n")
    prediction = analyze_sentiment(db, user_id, vector_store, news_articles, stock_symbol)
    return {
        "stock_symbol": stock_symbol,
        "stock_name": stock_info.get("symbolName"),
        "stock_price": stock_info.get("lastPrice"),
        "prediction": prediction
    }

# This function can be called from main.py
def get_stock_predictions(db: Session, user_id: str, stock_symbols: List[str]) -> List[Dict]:
    predictions = []
    for symbol in stock_symbols:
        prediction = predict_stock_movement(db, user_id, symbol)
        predictions.append(prediction)
    print(f"\n\n\n\n\nPredictions: {predictions}\n\n\n\n\n")
    return predictions
