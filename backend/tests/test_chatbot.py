import pytest
import asyncio
from datetime import date
from unittest.mock import patch
from app.modules.chatbot import service
from app.modules.chatbot.models import ChatSession, ChatMessage
from tests.stubs.schemas import EmployeeOut, LeaveBalanceOut
from app.core.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modules.auth.models import User
from app.modules.gamification.models import PointsLedger



@pytest.mark.asyncio
async def test_build_context_with_stubs(db_session):
    # Mock the dependencies to simulate returning stub schemas
    with patch("app.modules.employee.service.get_employee_by_id") as emp_mock, \
         patch("app.modules.leave.service.get_leave_balance") as leave_mock, \
         patch("app.modules.payroll.service.get_latest_payslip") as pay_mock, \
         patch("app.modules.gamification.service.get_total_points") as points_mock:
         
        emp_mock.return_value = EmployeeOut(id=1, user_id=1, name="Alice", department="Engineering",
                                            designation="Dev", date_of_joining=date.today())
        leave_mock.return_value = LeaveBalanceOut(employee_id=1, paid_remaining=12, sick_remaining=6, unpaid_used=0)
        pay_mock.return_value = None
        points_mock.return_value = 150

        ctx = await service.build_context(db_session, employee_id=1)

    assert ctx["employee"]["name"] == "Alice"
    assert ctx["leave_balance"]["paid_remaining"] == 12
    assert ctx["total_points"] == 150

@pytest.mark.asyncio
async def test_ollama_stream_mocked(db_session):
    async def fake_stream(messages):
        for chunk in ["Hello", " there", "!"]:
            yield chunk

    # Mock the actual Ollama streaming function in the service
    with patch("app.modules.chatbot.service.stream_completion", side_effect=fake_stream):
        session = ChatSession(employee_id=1)
        db_session.add(session)
        db_session.commit()
        chunks = []
        async for chunk in service.handle_message(db_session, session.id, 1, "Hi"):
            chunks.append(chunk)
            
    assert "".join(chunks) == "Hello there!"
    
    # Verify persistence
    msgs = db_session.query(ChatMessage).filter_by(session_id=session.id).order_by(ChatMessage.created_at).all()
    assert len(msgs) == 2  # user + assistant
    assert msgs[1].content == "Hello there!"
