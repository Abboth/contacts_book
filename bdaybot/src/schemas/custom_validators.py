from datetime import date
from pydantic import BeforeValidator
from typing import Annotated

from pydantic_extra_types.phone_numbers import PhoneNumberValidator, PhoneNumber


def parse_date(v: str) -> date:
    return date.fromisoformat(v)


DateValidator = Annotated[date, BeforeValidator(parse_date)]

ValidatorPhone = Annotated[
    PhoneNumber,
    PhoneNumberValidator(
        default_region="PL",
        supported_regions=["PL", "UA", "US"],
        number_format="E164")
]
