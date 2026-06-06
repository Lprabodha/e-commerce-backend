from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import generate_chat_reply

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, db=Depends(get_db)):
    try:
        reply = generate_chat_reply(
            db=db,
            customer_message=body.customer_message,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Chat model error: {exc}") from exc

    return ChatResponse(reply=reply)