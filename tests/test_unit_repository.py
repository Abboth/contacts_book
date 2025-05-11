# ------------------------------------------AUTH---------------------------------------
import unittest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


from src.auth.models import AuthSession
from src.auth.repository import update_token


class TestAsyncAuthRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = MagicMock(id=1)
        self.db_session = AsyncMock(spec=AsyncSession)

    async def test_create_token(self):
        device_type = "mobile"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        expires_at = date.today()

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.db_session.execute.return_value = mocked_result

        await update_token(self.user, device_type, token, expires_at, self.db_session)

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()


