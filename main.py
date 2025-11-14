from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

app = FastAPI()

# Model for input
class ChatInput(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "FastAPI server is running!"}

@app.post("/chat")
async def chat_with_ai(data: ChatInput):
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key="YOUR_API_KEY"
    )

    response = model.invoke([HumanMessage(content=data.message)])
    return {"reply": response.content}
