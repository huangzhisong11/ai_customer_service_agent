from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.schemas import ChatRequest, ChatResponse
from app.database import init_db, save_message, get_history
from app.rag import KnowledgeBase
from app.agents import CustomerServiceOrchestrator

app = FastAPI(title="AI Customer Service Agent")

kb = KnowledgeBase()
orchestrator = CustomerServiceOrchestrator(kb)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = get_history(req.session_id, limit=10)
    save_message(req.session_id, "user", req.message)

    result = orchestrator.run(req.message, history)
    save_message(req.session_id, "assistant", result["answer"])

    return ChatResponse(**result)

@app.post("/api/reload-kb")
def reload_kb():
    kb.load()
    return {"message": "knowledge base reloaded", "chunks": len(kb.docs)}

app.mount("/static", StaticFiles(directory="static"), name="static")
