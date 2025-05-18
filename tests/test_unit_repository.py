# ------------------------------------------AUTH TESTS------------------------------------------
import unittest

from docutils.nodes import description
from fastapi import HTTPException
from pydantic import EmailStr

import src.core.models
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthSession
from src.auth.repository import update_token
from src.contacts.models import Contact, ContactsPhone, ContactsEmail
from src.contacts.schemas.request_schema import AddContactSchema, ContactUpdateSchema, AddPhoneSchema, \
    PhoneUpdateSchema, AddEmailSchema, EmailUpdateSchema
from src.mail_services.models import Email, EmailTemplates
from src.users.models import User
from src.users.schemas import UserSchema


class TestAsyncAuthRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = MagicMock(id=1)
        self.db_session = AsyncMock(spec=AsyncSession)

    async def test_create_token(self):
        device_type = "mobile"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        expires_at = date.today()

        mocked_session = MagicMock()
        mocked_session.scalar_one_or_none.return_value = None
        self.db_session.execute.return_value = mocked_session

        await update_token(self.user, device_type, token, expires_at, self.db_session)

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    async def test_refresh_token(self):
        device_type = "mobile"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        expires_at = date.today() + timedelta(days=30)

        existing_session = AuthSession(
            id=1,
            user_id=1,
            device_type="mobile",
            refresh_token="old_token",
            expires_at=date(2025, 5, 10)
        )

        mocked_session = MagicMock()
        mocked_session.scalar_one_or_none.return_value = existing_session
        self.db_session.execute.return_value = mocked_session

        await update_token(self.user, device_type, token, expires_at, self.db_session)

        self.assertEqual(existing_session.refresh_token, token, msg="Refresh token should be updated")
        self.assertEqual(existing_session.expires_at, expires_at, msg="Expires at should be updated")

        self.db_session.commit.assert_called_once()
        self.db_session.add.assert_not_called()


# ------------------------------------------CONTACTS TESTS------------------------------------------
from src.contacts import repository as contact_repository


class TestAsyncContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1, profile_slug="test_profile", display_name="test_user", email="test_email")
        self.contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                               birthday=date(2000, 1, 1), description="contact_description", user_id=1)
        self.contacts_list = [Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                      birthday=date.today() + timedelta(days=2),
                                      description="contact_description", user_id=1),

                              Contact(id=2, first_name="second_contact_first_name",
                                      last_name="second_contact_last_name",
                                      birthday=date.today() + timedelta(days=5),
                                      description="second_contact_description", user_id=1),

                              Contact(id=3, first_name="third_contact_first_name", last_name="third_contact_last_name",
                                      birthday=date.today() + timedelta(days=10),
                                      description="third_contact_description", user_id=1)]
        self.db_session = AsyncMock(spec=AsyncSession)

    async def test_show_all_contacts(self):
        limit = 10
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = self.contacts_list
        self.db_session.execute.return_value = mocked_contacts

        result = await contact_repository.show_all_contacts(limit, self.user, self.db_session)

        self.assertEqual(result, self.contacts_list[:limit], msg="Contacts should be returned")
        self.db_session.execute.assert_called_once()

    async def test_show_empty_contacts_list(self):
        limit = 10
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = []
        self.db_session.execute.return_value = mocked_contacts

        with self.assertRaises(HTTPException) as error:
            await contact_repository.show_all_contacts(limit, self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

    async def test_get_contact_by_id(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = self.contact
        self.db_session.execute.return_value = mocked_contacts

        result = await contact_repository.get_contact_by_id(self.contact.id, self.user, self.db_session)

        self.assertEqual(result, self.contact, msg="Contact should be returned")
        self.db_session.execute.assert_called_once()

    async def test_get_contact_by_id_not_found(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = None
        self.db_session.execute.return_value = mocked_contacts

        with self.assertRaises(HTTPException) as error:
            await contact_repository.get_contact_by_id(self.contact.id, self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

    async def test_get_contact_by_name_all(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = self.contacts_list
        self.db_session.execute.return_value = mocked_contacts

        result = await contact_repository.get_contact_by_name(self.contact.first_name, self.user, self.db_session)

        self.assertEqual(result, self.contacts_list, msg="Contact should be returned")
        self.db_session.execute.assert_called_once()

    async def test_get_contact_by_name_just_one(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = [self.contacts_list[1]]
        self.db_session.execute.return_value = mocked_contact

        result = await contact_repository.get_contact_by_name(self.contacts_list[1].first_name, self.user,
                                                              self.db_session)

        self.assertEqual(result, [self.contacts_list[1]], msg="Contact should be returned")
        self.db_session.execute.assert_called_once()

    async def test_get_contact_by_name_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = []
        self.db_session.execute.return_value = mocked_contact

        with self.assertRaises(HTTPException) as error:
            await contact_repository.get_contact_by_name(self.contact.first_name, self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

    async def test_add_contact(self):
        body = AddContactSchema(
            first_name="test_contact_first_name",
            last_name="test_contact_last_name",
            birthday="2000-01-01",
            email="test_email@mail.com",
            mail_tag="test_tag",
            phone_number="321442552",
            phone_tag="test_tag",
            description="test_contact_description"
        )
        result = await contact_repository.add_contact(body, self.user, self.db_session)

        self.assertIsInstance(result, Contact, msg="Should be back Contact object")
        self.assertEqual(result.first_name, body.first_name, msg="First name should be the same")

        email = [e.email for e in result.email]
        phones = [p.phone for p in result.phones]

        self.assertIn(body.email, email, msg="Email should be the same")
        self.assertIn(body.phone_number, phones, msg="Mail tag should be the same")

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_update_contact_birthday_exists(self, mock_get_contact_by_id):
        body = ContactUpdateSchema(
            first_name="test_contact_first_name",
            last_name="test_contact_last_name",
            birthday="2000-03-03",
            description="new_test_contact_description"
        )

        mocked_contact = self.contact
        mock_get_contact_by_id.return_value = mocked_contact

        result = await contact_repository.update_contact(body, self.contact.id, self.user, self.db_session)

        self.assertIsInstance(result, Contact, msg="Should be back Contact object")
        self.assertNotEqual(result.birthday, body.birthday, msg="First name should be the same")
        self.assertEqual(result.description, body.description, msg="Description should be the same")
        self.assertEqual(result.birthday, self.contact.birthday, msg="Birthday not should be changed")
        self.assertEqual(result.id, self.contact.id, msg="Id should be the same")

        self.db_session.commit.assert_called_once()

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_update_contact_birthday_not_exists(self, mock_get_contact_by_id):
        body = ContactUpdateSchema(
            first_name="test_contact_first_name",
            last_name="test_contact_last_name",
            birthday="2000-03-03",
            description="new_test_contact_description"
        )

        mocked_contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                 description="contact_description", user_id=1)
        mock_get_contact_by_id.return_value = mocked_contact

        result = await contact_repository.update_contact(body, self.contact.id, self.user, self.db_session)

        self.assertIsInstance(result, Contact, msg="Should be back Contact object")
        self.assertEqual(result.birthday, body.birthday, msg="First name should be the same")

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_add_phone_tag_exists(self, mock_get_contact_by_id):
        body = AddPhoneSchema(
            phone_number="321442552",
            phone_tag="test_tag"
        )
        mocked_contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                 description="contact_description", user_id=1)
        mock_get_contact_by_id.return_value = mocked_contact

        self.db_session.scalar.return_value = True

        with self.assertRaises(HTTPException) as error:
            await contact_repository.add_phone(body, self.contact.id, self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 409, msg="Status code should be 409")

        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_add_phone(self, mock_get_contact_by_id):
        body = AddPhoneSchema(
            phone_number="321442552",
            phone_tag="tag"
        )

        mocked_contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                 description="contact_description", user_id=1)
        mock_get_contact_by_id.return_value = mocked_contact

        self.db_session.scalar.return_value = False

        result = await contact_repository.add_phone(body, self.contact.id, self.user, self.db_session)

        self.assertIn(body.phone_number, result.phone, msg="Phone should be added")
        self.assertIn(body.phone_tag, result.tag, msg="Tag should be added")

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_update_phone(self, mock_get_contact_by_id):
        body = PhoneUpdateSchema(phone_number="321442552")
        phone = ContactsPhone(id=1, phone="123456789", tag="tag", contact_id=1)
        mocked_phone = MagicMock()
        mocked_phone.scalar_one_or_none.return_value = phone
        self.db_session.execute.return_value = mocked_phone

        mocked_contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                 description="contact_description", user_id=1)
        mock_get_contact_by_id.return_value = mocked_contact

        result = await contact_repository.update_phone(body, self.contact.id, phone.tag, self.user, self.db_session)

        self.assertEqual(result.phone, body.phone_number, msg="Phone should be updated")
        self.assertEqual(result.tag, phone.tag, msg="Tag should be the same")

        self.db_session.commit.assert_called_once()

    async def test_update_phone_incorrect_tag(self):
        body = PhoneUpdateSchema(phone_number="321442552")

        mocked_tag_exist = MagicMock()
        mocked_tag_exist.scalar_one_or_none.return_value = None
        self.db_session.execute.return_value = mocked_tag_exist

        with self.assertRaises(HTTPException) as error:
            await contact_repository.update_email(body, self.contact.id, "incorrect_tag", self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

        self.db_session.commit.assert_not_called()

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_add_mail_tag_exists(self, mock_get_contact_by_id):
        body = AddEmailSchema(
            email="test_email@mail.com",
            mail_tag="test_tag"
        )

        mocked_contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                 description="contact_description", user_id=1)
        mock_get_contact_by_id.return_value = mocked_contact

        self.db_session.scalar.return_value = True

        with self.assertRaises(HTTPException) as error:
            await contact_repository.add_email(body, self.contact.id, self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 409, msg="Status code should be 409")

        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()

    @patch("src.contacts.repository.get_contact_by_id", new_callable=AsyncMock)
    async def test_add_mail(self, mock_get_contact_by_id):
        body = AddEmailSchema(
            email="test_email@mail.com",
            mail_tag="test_tag"
        )

        mocked_contact = Contact(id=1, first_name="contact_first_name", last_name="contact_last_name",
                                 description="contact_description", user_id=1)
        mock_get_contact_by_id.return_value = mocked_contact

        self.db_session.scalar.return_value = False

        result = await contact_repository.add_email(body, self.contact.id, self.user, self.db_session)

        self.assertIn(body.email, result.email, msg="Email should be added")
        self.assertIn(body.mail_tag, result.tag, msg="Tag should be added")

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    async def test_update_mail(self):
        body = EmailUpdateSchema(email="new_test_email@mail.com")
        email = ContactsEmail(id=1, email="test_email@mail.com", tag="tag", contact_id=1)
        mocked_email = MagicMock()
        mocked_email.scalar_one_or_none.return_value = email
        self.db_session.execute.return_value = mocked_email

        result = await contact_repository.update_email(body, self.contact.id, email.tag, self.user, self.db_session)

        self.assertEqual(result.email, body.email, msg="Email should be updated")
        self.assertEqual(result.tag, email.tag, msg="Tag should be the same")

        self.db_session.commit.assert_called_once()

    async def test_update_mail_incorrect_tag(self):
        body = EmailUpdateSchema(email="new_test_email@mail.com")

        mocked_tag_exist = MagicMock()
        mocked_tag_exist.scalar_one_or_none.return_value = None
        self.db_session.execute.return_value = mocked_tag_exist

        with self.assertRaises(HTTPException) as error:
            await contact_repository.update_email(body, self.contact.id, "incorrect_tag", self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

        self.db_session.commit.assert_not_called()

    async def test_get_contacts_birthday(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = self.contacts_list[:2]
        self.db_session.execute.return_value = mocked_contacts

        result = await contact_repository.get_contacts_birthday(self.user, self.db_session)

        self.assertIn(self.contacts_list[0], result, msg="First contacts should be returned")
        self.assertIn(self.contacts_list[1], result, msg="Second contacts should be returned")
        self.assertNotIn(self.contacts_list[2], result, msg="Third contacts should not be returned")
        self.db_session.execute.assert_called_once()

    async def test_get_contacts_birthday_empty(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = []
        self.db_session.execute.return_value = mocked_contacts

        result = await contact_repository.get_contacts_birthday(self.user, self.db_session)

        self.assertEqual(result, [], msg="No contacts should be returned")
        self.db_session.execute.assert_called_once()

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = self.contact
        self.db_session.execute.return_value = mocked_contact

        result = await contact_repository.delete_contact(self.contact.id, self.user, self.db_session)

        self.assertEqual(result, self.contact, msg="Contact should be deleted")
        self.db_session.delete.assert_called_once()
        self.db_session.commit.assert_called_once()

    async def test_delete_contact_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.db_session.execute.return_value = mocked_contact

        with self.assertRaises(HTTPException) as error:
            await contact_repository.delete_contact(self.contact.id, self.user, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

        self.db_session.delete.assert_not_called()


# ------------------------------------------MAIL SERVICE TESTS------------------------------------------
from src.mail_services import repository as mail_repository


class TestAsyncMailRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, profile_slug="test_profile", display_name="test_user", email="test_email")

        self.letter = Email(id=1, status="pending", template_id=1, user_id=1, opened=False)
        self.letter_list = [Email(id=1, status="pending", template_id=1, user_id=1, opened=False),
                            Email(id=2, status="pending", template_id=1, user_id=1, opened=False),
                            Email(id=3, status="pending", template_id=1, user_id=1, opened=False)]

        self.template = EmailTemplates(id=1, name="test_name", subject="test_subject", params={})

        self.template_data_dict = {
            "template_name": "test_name",
            "subject": "test_subject",
            "params": {}
        }

    @patch("src.mail_services.repository.Email")
    async def test_draft_letter(self, MockEmail):
        mocked_letter = MagicMock()
        mocked_letter.id = 42

        MockEmail.return_value = mocked_letter

        result = await mail_repository.draft_letter(self.user, self.db_session)

        self.assertEqual(result, 42, msg="Letter id should be returned")
        self.db_session.add.assert_called_once_with(mocked_letter)
        self.db_session.flush.assert_called_once()
        self.db_session.commit.assert_not_called()

    async def test_get_letter_by_id(self):
        mocked_letter = MagicMock()
        mocked_letter.scalar_one_or_none.return_value = self.letter_list[0]

        self.db_session.execute.return_value = mocked_letter

        result = await mail_repository.get_letter_by_id_async(self.letter.id, self.db_session)

        self.assertEqual(result, self.letter_list[0], msg="First letter should be returned")
        self.assertNotEqual(result, self.letter_list[1], msg="Second letter should not be returned")
        self.assertNotEqual(result, self.letter_list[2], msg="Third letter should not be returned")
        self.db_session.execute.assert_called_once()

    def test_get_template(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.template

        db_session = MagicMock()
        db_session.execute.return_value = mocked_result

        result = mail_repository.get_or_create_template(self.template_data_dict, db_session)

        self.assertEqual(result, self.template, msg="Template should be returned")
        self.assertIsInstance(result, EmailTemplates)

        db_session.execute.assert_called_once()
        db_session.commit.assert_not_called()
        db_session.add.assert_not_called()

    def test_create_template(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None

        db_session = MagicMock()
        db_session.execute.return_value = mocked_result

        result = mail_repository.get_or_create_template(self.template_data_dict, db_session)

        self.assertIsInstance(result, EmailTemplates)
        self.assertEqual(result.name, "test_name")
        self.assertEqual(result.subject, "test_subject")
        self.assertEqual(result.params, {})

        db_session.execute.assert_called_once()
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    @patch("src.mail_services.repository.get_letter_by_id_async")
    async def test_mark_letter_as_opened(self, mock_get_letter_by_id_async):
        mocked_letter = self.letter

        mock_get_letter_by_id_async.return_value = mocked_letter

        await mail_repository.mark_letter_as_opened(self.letter.id, self.db_session)

        self.assertTrue(mocked_letter.opened, msg="Letter should be marked as opened")
        self.assertIsInstance(mocked_letter.opened, bool)
        self.db_session.commit.assert_called_once()

    @patch("src.mail_services.repository.get_letter_by_id_async")
    async def test_mark_letter_as_opened_already_opened(self, mock_get_letter_by_id_async):
        mocked_letter = MagicMock()
        mocked_letter.opened = True

        mock_get_letter_by_id_async.return_value = mocked_letter

        await mail_repository.mark_letter_as_opened(self.letter.id, self.db_session)

        self.assertTrue(mocked_letter.opened, msg="Letter should be marked as opened")
        self.assertIsInstance(mocked_letter.opened, bool)
        self.db_session.commit.assert_not_called()

    @patch("src.mail_services.repository.sync_sessionmanager.session")
    @patch("src.mail_services.repository.get_or_create_template")
    @patch("src.mail_services.repository.get_letter_by_id_sync")
    async def test_letter_register(self, mock_get_letter_by_id_sync, mock_get_or_create_template, mock_session):
        mocked_letter = self.letter

        mock_get_or_create_template.return_value = self.template
        mock_get_letter_by_id_sync.return_value = mocked_letter

        mocked_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mocked_db

        await mail_repository.letter_register(mocked_letter.id, self.template_data_dict)

        self.assertEqual(mocked_letter.status, "sent", msg="Letter status should be sent")
        self.assertEqual(mocked_letter.template_id, self.template.id, msg="Template ID should be assigned")
        mocked_db.commit.assert_called_once()

    @patch("src.mail_services.repository.sync_sessionmanager.session")
    @patch("src.mail_services.repository.get_letter_by_id_sync")
    async def test_letter_register_not_found(self, mock_get_letter_by_id_sync, mock_session):
        mocked_letter = self.letter

        mock_get_letter_by_id_sync.return_value = None

        mocked_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mocked_db

        with self.assertRaises(HTTPException) as error:
            await mail_repository.letter_register(mocked_letter.id, self.template_data_dict)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")
        mocked_db.commit.assert_not_called()


# ------------------------------------------USERS TESTS------------------------------------------
from src.users import repository as users_repository

class TestAsyncUsersRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1, profile_slug="test_profile", display_name="test_user",
                         email="test_email@mail.com", hashed_pwd="password", is_verified=False)
        self.user_list = [User(id=1, profile_slug="test_profile1", display_name="test_user1",
                               email="test_email@mail.com", hashed_pwd="password", is_verified=False),
                          User(id=2, profile_slug="test_profile2", display_name="test_user2",
                               email="test_email2@mail.com", hashed_pwd="password", is_verified=False),
                          User(id=3, profile_slug="test_profile3", display_name="test_user3",
                               email="test_email3@mail.com", hashed_pwd="password", is_verified=False)]
        self.db_session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email_or_none(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user_list[0]

        self.db_session.execute.return_value = mocked_user

        result = await users_repository.get_user_by_email_or_none(self.user.email, self.db_session)

        self.assertEqual(result, self.user_list[0], msg="First user should be returned")
        self.assertNotEqual(result, self.user_list[1], msg="Second user should not be returned")
        self.assertNotEqual(result, self.user_list[2], msg="Third user should not be returned")
        self.db_session.execute.assert_called_once()

    async def test_get_user_by_email_or_none_not_found(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = None

        self.db_session.execute.return_value = mocked_user

        result = await users_repository.get_user_by_email_or_none(self.user.email, self.db_session)

        self.assertIsNone(result, msg="User should be None")
        self.db_session.execute.assert_called_once()

    @patch("src.users.repository.get_user_by_email_or_none")
    async def test_get_user_by_email(self, mock_get_user_by_email_or_none):
        mock_get_user_by_email_or_none.return_value = self.user

        result = await users_repository.get_user_by_email(self.user.email, self.db_session)

        self.assertEqual(result, self.user, msg="User should be returned")

    @patch("src.users.repository.get_user_by_email_or_none")
    async def test_get_user_by_email_not_found(self, mock_get_user_by_email_or_none):
        mock_get_user_by_email_or_none.return_value = None
        with self.assertRaises(HTTPException) as error:
            await users_repository.get_user_by_email(self.user.email, self.db_session)

        self.assertEqual(error.exception.status_code, 404, msg="Status code should be 404")

    @patch("src.users.repository.Gravatar")
    async def test_create_new_user_gravatar_success(self, mock_gravatar):
        body = UserSchema(profile_slug="test_profile",
                          display_name="test_user",
                          email="test_email@mail.com",
                          password="password")

        mock_gravatar_instance = MagicMock()
        mock_gravatar_instance.get_image.return_value = "https://gravatar.com/avatar/link"
        mock_gravatar.return_value = mock_gravatar_instance

        result = await users_repository.create_new_user(body, self.db_session)

        self.assertEqual(body.email, result.email, msg="Email should be match")
        self.assertEqual(body.profile_slug, result.profile_slug, msg="Profile slug should be match")
        self.assertEqual(body.display_name, result.display_name, msg="display_name should be match")
        self.assertEqual(body.password, result.hashed_pwd, msg="Hashed password should be match")
        self.assertEqual(result.avatar, "https://gravatar.com/avatar/link", msg="avatar be returned")

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    @patch("src.users.repository.Gravatar")
    async def test_create_new_user_gravatar_false(self, mock_gravatar):
        body = UserSchema(profile_slug="test_profile",
                          display_name="test_user",
                          email="test_email@mail.com",
                          password="password")

        mock_gravatar_instance = MagicMock()
        mock_gravatar_instance.get_image.return_value = None
        mock_gravatar.return_value = mock_gravatar_instance

        result = await users_repository.create_new_user(body, self.db_session)

        self.assertEqual(body.email, result.email, msg="Email should be match")
        self.assertEqual(body.profile_slug, result.profile_slug, msg="Profile slug should be match")
        self.assertEqual(body.display_name, result.display_name, msg="Display name should be match")
        self.assertEqual(body.password, result.hashed_pwd, msg="Hashed password should be match")
        self.assertIsNone(result.avatar)

        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    @patch("src.users.repository.get_user_by_email")
    async def test_confirm_email(self, mock_get_user):
        mocked_user = MagicMock()
        mocked_user.is_verified = False

        mock_get_user.return_value = mocked_user

        await users_repository.confirmed_email(mock_get_user.email, self.db_session)

        self.assertTrue(mocked_user.is_verified, msg="User should be confirmed")
        self.assertIsInstance(mocked_user.is_verified, bool)
        self.db_session.commit.assert_called_once()

    @patch("src.users.repository.get_user_by_email")
    async def test_change_password(self, mock_get_user):
        mocked_user = MagicMock()
        mocked_user.hashed_pwd = self.user.hashed_pwd

        mock_get_user.return_value = mocked_user

        await users_repository.change_password(self.user.email, "new_password", self.db_session)

        self.assertEqual(mocked_user.hashed_pwd, "new_password", msg="Password should be changed")
        self.db_session.commit.assert_called_once()

    @patch("src.users.repository.get_user_by_email")
    async def test_update_avatar(self, mock_get_user):
        mocked_user = MagicMock()
        mocked_user.avatar = "old_avatar"

        mock_get_user.return_value = mocked_user

        new_avatar = "new_avatar"
        await users_repository.update_avatar(self.user.email, new_avatar, self.db_session)

        self.assertEqual(mocked_user.avatar, new_avatar, msg="Avatar should be updated")
        self.db_session.commit.assert_called_once()

