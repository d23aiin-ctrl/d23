from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import time

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select, func, and_, extract
from pydantic import BaseModel

from ohgrt_api.config import get_settings
from ohgrt_api.db.base import SessionLocal, is_db_available
from ohgrt_api.db.models import ConversationContext, WhatsAppChatMessage
from ohgrt_api.admin.auth import (
    LoginRequest,
    LoginResponse,
    AdminUser,
    verify_password,
    create_access_token,
    require_admin,
    log_admin_action,
)

router = APIRouter(prefix="/admin", tags=["admin"])

# Track application start time for uptime
_app_start_time = time.time()
_last_error: str | None = None


class BroadcastRequest(BaseModel):
    message: str


# =====================
# Authentication Endpoints
# =====================

@router.post("/login", response_class=JSONResponse)
async def admin_login(request: LoginRequest) -> LoginResponse:
    """Admin login endpoint. Returns JWT token."""
    if not verify_password(request.username, request.password):
        # Log failed attempt
        print(f"[SECURITY] Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # Create token
    token, expires_at = create_access_token(request.username)

    # Log successful login
    print(f"[SECURITY] Successful login: {request.username}")

    return LoginResponse(
        token=token,
        expires_at=expires_at.isoformat(),
        user={
            "username": request.username,
            "role": "admin",
        },
    )


@router.get("/verify", response_class=JSONResponse)
async def verify_session(user: AdminUser = Depends(require_admin)) -> dict:
    """Verify that the current session/token is valid."""
    return {
        "valid": True,
        "user": {
            "username": user.username,
            "role": user.role,
        },
    }


@router.post("/logout", response_class=JSONResponse)
async def admin_logout(user: AdminUser = Depends(require_admin)) -> dict:
    """Logout endpoint (client should delete token)."""
    log_admin_action(user, "logout")
    return {"message": "Logged out successfully"}


# =====================
# Protected Admin Endpoints
# =====================

def _get_whatsapp_counts() -> dict:
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        total_stmt = select(func.count(func.distinct(ConversationContext.client_id))).where(
            ConversationContext.client_type == "whatsapp"
        )
        total = db.execute(total_stmt).scalar() or 0

        since = datetime.now(timezone.utc) - timedelta(hours=24)
        active_stmt = select(func.count(func.distinct(ConversationContext.client_id))).where(
            ConversationContext.client_type == "whatsapp",
            ConversationContext.updated_at >= since,
        )
        active_24h = db.execute(active_stmt).scalar() or 0

        return {"total": total, "active_24h": active_24h}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.get("/whatsapp-users", response_class=JSONResponse)
async def whatsapp_users_stats(user: AdminUser = Depends(require_admin)) -> dict:
    """Return WhatsApp user counts for admin dashboard."""
    log_admin_action(user, "view_user_stats")
    counts = _get_whatsapp_counts()
    return {
        "whatsapp_users_total": counts["total"],
        "whatsapp_users_active_24h": counts["active_24h"],
    }


@router.get("/whatsapp-chats", response_class=JSONResponse)
async def whatsapp_chat_messages(
    phone: str = Query(..., min_length=6),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: AdminUser = Depends(require_admin),
) -> dict:
    """Return recent WhatsApp chat messages for a phone number."""
    log_admin_action(user, "view_chat", {"phone": phone})
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        stmt = (
            select(WhatsAppChatMessage)
            .where(WhatsAppChatMessage.phone_number == phone)
            .order_by(WhatsAppChatMessage.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = db.execute(stmt).scalars().all()
        messages = [
            {
                "direction": r.direction,
                "text": r.text,
                "message_id": r.message_id,
                "response_type": r.response_type,
                "media_url": r.media_url,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reversed(rows)
        ]
        return {"phone": phone, "count": len(messages), "messages": messages}
    finally:
        db.close()


@router.get("/whatsapp-users-list", response_class=JSONResponse)
async def whatsapp_users_list(
    start_date: str = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date filter (YYYY-MM-DD)"),
    min_messages: int = Query(0, ge=0, description="Minimum message count"),
    direction: str = Query("all", description="Filter by direction: all, incoming, outgoing"),
    user: AdminUser = Depends(require_admin),
) -> dict:
    """Return WhatsApp users list with last activity and date filtering."""
    log_admin_action(user, "view_users_list", {"filters": {
        "start_date": start_date,
        "end_date": end_date,
        "min_messages": min_messages,
    }})
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        # Build base query
        query = select(
            WhatsAppChatMessage.phone_number,
            func.max(WhatsAppChatMessage.created_at).label("last_seen"),
            func.min(WhatsAppChatMessage.created_at).label("first_seen"),
            func.count(WhatsAppChatMessage.id).label("message_count"),
        )

        # Apply filters
        filters = []

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
                filters.append(WhatsAppChatMessage.created_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                filters.append(WhatsAppChatMessage.created_at <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        if direction != "all":
            filters.append(WhatsAppChatMessage.direction == direction)

        if filters:
            query = query.where(and_(*filters))

        # Group and order
        stmt = query.group_by(WhatsAppChatMessage.phone_number)

        # Apply message count filter after grouping
        if min_messages > 0:
            stmt = stmt.having(func.count(WhatsAppChatMessage.id) >= min_messages)

        stmt = stmt.order_by(func.max(WhatsAppChatMessage.created_at).desc())

        rows = db.execute(stmt).all()
        users = [
            {
                "phone": r.phone_number,
                "last_seen": r.last_seen.isoformat() if r.last_seen else None,
                "first_seen": r.first_seen.isoformat() if r.first_seen else None,
                "message_count": r.message_count,
            }
            for r in rows
        ]
        return {"count": len(users), "users": users, "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "min_messages": min_messages,
            "direction": direction,
        }}
    finally:
        db.close()


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard() -> HTMLResponse:
    """Simple admin dashboard for WhatsApp metrics."""
    settings = get_settings()
    error_detail = None
    counts = {"total": 0, "active_24h": 0}
    try:
        counts = _get_whatsapp_counts()
    except HTTPException as exc:
        error_detail = exc.detail
    error_block = (
        f"<div class=\"card\"><div class=\"label\">Status</div>"
        f"<div class=\"value\" style=\"color:#b91c1c;\">DB Unavailable</div>"
        f"<div class=\"meta\">{error_detail}</div></div>"
    ) if error_detail else ""
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>WhatsApp Admin Dashboard</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    :root {{
      --bg1: #f7f2e9;
      --bg2: #f2e8d8;
      --ink: #1f2937;
      --muted: #6b7280;
      --accent: #0f766e;
      --card: #ffffff;
      --shadow: 0 20px 60px rgba(15, 118, 110, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      height: 100%;
      overflow: hidden;
    }}
    body {{
      margin: 0;
      font-family: "Space Grotesk", sans-serif;
      color: var(--ink);
      background: radial-gradient(1200px 800px at 10% -20%, var(--bg2), transparent),
                  radial-gradient(900px 600px at 90% 0%, #efe7d7, transparent),
                  linear-gradient(135deg, var(--bg1), #faf7f0 60%);
      min-height: 100vh;
    }}
    .wrap {{
      max-width: 980px;
      margin: 0 auto;
      padding: 24px;
      height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .chat-card {{
      display: flex;
      flex-direction: column;
      height: calc(100vh - 260px);
    }}
    .title {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 28px;
      font-weight: 700;
      letter-spacing: 0.2px;
    }}
    .subtitle {{
      color: var(--muted);
      margin-top: 6px;
      font-size: 14px;
    }}
    .grid {{
      margin-top: 12px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 18px;
      min-height: 0;
    }}
    .chat-grid {{
      flex: 1;
      min-height: 0;
      align-items: stretch;
      height: calc(100vh - 230px);
    }}
    .card {{
      background: var(--card);
      border-radius: 16px;
      padding: 22px;
      box-shadow: var(--shadow);
      border: 1px solid #eef2f3;
    }}
    .chat-grid .card {{
      height: 100%;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }}
    .label {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .value {{
      font-size: 36px;
      font-weight: 700;
      color: var(--accent);
    }}
    .meta {{
      margin-top: 18px;
      font-size: 12px;
      color: var(--muted);
    }}
    .pill {{
      display: inline-block;
      margin-top: 10px;
      padding: 6px 10px;
      background: #e6fffb;
      color: #115e59;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
    }}
    .chat-window {{
      flex: 1;
      overflow-y: auto;
      padding-right: 6px;
      min-height: 0;
    }}
    .panel-body {{
      flex: 1;
      overflow-y: auto;
      padding-right: 6px;
      min-height: 0;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="title">WhatsApp Admin Dashboard</div>
    <div class="subtitle">Connected users based on unique phone numbers.</div>
    <div class="grid">
      <div class="card">
        <div class="label">Total Connected Users</div>
        <div class="value">{counts['total']}</div>
        <div class="pill">All time</div>
      </div>
      <div class="card">
        <div class="label">Active in Last 24 Hours</div>
        <div class="value">{counts['active_24h']}</div>
        <div class="pill">Rolling window</div>
      </div>
      {error_block}
    </div>
    <div class="meta">Environment: {settings.environment}</div>
    <div class="meta">Chat API: /admin/whatsapp-chats?phone=+91XXXXXXXXXX</div>
    <div class="grid chat-grid" style="margin-top: 12px;">
      <div class="card">
        <div class="label">Users</div>
        <div id="users" class="meta panel-body">Loading...</div>
      </div>
      <div class="card chat-card">
        <div class="label">Chat</div>
        <div id="chat" class="meta chat-window panel-body">Select a user to view messages.</div>
      </div>
    </div>
  </div>
  <script>
    async function loadUsers() {{
      const res = await fetch('/admin/whatsapp-users-list');
      const data = await res.json();
      const root = document.getElementById('users');
      if (!data.users || data.users.length === 0) {{
        root.textContent = 'No users yet.';
        return;
      }}
      const rows = data.users.map(u => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f1f5f9;cursor:pointer;" onclick="loadChat('${{u.phone}}')">
          <div>
            <div style="font-weight:600;">${{u.phone}}</div>
            <div style="color:#6b7280;font-size:12px;">Messages: ${{u.message_count}}</div>
          </div>
          <div style="color:#6b7280;font-size:12px;">${{(u.last_seen || '').replace('T',' ').replace('Z','')}}</div>
        </div>
      `).join('');
      root.innerHTML = rows;
    }}

    const PAGE_SIZE = 15;
    let chatState = {{ phone: null, offset: 0 }};

    function renderMessages(messages) {{
      return messages.map(m => {{
        const align = m.direction === 'incoming' ? 'flex-start' : 'flex-end';
        const bg = m.direction === 'incoming' ? '#f1f5f9' : '#e6fffb';
        return `
          <div style="display:flex;justify-content:${{align}};margin:8px 0;">
            <div style="max-width:70%;background:${{bg}};padding:10px 12px;border-radius:12px;">
              <div style="font-size:13px;white-space:pre-wrap;">${{m.text || ''}}</div>
              <div style="font-size:10px;color:#6b7280;margin-top:6px;">${{m.created_at || ''}}</div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    async function fetchMoreMessages(reset = false) {{
      if (!chatState.phone) return;
      const res = await fetch(`/admin/whatsapp-chats?phone=${{encodeURIComponent(chatState.phone)}}&limit=${{PAGE_SIZE}}&offset=${{chatState.offset}}`);
      const data = await res.json();
      const root = document.getElementById('chat');
      const messages = data.messages || [];
      if (reset) {{
        root.innerHTML = `
          <div style="font-weight:600;margin-bottom:8px;">${{data.phone}}</div>
          <div id="chat-messages"></div>
          <div id="chat-load-more" style="margin-top:10px;display:flex;justify-content:center;">
            <button style="border:1px solid #e2e8f0;background:#fff;border-radius:8px;padding:6px 10px;cursor:pointer;" onclick="loadMore()">Load more</button>
          </div>
        `;
      }}
      const container = document.getElementById('chat-messages');
      if (!messages.length) {{
        const btn = document.getElementById('chat-load-more');
        if (btn) btn.style.display = 'none';
        return;
      }}
      container.insertAdjacentHTML('afterbegin', renderMessages(messages));
      chatState.offset += messages.length;
      if (messages.length < PAGE_SIZE) {{
        const btn = document.getElementById('chat-load-more');
        if (btn) btn.style.display = 'none';
      }}
    }}

    async function loadChat(phone) {{
      chatState = {{ phone, offset: 0 }};
      await fetchMoreMessages(true);
    }}

    async function loadMore() {{
      await fetchMoreMessages(false);
    }}

    loadUsers();
  </script>
</body>
</html>"""
    return HTMLResponse(content=html)


@router.get("/analytics", response_class=JSONResponse)
async def get_analytics(
    days: int = Query(7, ge=1, le=365),
    user: AdminUser = Depends(require_admin),
) -> dict:
    """Return analytics data for admin dashboard with date range filter."""
    log_admin_action(user, "view_analytics", {"days": days})
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        # Calculate time range
        time_range = datetime.now(timezone.utc) - timedelta(days=days)

        # Get intent distribution for the date range
        intent_stmt = (
            select(
                WhatsAppChatMessage.response_type,
                func.count(WhatsAppChatMessage.id).label("count")
            )
            .where(
                WhatsAppChatMessage.response_type.isnot(None),
                WhatsAppChatMessage.direction == "outgoing",
                WhatsAppChatMessage.created_at >= time_range
            )
            .group_by(WhatsAppChatMessage.response_type)
        )
        intent_results = db.execute(intent_stmt).all()
        intent_distribution = {
            row.response_type: row.count for row in intent_results if row.response_type
        }

        # Get total messages for the date range
        total_stmt = select(func.count(WhatsAppChatMessage.id)).where(
            WhatsAppChatMessage.created_at >= time_range
        )
        total_messages = db.execute(total_stmt).scalar() or 0

        # Get peak hours for the date range
        peak_hours_stmt = (
            select(
                extract("hour", WhatsAppChatMessage.created_at).label("hour"),
                func.count(WhatsAppChatMessage.id).label("count")
            )
            .where(WhatsAppChatMessage.created_at >= time_range)
            .group_by(extract("hour", WhatsAppChatMessage.created_at))
            .order_by(extract("hour", WhatsAppChatMessage.created_at))
        )
        peak_hours_results = db.execute(peak_hours_stmt).all()

        # Fill in all 24 hours
        peak_hours = []
        hour_map = {int(row.hour): row.count for row in peak_hours_results if row.hour is not None}
        for hour in range(24):
            peak_hours.append({"hour": hour, "count": hour_map.get(hour, 0)})

        # Get message volume by day for the date range
        volume_stmt = (
            select(
                func.date(WhatsAppChatMessage.created_at).label("date"),
                func.count(WhatsAppChatMessage.id).label("count")
            )
            .where(WhatsAppChatMessage.created_at >= time_range)
            .group_by(func.date(WhatsAppChatMessage.created_at))
            .order_by(func.date(WhatsAppChatMessage.created_at))
        )
        volume_results = db.execute(volume_stmt).all()
        message_volume = [
            {"date": str(row.date), "count": row.count}
            for row in volume_results
        ]

        # User engagement metrics (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)

        # New users (first seen in last 7 days)
        new_users_stmt = (
            select(func.count(func.distinct(WhatsAppChatMessage.phone_number)))
            .where(
                WhatsAppChatMessage.created_at >= seven_days_ago,
                WhatsAppChatMessage.phone_number.notin_(
                    select(func.distinct(WhatsAppChatMessage.phone_number))
                    .where(
                        WhatsAppChatMessage.created_at < seven_days_ago,
                        WhatsAppChatMessage.created_at >= fourteen_days_ago
                    )
                )
            )
        )
        new_users_7d = db.execute(new_users_stmt).scalar() or 0

        # Returning users (active in last 7 days and were also active 7-14 days ago)
        returning_users_stmt = (
            select(func.count(func.distinct(WhatsAppChatMessage.phone_number)))
            .where(
                WhatsAppChatMessage.created_at >= seven_days_ago,
                WhatsAppChatMessage.phone_number.in_(
                    select(func.distinct(WhatsAppChatMessage.phone_number))
                    .where(
                        WhatsAppChatMessage.created_at < seven_days_ago,
                        WhatsAppChatMessage.created_at >= fourteen_days_ago
                    )
                )
            )
        )
        returning_users_7d = db.execute(returning_users_stmt).scalar() or 0

        # Average messages per user
        total_users_stmt = select(func.count(func.distinct(WhatsAppChatMessage.phone_number))).where(
            WhatsAppChatMessage.created_at >= time_range
        )
        total_users = db.execute(total_users_stmt).scalar() or 1
        avg_messages_per_user = total_messages / total_users if total_users > 0 else 0

        return {
            "intent_distribution": intent_distribution,
            "message_volume": message_volume,
            "peak_hours": peak_hours,
            "total_messages": total_messages,
            "user_engagement": {
                "new_users_7d": new_users_7d,
                "returning_users_7d": returning_users_7d,
                "avg_messages_per_user": round(avg_messages_per_user, 2),
            },
        }
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.get("/top-users", response_class=JSONResponse)
async def get_top_users(
    limit: int = Query(10, ge=1, le=50),
    user: AdminUser = Depends(require_admin),
) -> dict:
    """Return top active users by message count."""
    log_admin_action(user, "view_top_users")
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        stmt = (
            select(
                WhatsAppChatMessage.phone_number,
                func.count(WhatsAppChatMessage.id).label("message_count"),
                func.max(WhatsAppChatMessage.created_at).label("last_active"),
                func.min(WhatsAppChatMessage.created_at).label("first_seen")
            )
            .group_by(WhatsAppChatMessage.phone_number)
            .order_by(func.count(WhatsAppChatMessage.id).desc())
            .limit(limit)
        )
        results = db.execute(stmt).all()

        top_users = [
            {
                "phone": row.phone_number,
                "message_count": row.message_count,
                "last_active": row.last_active.isoformat() if row.last_active else None,
                "first_seen": row.first_seen.isoformat() if row.first_seen else None,
            }
            for row in results
        ]

        return {"users": top_users, "count": len(top_users)}
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.get("/recent-activity", response_class=JSONResponse)
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    start_date: str = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date filter (YYYY-MM-DD)"),
    phone: str = Query(None, description="Filter by specific phone number"),
    direction: str = Query("all", description="Filter by direction: all, incoming, outgoing"),
    response_type: str = Query(None, description="Filter by response type"),
) -> dict:
    """Return recent activity feed with comprehensive filtering."""
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        query = select(WhatsAppChatMessage)

        # Apply filters
        filters = []

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
                filters.append(WhatsAppChatMessage.created_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                filters.append(WhatsAppChatMessage.created_at <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

        if phone:
            filters.append(WhatsAppChatMessage.phone_number == phone)

        if direction != "all":
            filters.append(WhatsAppChatMessage.direction == direction)

        if response_type:
            filters.append(WhatsAppChatMessage.response_type == response_type)

        if filters:
            query = query.where(and_(*filters))

        stmt = query.order_by(WhatsAppChatMessage.created_at.desc()).limit(limit)
        results = db.execute(stmt).scalars().all()

        activities = [
            {
                "phone": row.phone_number,
                "direction": row.direction,
                "text": row.text[:100] + "..." if row.text and len(row.text) > 100 else row.text,
                "response_type": row.response_type,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in results
        ]

        return {
            "activities": activities,
            "count": len(activities),
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "phone": phone,
                "direction": direction,
                "response_type": response_type,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.get("/growth-metrics", response_class=JSONResponse)
async def get_growth_metrics() -> dict:
    """Return growth metrics comparing current vs previous period."""
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # Current period (last 7 days)
        current_start = now - timedelta(days=7)

        # Previous period (7-14 days ago)
        previous_start = now - timedelta(days=14)
        previous_end = now - timedelta(days=7)

        # Messages in current period
        current_messages_stmt = select(func.count(WhatsAppChatMessage.id)).where(
            WhatsAppChatMessage.created_at >= current_start
        )
        current_messages = db.execute(current_messages_stmt).scalar() or 0

        # Messages in previous period
        previous_messages_stmt = select(func.count(WhatsAppChatMessage.id)).where(
            and_(
                WhatsAppChatMessage.created_at >= previous_start,
                WhatsAppChatMessage.created_at < previous_end
            )
        )
        previous_messages = db.execute(previous_messages_stmt).scalar() or 0

        # Users in current period
        current_users_stmt = select(func.count(func.distinct(WhatsAppChatMessage.phone_number))).where(
            WhatsAppChatMessage.created_at >= current_start
        )
        current_users = db.execute(current_users_stmt).scalar() or 0

        # Users in previous period
        previous_users_stmt = select(func.count(func.distinct(WhatsAppChatMessage.phone_number))).where(
            and_(
                WhatsAppChatMessage.created_at >= previous_start,
                WhatsAppChatMessage.created_at < previous_end
            )
        )
        previous_users = db.execute(previous_users_stmt).scalar() or 0

        # Calculate percentage changes
        messages_change = ((current_messages - previous_messages) / previous_messages * 100) if previous_messages > 0 else 0
        users_change = ((current_users - previous_users) / previous_users * 100) if previous_users > 0 else 0

        return {
            "current_period": {
                "messages": current_messages,
                "users": current_users,
            },
            "previous_period": {
                "messages": previous_messages,
                "users": previous_users,
            },
            "change": {
                "messages_percent": round(messages_change, 1),
                "users_percent": round(users_change, 1),
            }
        }
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.get("/conversation-metrics", response_class=JSONResponse)
async def get_conversation_metrics() -> dict:
    """Return conversation quality metrics."""
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        # Average conversation length (messages per user session)
        # Consider a session as messages within 30 minutes of each other

        # Total conversations (users who sent at least one message)
        total_conversations_stmt = select(func.count(func.distinct(WhatsAppChatMessage.phone_number)))
        total_conversations = db.execute(total_conversations_stmt).scalar() or 1

        # Total messages
        total_messages_stmt = select(func.count(WhatsAppChatMessage.id))
        total_messages = db.execute(total_messages_stmt).scalar() or 0

        # Average messages per conversation
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0

        # Incoming vs outgoing ratio
        incoming_stmt = select(func.count(WhatsAppChatMessage.id)).where(
            WhatsAppChatMessage.direction == "incoming"
        )
        incoming_count = db.execute(incoming_stmt).scalar() or 0

        outgoing_stmt = select(func.count(WhatsAppChatMessage.id)).where(
            WhatsAppChatMessage.direction == "outgoing"
        )
        outgoing_count = db.execute(outgoing_stmt).scalar() or 0

        # Response rate (what % of incoming messages got a response)
        response_rate = (outgoing_count / incoming_count * 100) if incoming_count > 0 else 0

        return {
            "total_conversations": total_conversations,
            "avg_messages_per_conversation": round(avg_messages, 2),
            "incoming_messages": incoming_count,
            "outgoing_messages": outgoing_count,
            "response_rate": round(response_rate, 2),
        }
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.get("/system-health", response_class=JSONResponse)
async def get_system_health() -> dict:
    """Return system health status."""
    # Check database
    db_status = "connected" if is_db_available() else "disconnected"

    # Calculate error rate (simplified - in production, track actual errors)
    error_rate = 0.0
    if not is_db_available():
        error_rate = 100.0

    # Calculate uptime
    uptime_seconds = int(time.time() - _app_start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    uptime_str = f"{hours}h {minutes}m"

    # Determine API status
    api_status = "healthy" if db_status == "connected" else "degraded"

    return {
        "api_status": api_status,
        "database_status": db_status,
        "error_rate": error_rate,
        "uptime": uptime_str,
        "last_error": _last_error,
    }


@router.get("/export-chat/{phone}", response_class=JSONResponse)
async def export_user_chat(phone: str) -> dict:
    """Export all chat history for a specific user."""
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        stmt = (
            select(WhatsAppChatMessage)
            .where(WhatsAppChatMessage.phone_number == phone)
            .order_by(WhatsAppChatMessage.created_at.asc())
        )
        results = db.execute(stmt).scalars().all()

        messages = [
            {
                "phone": row.phone_number,
                "direction": row.direction,
                "text": row.text,
                "response_type": row.response_type,
                "media_url": row.media_url,
                "message_id": row.message_id,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in results
        ]

        return {
            "phone": phone,
            "total_messages": len(messages),
            "messages": messages
        }
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


@router.post("/broadcast", response_class=JSONResponse)
async def broadcast_message(
    request: BroadcastRequest,
    user: AdminUser = Depends(require_admin),
) -> dict:
    """Broadcast a message to all active WhatsApp users."""
    log_admin_action(user, "broadcast_message", {"message_length": len(request.message)})
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    db = SessionLocal()
    try:
        # Get active users from last 24 hours
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        stmt = select(func.distinct(ConversationContext.client_id)).where(
            ConversationContext.client_type == "whatsapp",
            ConversationContext.updated_at >= since,
        )
        active_users = db.execute(stmt).scalars().all()

        # In a real implementation, you would:
        # 1. Queue messages to be sent via WhatsApp API
        # 2. Use background tasks to send messages
        # 3. Track delivery status

        # For now, we'll just return the count
        # TODO: Implement actual WhatsApp message sending

        return {
            "sent_count": len(active_users),
            "message": request.message,
            "status": "queued",
        }
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Failed to broadcast: {e}") from e
    finally:
        db.close()


@router.get("/tools-usage", response_class=JSONResponse)
async def get_tools_usage(
    days: int = Query(30, ge=1, le=365),
    user: AdminUser = Depends(require_admin),
) -> dict:
    """Return detailed tools usage analytics."""
    log_admin_action(user, "view_tools_usage", {"days": days})
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    db = SessionLocal()
    try:
        time_range = datetime.now(timezone.utc) - timedelta(days=days)

        # 1. Overall tools usage (total count per tool)
        tools_stmt = (
            select(
                WhatsAppChatMessage.response_type,
                func.count(WhatsAppChatMessage.id).label("count"),
                func.count(func.distinct(WhatsAppChatMessage.phone_number)).label("unique_users")
            )
            .where(
                WhatsAppChatMessage.response_type.isnot(None),
                WhatsAppChatMessage.direction == "outgoing",
                WhatsAppChatMessage.created_at >= time_range
            )
            .group_by(WhatsAppChatMessage.response_type)
            .order_by(func.count(WhatsAppChatMessage.id).desc())
        )
        tools_results = db.execute(tools_stmt).all()

        tools_usage = [
            {
                "tool": row.response_type,
                "usage_count": row.count,
                "unique_users": row.unique_users,
            }
            for row in tools_results if row.response_type
        ]

        # 2. Tools usage trend over time (daily)
        trend_stmt = (
            select(
                func.date(WhatsAppChatMessage.created_at).label("date"),
                WhatsAppChatMessage.response_type,
                func.count(WhatsAppChatMessage.id).label("count")
            )
            .where(
                WhatsAppChatMessage.response_type.isnot(None),
                WhatsAppChatMessage.direction == "outgoing",
                WhatsAppChatMessage.created_at >= time_range
            )
            .group_by(
                func.date(WhatsAppChatMessage.created_at),
                WhatsAppChatMessage.response_type
            )
            .order_by(func.date(WhatsAppChatMessage.created_at))
        )
        trend_results = db.execute(trend_stmt).all()

        # Format trend data by tool
        usage_trend = {}
        for row in trend_results:
            if row.response_type not in usage_trend:
                usage_trend[row.response_type] = []
            usage_trend[row.response_type].append({
                "date": str(row.date),
                "count": row.count
            })

        # 3. Tools usage by hour of day
        hourly_stmt = (
            select(
                WhatsAppChatMessage.response_type,
                extract("hour", WhatsAppChatMessage.created_at).label("hour"),
                func.count(WhatsAppChatMessage.id).label("count")
            )
            .where(
                WhatsAppChatMessage.response_type.isnot(None),
                WhatsAppChatMessage.direction == "outgoing",
                WhatsAppChatMessage.created_at >= time_range
            )
            .group_by(
                WhatsAppChatMessage.response_type,
                extract("hour", WhatsAppChatMessage.created_at)
            )
        )
        hourly_results = db.execute(hourly_stmt).all()

        hourly_usage = {}
        for row in hourly_results:
            if row.response_type not in hourly_usage:
                hourly_usage[row.response_type] = {}
            if row.hour is not None:
                hourly_usage[row.response_type][int(row.hour)] = row.count

        # 4. Top users per tool (top 5)
        top_users_per_tool = {}
        for tool in [t["tool"] for t in tools_usage[:10]]:  # Top 10 tools only
            top_users_stmt = (
                select(
                    WhatsAppChatMessage.phone_number,
                    func.count(WhatsAppChatMessage.id).label("count")
                )
                .where(
                    WhatsAppChatMessage.response_type == tool,
                    WhatsAppChatMessage.created_at >= time_range
                )
                .group_by(WhatsAppChatMessage.phone_number)
                .order_by(func.count(WhatsAppChatMessage.id).desc())
                .limit(5)
            )
            top_users_results = db.execute(top_users_stmt).all()
            top_users_per_tool[tool] = [
                {"phone": row.phone_number, "usage_count": row.count}
                for row in top_users_results
            ]

        # 5. Recent tool usage (last 20 uses)
        recent_stmt = (
            select(
                WhatsAppChatMessage.phone_number,
                WhatsAppChatMessage.response_type,
                WhatsAppChatMessage.created_at
            )
            .where(
                WhatsAppChatMessage.response_type.isnot(None),
                WhatsAppChatMessage.direction == "outgoing",
                WhatsAppChatMessage.created_at >= time_range
            )
            .order_by(WhatsAppChatMessage.created_at.desc())
            .limit(20)
        )
        recent_results = db.execute(recent_stmt).all()
        recent_usage = [
            {
                "phone": row.phone_number,
                "tool": row.response_type,
                "timestamp": row.created_at.isoformat() if row.created_at else None
            }
            for row in recent_results
        ]

        # 6. Calculate total stats
        total_tool_uses = sum(t["usage_count"] for t in tools_usage)
        total_unique_users = len(set(u["phone"] for tool_users in top_users_per_tool.values() for u in tool_users))

        return {
            "tools_usage": tools_usage,
            "usage_trend": usage_trend,
            "hourly_usage": hourly_usage,
            "top_users_per_tool": top_users_per_tool,
            "recent_usage": recent_usage,
            "summary": {
                "total_tools": len(tools_usage),
                "total_tool_uses": total_tool_uses,
                "date_range_days": days,
                "most_popular_tool": tools_usage[0]["tool"] if tools_usage else None,
            }
        }
    except Exception as e:
        global _last_error
        _last_error = str(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}") from e
    finally:
        db.close()


# =====================
# Landing Page Content Management
# =====================

import json
import os
from pathlib import Path

# File to store landing page content
LANDING_CONTENT_FILE = Path(__file__).parent.parent.parent / "data" / "landing_content.json"

# Default landing page content
DEFAULT_LANDING_CONTENT = {
    "hero": {
        "title": "Need an answer?",
        "subtitle": "just",
        "rotatingWords": ["पूछो", "કહો", "ಕೇಳಿ", "అడుగు", "D23"],
        "description": "Your AI assistant that speaks your language. Get instant answers in Hindi, Tamil, Telugu & 11+ regional languages.",
        "ctaPrimary": "Start on WhatsApp",
        "ctaSecondary": "Try Web Chat",
        "whatsappLink": "https://wa.me/918548819349",
    },
    "stats": [
        {"value": "5000+", "label": "Active Users", "icon": "👥"},
        {"value": "11+", "label": "Languages", "icon": "🌐"},
        {"value": "24/7", "label": "Available", "icon": "⚡"},
        {"value": "<2s", "label": "Response", "icon": "🚀"},
    ],
    "languages": [
        {"name": "हिंदी", "code": "hi", "english": "Hindi"},
        {"name": "தமிழ்", "code": "ta", "english": "Tamil"},
        {"name": "తెలుగు", "code": "te", "english": "Telugu"},
        {"name": "ಕನ್ನಡ", "code": "kn", "english": "Kannada"},
        {"name": "മലയാളം", "code": "ml", "english": "Malayalam"},
        {"name": "ગુજરાતી", "code": "gu", "english": "Gujarati"},
        {"name": "मराठी", "code": "mr", "english": "Marathi"},
        {"name": "বাংলা", "code": "bn", "english": "Bengali"},
        {"name": "ਪੰਜਾਬੀ", "code": "pa", "english": "Punjabi"},
        {"name": "ଓଡ଼ିଆ", "code": "or", "english": "Odia"},
        {"name": "English", "code": "en", "english": "English"},
    ],
    "founders": [
        {"name": "Naseer", "role": "Co-Founder & CEO", "twitter": "#", "linkedin": "#"},
        {"name": "Pawan", "role": "Co-Founder & CPO", "twitter": "#", "linkedin": "https://www.linkedin.com/in/pawan-k-singh-119b8a20/"},
        {"name": "Rishi", "role": "Co-Founder & CTO", "twitter": "https://x.com/RishiSi92580328", "linkedin": "https://www.linkedin.com/in/rishi-kumar-5878742a/"},
    ],
    "meta": {
        "title": "D23 AI | Bharat's WhatsApp AI Assistant",
        "description": "Get instant answers in Hindi, Tamil, Telugu & 11+ Indian languages",
    }
}


class LandingContentUpdate(BaseModel):
    hero: Optional[Dict[str, Any]] = None
    stats: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    founders: Optional[List[Dict[str, Any]]] = None
    meta: Optional[Dict[str, Any]] = None


def _ensure_data_dir():
    """Ensure the data directory exists."""
    LANDING_CONTENT_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_landing_content() -> Dict[str, Any]:
    """Load landing page content from file or return defaults."""
    _ensure_data_dir()
    if LANDING_CONTENT_FILE.exists():
        try:
            with open(LANDING_CONTENT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_LANDING_CONTENT.copy()
    return DEFAULT_LANDING_CONTENT.copy()


def _save_landing_content(content: Dict[str, Any]):
    """Save landing page content to file."""
    _ensure_data_dir()
    with open(LANDING_CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


@router.get("/landing-content", response_class=JSONResponse)
async def get_landing_content():
    """Get landing page content. Public endpoint for frontend."""
    return _load_landing_content()


@router.put("/landing-content", response_class=JSONResponse)
async def update_landing_content(
    update: LandingContentUpdate,
    user: AdminUser = Depends(require_admin)
):
    """Update landing page content. Admin only."""
    current = _load_landing_content()

    # Update only the provided fields
    if update.hero:
        current["hero"] = {**current.get("hero", {}), **update.hero}
    if update.stats:
        current["stats"] = update.stats
    if update.languages:
        current["languages"] = update.languages
    if update.founders:
        current["founders"] = update.founders
    if update.meta:
        current["meta"] = {**current.get("meta", {}), **update.meta}

    _save_landing_content(current)
    log_admin_action(user, "update_landing_content", {"updated_fields": list(update.dict(exclude_none=True).keys())})

    return {"success": True, "content": current}


@router.post("/landing-content/reset", response_class=JSONResponse)
async def reset_landing_content(user: AdminUser = Depends(require_admin)):
    """Reset landing page content to defaults. Admin only."""
    _save_landing_content(DEFAULT_LANDING_CONTENT.copy())
    log_admin_action(user, "reset_landing_content", {})
    return {"success": True, "content": DEFAULT_LANDING_CONTENT}
