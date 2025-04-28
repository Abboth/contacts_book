from theregram_proj.src.auth.security import auth_security
from theregram_proj.src.mail_services.schemas import EmailTemplateSchema
from theregram_proj.src.users.models import User


async def prepare_email_verification(user: User, host: str, token, tracking_token):
    template_data = EmailTemplateSchema(
        subject="Confirm your email",
        template_name="email_verification.html",
        params={"host": host, "username": user.username, "token": token, "tracking_token": tracking_token}
    )
    return template_data


async def prepare_password_reset(user: User, host: str, token, tracking_token):
    template_data = EmailTemplateSchema(
        subject="Reset your password",
        template_name="reset_password_request.html",
        params={"host": host, "username": user.username, "token": token, "tracking_token": tracking_token}
    )
    return template_data
