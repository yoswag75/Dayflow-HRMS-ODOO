from sqlalchemy.orm import Session
from app.modules.chatbot.models import ChatSession, ChatMessage
from app.modules.chatbot.ollama_client import stream_completion

async def build_context(db: Session, employee_id: int) -> dict:
    """
    Assembles read-only snapshot from all modules. Always via service functions, never models.
    Import errors are caught so chatbot works even if a module isn't deployed yet.
    """
    context = {}

    try:
        from app.modules.employee.service import get_employee_by_id
        emp = get_employee_by_id(db, employee_id)
        context["employee"] = emp.model_dump() if emp else {}
    except ImportError:
        context["employee"] = {"id": employee_id, "name": f"Employee {employee_id}"}

    try:
        from app.modules.leave.service import get_leave_balance
        balance = get_leave_balance(db, employee_id)
        context["leave_balance"] = balance.model_dump() if balance else {}
    except ImportError:
        context["leave_balance"] = {}

    try:
        from app.modules.payroll.service import get_latest_payslip
        payslip = get_latest_payslip(db, employee_id)
        context["latest_payslip"] = payslip.model_dump() if payslip else {}
    except ImportError:
        context["latest_payslip"] = {}

    try:
        from app.modules.gamification.service import get_total_points
        context["total_points"] = get_total_points(db, employee_id)
    except ImportError:
        context["total_points"] = 0

    return context

def _build_system_prompt(context: dict) -> str:
    emp = context.get("employee", {})
    balance = context.get("leave_balance", {})
    payslip = context.get("latest_payslip", {})
    points = context.get("total_points", 0)
    return f"""You are Dayflow Assistant, an HR chatbot for {emp.get('name', 'this employee')}.
You have access to their live HR data. Answer based ONLY on the data below.

EMPLOYEE PROFILE:
- Name: {emp.get('name', 'N/A')}
- Department: {emp.get('department', 'N/A')}
- Designation: {emp.get('designation', 'N/A')}
- Joined: {emp.get('date_of_joining', 'N/A')}

LEAVE BALANCE:
- Paid Leave Remaining: {balance.get('paid_remaining', 'N/A')} days
- Sick Leave Remaining: {balance.get('sick_remaining', 'N/A')} days
- Unpaid Leave Used: {balance.get('unpaid_used', 'N/A')} days

LATEST PAYSLIP ({payslip.get('month', 'N/A')}/{payslip.get('year', 'N/A')}):
- Gross: Rs {payslip.get('gross', 'N/A')}
- Deductions: Rs {payslip.get('deductions', 'N/A')}
- Net: Rs {payslip.get('net', 'N/A')}

GAMIFICATION:
- Total Points: {points}

Respond professionally. If data is missing, say it is not available. Never invent data."""

async def handle_message(db: Session, session_id: int, employee_id: int, message: str):
    """AsyncGenerator — yields text chunks, persists messages when done."""
    # Persist user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=message)
    db.add(user_msg)
    db.commit()

    # Build prompt
    context = await build_context(db, employee_id)
    system_prompt = _build_system_prompt(context)

    # Get last 20 messages for context window management
    history = (db.query(ChatMessage).filter_by(session_id=session_id)
               .order_by(ChatMessage.created_at).limit(20).all())
    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in history]

    # Stream from Ollama, accumulate
    full_response = ""
    async for chunk in stream_completion(messages):
        full_response += chunk
        yield chunk

    # Persist complete assistant response
    assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=full_response)
    db.add(assistant_msg)
    db.commit()
