Contact Book API
A simple contact management system built with FastAPI.

Features

CRUD operations for contacts (only for authenticated users) # TODO EDITE NEW CONCEPTION

Contact search by name, or id

Get contacts with upcoming birthdays (within 7 days)

Setup

poetry install
alembic upgrade head
uvicorn uvicorn contacts_book.app:app --reload
