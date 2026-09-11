# app/microblog/__init__.py
from flask import Blueprint
bp = Blueprint("microblog", __name__, template_folder="templates", static_folder="static")
from . import routes  # noqa
