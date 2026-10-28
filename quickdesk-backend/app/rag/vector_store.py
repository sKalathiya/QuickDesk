from langchain_postgres import PGVector
from app.core.database import url
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings



embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",api_key=settings.GOOGLE_API_KEY.get_secret_value())

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="documents",
    connection=url,
    async_mode=True
)

