from flask import abort, render_template

from . import bp

OWNER_NAME = "Bob Smith"

PROJECTS = [
    {
        "slug": "habit-tracker",
        "title": "Habit tracking app with Python and MongoDB",
        "category": "Python | Web",
        "image": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?auto=format&fit=crop&w=900&q=80",
        "technologies": ["Python", "Flask", "MongoDB"],
        "production_url": "#",
        "description": [
            "A lightweight daily habit tracker built with Flask and MongoDB. "
            "Pick any date on the calendar strip, tick off the habits you completed, "
            "and the app keeps a running log of every day's progress.",
            "The whole UI is server-rendered with Jinja templates, so there's no "
            "client-side framework in the way — just clean routes, a couple of "
            "collections, and a bit of care put into the interaction details.",
        ],
    },
    {
        "slug": "finance-tracker",
        "title": "Personal finance tracking app with React",
        "category": "React | JavaScript",
        "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
        "technologies": ["React", "JavaScript", "Chart.js"],
        "production_url": "#",
        "description": [
            "A single-page app for tracking income and expenses, with a dashboard "
            "of monthly spend broken down by category.",
            "Built with React and a small REST API, it stores transactions locally "
            "and renders interactive charts so trends are easy to spot at a glance.",
        ],
    },
    {
        "slug": "rest-api-docs",
        "title": "REST API Documentation with Postman and Swagger",
        "category": "Writing",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
        "technologies": ["Postman", "Swagger", "OpenAPI"],
        "production_url": "#",
        "description": [
            "Complete reference documentation for a REST API, covering every "
            "endpoint, request/response shape, and authentication flow.",
            "Written alongside a Postman collection and an OpenAPI/Swagger spec "
            "so the docs stay in sync with what the API actually does.",
        ],
    },
]


def _find_project(slug):
    for project in PROJECTS:
        if project["slug"] == slug:
            return project
    return None


@bp.route("/")
def index():
    return render_template(
        "index.html", owner_name=OWNER_NAME, projects=PROJECTS, active="projects"
    )


@bp.route("/about")
def about():
    return render_template("about.html", owner_name=OWNER_NAME, active="about")


@bp.route("/contact")
def contact():
    return render_template("contact.html", owner_name=OWNER_NAME, active="contact")


@bp.route("/project/<slug>")
def detail(slug):
    project = _find_project(slug)
    if project is None:
        abort(404)
    return render_template(
        "detail.html", owner_name=OWNER_NAME, project=project, active="projects"
    )
