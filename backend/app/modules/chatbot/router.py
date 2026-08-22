from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user
from app.core.database import get_db
from app.modules.chatbot import service, schemas
from app.modules.chatbot.models import ChatSession, ChatMessage
from app.modules.chatbot.ollama_client import check_ollama_health

router = APIRouter(tags=["Chatbot"])

@router.post("/chatbot/session", response_model=schemas.ChatSessionOut)
async def create_session(db=Depends(get_db), current_user=Depends(get_current_user)):
    # Fallback if employee_id isn't defined yet
    emp_id = getattr(current_user, "employee_id", current_user.id)
    session = ChatSession(employee_id=emp_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.post("/chatbot/message")
async def send_message(request: schemas.ChatRequest, db=Depends(get_db), current_user=Depends(get_current_user)):
    if not await check_ollama_health():
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable. Please try again later.")
    
    emp_id = getattr(current_user, "employee_id", current_user.id)
    # Verify session belongs to current user
    session = db.query(ChatSession).filter_by(id=request.session_id, employee_id=emp_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def generator():
        async for chunk in service.handle_message(db, request.session_id, emp_id, request.message):
            yield chunk

    return StreamingResponse(generator(), media_type="text/plain")

@router.get("/chatbot/session/{session_id}/history", response_model=list[schemas.ChatMessageOut])
def session_history(session_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    emp_id = getattr(current_user, "employee_id", current_user.id)
    session = db.query(ChatSession).filter_by(id=session_id, employee_id=emp_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
