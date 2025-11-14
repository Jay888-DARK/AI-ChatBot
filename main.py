import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# ----------------------------
# 1️⃣ Load API key
# ----------------------------
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
if not key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

# ----------------------------
# 2️⃣ Define output model
# ----------------------------
class ResearchResponse(BaseModel):
    topic: str = Field(..., description="Topic being researched")
    summary: str = Field(..., description="A short summary of the topic")
    sources: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# ----------------------------
# 3️⃣ Initialize LLM
# ----------------------------
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    google_api_key=key,
    temperature=0.4,
)

# ----------------------------
# 4️⃣ Define Wikipedia tool
# ----------------------------
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# ----------------------------
# 5️⃣ Define prompt template
# ----------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research assistant. Use Wikipedia to gather info."),
    ("human", "Research the topic: {query}. Return JSON in this format:\n{format_instructions}")
]).partial(format_instructions=parser.get_format_instructions())

# ----------------------------
# 6️⃣ Define research function
# ----------------------------
def run_research(query: str):
    try:
        wiki_result = wiki.run(query)
        messages = prompt.format_messages(query=query)
        response = llm.invoke(messages + [{"role": "user", "content": wiki_result}])
        text = response.content

        json_text = text.strip().removeprefix("```json").removesuffix("```").strip()
        try:
            structured = json.loads(json_text)
        except json.JSONDecodeError:
            structured = {
                "topic": query,
                "summary": text,
                "sources": ["Wikipedia"],
                "tools_used": ["WikipediaQueryRun"]
            }

        parsed = parser.parse(json.dumps(structured))
        return parsed.model_dump()
    except Exception as e:
        return {"error": str(e), "message": "Something went wrong while processing your request."}

# ----------------------------
# 7️⃣ FastAPI App Setup
# ----------------------------
app = FastAPI(title="AI Research ChatBot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Research endpoint
@app.get("/research")
def research(query: str):
    return run_research(query)
