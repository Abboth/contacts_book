from datetime import date
from pydantic import BeforeValidator
from typing import Annotated

from pydantic_extra_types.phone_numbers import PhoneNumberValidator, PhoneNumber


def parse_date(string_date: str) -> date:
    return date.fromisoformat(string_date)


DateValidator = Annotated[date, BeforeValidator(parse_date)]

ValidatorPhone = Annotated[
    PhoneNumber,
    PhoneNumberValidator(
        default_region="PL",
        supported_regions=["PL", "UA", "US"],
        number_format="E164")
]
