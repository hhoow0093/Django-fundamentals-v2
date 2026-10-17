# Django Fundamentals

This repository is a learning project for working through the official Django
tutorials. The goal is to learn Django itself while also gradually learning the
tools commonly used to manage and check a Python project.

The tooling is here to support learning, not to make the project "production
ready" by itself. Django features, deployment, database operations, and testing
still need to be learned and configured for the particular application.

## What is in this project

For a step-by-step explanation of the environment, tool configuration, CI,
and troubleshooting, see the [development setup walkthrough](./docs/development-setup.md).

- `mysite/` contains the Django project configuration: settings, URL routing,
  and ASGI/WSGI entry points.
- `mysite/polls/` is the tutorial application. An app is a Django component
  that groups related models, views, tests, and migrations.
- `pyproject.toml` describes the Python package, runtime dependencies, optional
  development tools, and their Ruff, mypy, and Bandit configuration.
- `uv.lock` records exact dependency versions so local and CI installs can be
  reproduced.
- `.pre-commit-config.yaml` defines checks that can run before a local commit.
- `.github/workflows/lint.yml` defines automated checks for GitHub Actions.
- `.python-version` selects the Python version used by uv (Python 3.14).
- `mysite/local_settings.py` is an optional local-only settings override and
  is excluded from Git.

## Dependencies and reproducible setup

The project requires Python 3.14 or newer. Runtime dependencies are in the
`[project].dependencies` list: Django and `psycopg[binary]`, the PostgreSQL
database adapter. Development dependencies are in the `dev` dependency group:
Ruff, mypy, Bandit, pre-commit, and Django's typing support (`django-stubs`).
Keeping development tools separate means they are not required just to run the
application.

`uv.lock` pins the resolved versions (including transitive dependencies).
`uv sync --locked` installs from that lockfile and fails if the lockfile needs
updating, helping prevent "works on my machine" differences.

```bash
uv sync --locked --group dev
export DJANGO_SECRET_KEY="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(50))')"
```

`DJANGO_SECRET_KEY` is configuration, not source code. Django uses it for
cryptographic signing, so a real key should not be committed or reused in
public examples. The command above creates a local development key. GitHub
Actions uses a separate throwaway value for its checks.

The default database in `mysite/settings.py` is SQLite, which keeps the
tutorial easy to run locally. If `mysite/local_settings.py` is present, its
settings override the defaults; this is where this project can select local
PostgreSQL settings without committing machine-specific credentials. Installing
the `psycopg` dependency does not by itself switch Django to PostgreSQL.

## Quality checks

### Ruff

Ruff checks Python code for common mistakes and style issues, and formats it.
Its configuration lives in `pyproject.toml`; the pre-commit hooks run the
project's locked Ruff version through uv. Ruff can automatically fix some
issues, so review changes made by the hook.

### mypy and Django typing

mypy checks type annotations and catches some incompatible or missing types
before runtime. Django does not provide all the type information mypy needs,
so this project includes `django-stubs` and its Django plugin. The plugin is
configured with `mysite.settings`, and mypy checks the configured `mysite/`
source.

The local PostgreSQL `DATABASES` override is annotated as
`dict[str, dict[str, object]]`. This gives it a compatible type with the
default SQLite database configuration, whose `NAME` value is a `Path` rather
than a string. Without a shared annotation, mypy inferred different nested
dictionary types and reported an incompatible wildcard-import override.

### Bandit

Bandit looks for patterns that may be security problems, such as hard-coded
secrets. It is a static check, not a guarantee that the application is secure;
findings still need to be assessed in context.

### pre-commit

`pre-commit` runs the configured hooks on files before a local commit. Install
the Git hook once after syncing dependencies:

```bash
uv run pre-commit install
```

Run all configured checks manually with:

```bash
uv run pre-commit run --all-files
```

The project hooks use `uv run --locked`, so they use the same dependency
versions as the rest of the project. Ruff and Bandit check applicable files;
mypy runs over the configured project source even when only a subset of files
has changed.

## GitHub Actions

The workflow sets up Python 3.14 and uv, installs the locked development
environment, runs pre-commit, and runs Django's system check and test command.
The workflow currently triggers on pushes to branches other than `main`; its
pull-request-specific hook step will only run if a pull-request trigger is
configured.

The test command is in place, but `mysite/polls/tests.py` is currently a
placeholder, so Django reports that it found zero tests. A successful command
with zero tests means the test runner works; it does not yet demonstrate
application behavior. Add test cases as the tutorial app gains behavior.

## Commands to practice

```bash
# Check project configuration
uv run python manage.py check

# Run Django tests
uv run python manage.py test

# Run lint, formatting, security, and type checks
uv run pre-commit run --all-files
```

## What I learned while setting this up

Several issues came from making separate tools agree with the actual project:

1. CI initially installed only pre-commit, while the mypy hook expected mypy
   to already be available. Installing the locked `dev` group fixes the
   environment mismatch.
2. A configured source directory must match the repository. The original
   `src/` target did not exist; the Django project lives in `mysite/`.
3. Django code needs type information for strict mypy checks. Adding
   `django-stubs` and configuring its plugin provides that information, while
   the explicit `ALLOWED_HOSTS` annotation resolves a genuine strict typing
   complaint.
4. A development secret should not live in settings committed to Git. Reading
   it from `DJANGO_SECRET_KEY` keeps configuration out of source and lets CI
   provide its own temporary value.
5. A database settings override can expose type-inference conflicts even when
   both configurations work at runtime. The shared `DATABASES` annotation
   documents the common shape and resolves mypy's assignment error.
6. A green CI command is only as useful as the checks it actually runs. The
   Django test command currently runs zero tests, so writing tests is the next
   step for verifying application behavior.

These are normal integration problems, not evidence that you are "bad at
programming." Each tool has its own model of the project: uv resolves
dependencies, Django loads settings dynamically, mypy reasons about types,
Ruff checks style and common errors, Bandit scans security patterns, and
GitHub Actions runs commands in a fresh environment. At first, connecting
those models is an advanced-feeling task even for experienced developers.

A reliable way to learn is to handle one layer at a time:

1. Make the smallest Django example work.
2. Add one tool and understand what it checks.
3. Read the exact error and trace it to its source rather than silencing it.
4. Re-run the failing check after the change.
5. Keep notes about why the setting exists so you can recognize the pattern
   next time.

You do not need to understand every setting before continuing the tutorial.
The aim is to build that understanding gradually and keep the project runnable
while you do.

## Learning materials

### Official Django tutorial

- [Tutorial 1: Writing your first Django app, part 1](https://docs.djangoproject.com/en/6.1/intro/tutorial01/) — Project setup, the development server, apps, views, and URL routing.
- [Tutorial 2: Writing your first Django app, part 2](https://docs.djangoproject.com/en/6.1/intro/tutorial02/) — Database configuration, migrations, models, and the admin.
- [Tutorial 3: Writing your first Django app, part 3](https://docs.djangoproject.com/en/6.1/intro/tutorial03/) — Views, 404 handling, templates, and dynamic responses.
- [Tutorial 4: Writing your first Django app, part 4](https://docs.djangoproject.com/en/6.1/intro/tutorial04/) — Forms, POST requests, validation, and generic views.
- [Tutorial 5: Writing your first Django app, part 5](https://docs.djangoproject.com/en/6.1/intro/tutorial05/) — Automated tests for models and views.
- [Tutorial 6: Writing your first Django app, part 6](https://docs.djangoproject.com/en/6.1/intro/tutorial06/) — Static files.
- [Tutorial 7: Writing your first Django app, part 7](https://docs.djangoproject.com/en/6.1/intro/tutorial07/) — Admin customization.
- [Tutorial 8: Writing your first Django app, part 8](https://docs.djangoproject.com/en/6.1/intro/tutorial08/) — Third-party packages and further customization.

### Django Ninja (future learning)

- [Tutorial part 1](https://django-ninja.dev/tutorial/part-1/) — API setup, routers, and endpoints.
- [Tutorial part 2](https://django-ninja.dev/tutorial/part-2/) — Schemas, validation, and serialization.
- [Tutorial part 3](https://django-ninja.dev/tutorial/part-3/) — Database operations and CRUD.
- [Tutorial part 4](https://django-ninja.dev/tutorial/part-4/) — Authentication and permissions.
- [Tutorial part 5](https://django-ninja.dev/tutorial/part-5/) — Filters, search, and ordering.
- [Tutorial part 6](https://django-ninja.dev/tutorial/part-6/) — Pagination.
- [Tutorial part 7](https://django-ninja.dev/tutorial/part-7/) — API tests.
- [Tutorial part 8](https://django-ninja.dev/tutorial/part-8/) — Async support and deployment topics.
