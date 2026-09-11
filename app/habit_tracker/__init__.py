# app/habit_tracker/__init__.py
from flask import Blueprint
bp = Blueprint(
    "habit_tracker",
    __name__,
    template_folder="templates",
    static_folder="static",
)
from . import routes  # noqa
