"""
Chat API Router.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ohgrt_api.auth.dependencies import User, get_current_user, get_optional_user, get_db
from ohgrt_api.chat.service import get_chat_service
from ohgrt_api.config import get_settings
from ohgrt_api.db.models import User as DBUser, IntegrationCredential
from ohgrt_api.services.gmail_service import GmailService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    history: Optional[List[ChatMessage]] = Field(
        None, description="Conversation history"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class AssistantMessage(BaseModel):
    """Assistant message model for web frontend."""

    id: str = Field(..., description="Message ID")
    content: str = Field(..., description="Assistant response content")
    role: str = Field(default="assistant", description="Message role")
    created_at: Optional[str] = Field(None, description="Message creation timestamp")
    intent: Optional[str] = Field(None, description="Detected intent")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")
    media_url: Optional[str] = Field(None, description="Media URL if applicable")


class ChatResponse(BaseModel):
    """Chat response model.

    Note: iOS uses .convertFromSnakeCase decoder, so all field names
    should be snake_case. The iOS app will automatically convert them
    to camelCase when decoding.
    """

    # iOS app expects these fields (snake_case for API, iOS decodes to camelCase)
    id: str = Field(..., description="Message ID")
    content: str = Field(..., description="Assistant response content")
    role: str = Field(default="assistant", description="Message role")
    created_at: Optional[str] = Field(None, description="Message creation timestamp")

    # Common fields
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    intent: Optional[str] = Field(None, description="Detected intent")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data (email list, weather, etc)")
    requires_location: Optional[bool] = Field(None, description="Whether location is needed")
    media_url: Optional[str] = Field(None, description="Media URL if applicable")

    # Web frontend expects assistant_message wrapper
    assistant_message: Optional[AssistantMessage] = Field(None, description="Assistant message for web frontend")

    # Legacy/web fields (keeping for backwards compatibility)
    response: Optional[str] = Field(None, description="Legacy: Assistant response")
    needs_location: Optional[bool] = Field(None, description="Legacy: Whether location is needed")
    metadata: Optional[Dict[str, Any]] = Field(None)


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: User = Depends(get_current_user),
):
    """
    Send a message to the AI assistant.

    Args:
        request: ChatRequest with message and optional context
        user: Authenticated user

    Returns:
        ChatResponse with AI response
    """
    try:
        service = get_chat_service()

        # Convert history to list of dicts
        history = None
        if request.history:
            history = [{"role": m.role, "content": m.content} for m in request.history]

        result = await service.process_message(
            message=request.message,
            user_id=user.user_id,
            conversation_history=history,
            context=request.context,
        )

        response_text = result.get("response", "")
        message_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        intent = result.get("intent")
        structured_data = result.get("structured_data")

        logger.info(f"Chat result for {user.user_id}: response={response_text[:100] if response_text else 'empty'}, intent={intent}, has_structured_data={bool(structured_data)}")

        # Create assistant message for web frontend
        assistant_msg = AssistantMessage(
            id=message_id,
            content=response_text,
            role="assistant",
            created_at=created_at,
            intent=intent,
            structured_data=structured_data,
        )

        return ChatResponse(
            # iOS required fields
            id=message_id,
            content=response_text,
            role="assistant",
            created_at=created_at,
            # Common fields
            conversation_id=request.conversation_id,
            intent=intent,
            structured_data=structured_data,
            requires_location=result.get("needs_location"),
            # Web frontend expects assistant_message wrapper
            assistant_message=assistant_msg,
            # Legacy fields for backwards compatibility
            response=response_text,
            needs_location=result.get("needs_location"),
            metadata=result.get("metadata"),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")


@router.post("/completion")
async def get_completion(
    request: ChatRequest,
    user: User = Depends(get_current_user),
):
    """
    Get a direct LLM completion.

    Args:
        request: ChatRequest with message
        user: Authenticated user

    Returns:
        Completion response
    """
    try:
        service = get_chat_service()

        # Build messages
        messages = []
        if request.history:
            messages.extend(
                [{"role": m.role, "content": m.content} for m in request.history]
            )
        messages.append({"role": "user", "content": request.message})

        response = await service.get_completion(messages)

        return {"response": response}

    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(status_code=500, detail="Completion failed")


@router.get("/health")
async def chat_health():
    """Chat service health check."""
    return {"status": "healthy", "service": "chat"}


# Conversation models
class ConversationSummary(BaseModel):
    """Conversation summary for listing."""

    id: str
    title: str
    updated_at: str
    message_count: int = 0


@router.get("/conversations", response_model=List[ConversationSummary])
async def get_conversations(
    user: User = Depends(get_current_user),
):
    """
    Get all conversations for the current user.

    Returns:
        List of conversation summaries
    """
    # TODO: Integrate with ConversationService when database persistence is needed
    # For now, return empty list (conversations stored client-side)
    return []


# Scheduled email models
class ScheduledEmailSummary(BaseModel):
    """Scheduled email summary."""

    id: str
    to: str
    subject: str
    status: str  # active, sent, cancelled, failed
    scheduled_at: str
    created_at: str


@router.get("/email/scheduled", response_model=List[ScheduledEmailSummary])
async def get_scheduled_emails(
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    """
    Get scheduled emails for the current user.

    Args:
        status: Optional filter by status (active, sent, cancelled)

    Returns:
        List of scheduled emails
    """
    # TODO: Integrate with ScheduledTaskService for email scheduling
    # For now, return empty list
    return []


# MCP tools model
class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str
    description: str
    enabled: bool = True


@router.get("/mcp-tools", response_model=List[MCPTool])
async def get_mcp_tools(
    user: User = Depends(get_current_user),
):
    """
    Get available MCP tools for the current user.

    Returns:
        List of available MCP tools
    """
    # Return the default set of tools available
    return [
        MCPTool(name="gmail", description="Read and send emails via Gmail", enabled=True),
        MCPTool(name="weather", description="Get weather information", enabled=True),
        MCPTool(name="news", description="Get latest news", enabled=True),
        MCPTool(name="web_search", description="Search the web", enabled=True),
    ]


# Email detail model
class EmailDetail(BaseModel):
    """Full email detail model."""

    id: str
    thread_id: Optional[str] = None
    subject: str
    from_address: str = Field(..., alias="from")
    to: str
    cc: Optional[str] = None
    date: str
    body: str
    body_html: Optional[str] = None
    body_plain: Optional[str] = None
    snippet: Optional[str] = None
    label_ids: Optional[List[str]] = None

    class Config:
        populate_by_name = True


@router.get("/email/{email_id}", response_model=EmailDetail)
async def get_email_detail(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get full email details by ID.

    Args:
        email_id: The Gmail message ID
        user: Authenticated user
        db: Database session

    Returns:
        Full email details including body
    """
    settings = get_settings()

    # Find user by Firebase UID
    db_user = db.query(DBUser).filter(DBUser.firebase_uid == user.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get Gmail credential
    credential = (
        db.query(IntegrationCredential)
        .filter(
            IntegrationCredential.user_id == db_user.id,
            IntegrationCredential.provider == "gmail",
        )
        .first()
    )

    if not credential:
        raise HTTPException(status_code=400, detail="Gmail not connected")

    # Build credential dict for GmailService
    cred_dict = {
        "access_token": credential.access_token,
        "config": credential.config or {},
    }

    # Initialize Gmail service
    gmail_service = GmailService(settings, credential=cred_dict)

    if not gmail_service.available:
        raise HTTPException(status_code=400, detail="Gmail service not available")

    try:
        email = await gmail_service.get_email_by_id(email_id)

        return EmailDetail(
            id=email.get("id", ""),
            thread_id=email.get("threadId"),
            subject=email.get("subject", ""),
            **{"from": email.get("from", "")},
            to=email.get("to", ""),
            cc=email.get("cc"),
            date=email.get("date", ""),
            body=email.get("body", ""),
            body_html=email.get("body_html"),
            body_plain=email.get("body_plain"),
            snippet=email.get("snippet"),
            label_ids=email.get("labelIds"),
        )
    except Exception as e:
        logger.error(f"Error fetching email {email_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch email: {str(e)}")
