from alembic import op

from contacts_book.src.auth.models import AuthSession
from contacts_book.src.users.models import Role, User
from contacts_book.src.mail_services.models import EmailTemplates, Email
