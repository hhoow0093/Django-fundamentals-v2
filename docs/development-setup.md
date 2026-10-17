# Development Setup: Technical Walkthrough

This guide explains how this Django learning project is configured and why its
development tools are present. It describes the current repository setup, not a
generic production deployment recipe.

## 1. Project layout and responsibilities

- `mysite/` is the Django project package. It holds project-wide settings and
  URL routing.
- `mysite/polls/` is a Django app. Apps group related models, views, tests, and
  migrations; the `polls` app is nested inside the project package here.
- `pyproject.toml` declares the project, supported Python version, dependency
  groups, and tool configuration.
- `uv.lock` records the resolved versions, including transitive dependencies.
- `.python-version` selects Python 3.14 when using uv.
- `.pre-commit-config.yaml` defines local Git pre-commit hooks.
- `.github/workflows/lint.yml` defines checks that run on GitHub Actions.
- `mysite/local_settings.py` is a machine-specific override ignored by Git.

The separation matters: Django owns application behavior; uv manages Python
and packages; Ruff, mypy, and Bandit inspect different aspects of source code;
pre-commit coordinates local checks; and GitHub Actions repeats checks in a
clean hosted environment.

## 2. Python and dependency setup

The `[project]` section of `pyproject.toml` includes:

- `requires-python = ">=3.14"`: the project declares Python 3.14 as its minimum.
- `dependencies`: packages required at runtime. Django is the web framework;
  `psycopg[binary]` provides the PostgreSQL driver and its binary extra.
- `[dependency-groups].dev`: development-only tools. These include Ruff,
  mypy, Bandit, pre-commit, and `django-stubs[compatible-mypy]`.

Separating development tools from runtime requirements avoids requiring lint
and analysis tools just to install or run the application. `django-stubs`
provides type information for Django APIs that mypy cannot fully infer from
Django itself.

Use the lockfile when installing:

```bash
uv sync --locked --group dev
```

`--group dev` installs the development tools as well as runtime requirements.
`--locked` asks uv to use the checked-in lockfile without silently changing it;
if the dependency declarations and lockfile disagree, uv reports that instead
of resolving a different environment. After intentionally changing
dependencies, update and review the lockfile, then verify with
`uv lock --check`.

## 3. Why settings use environment and local configuration

### Secret key

`mysite/settings.py` reads `DJANGO_SECRET_KEY` from the environment rather than
containing a committed key. Django uses this value for signing and related
cryptographic operations. A key committed to source control could be copied
and reused by others, so use a fresh local value and keep real deployment keys
in a secret manager.

For local development, create a key and export it in the current shell:

```bash
export DJANGO_SECRET_KEY="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(50))')"
```

The workflow supplies its own disposable test value. It is not a production
secret.

### Database selection

The default `DATABASES` setting uses SQLite and stores its file under the
project directory. This keeps early tutorial steps easy to run. The
`psycopg[binary]` dependency only installs a PostgreSQL driver; it does not
switch Django's configured database.

When present, `mysite/local_settings.py` overrides settings from
`mysite/settings.py`. It is ignored by Git to keep local database choices and
credentials out of commits. The example currently has literal PostgreSQL
connection values, so treat it as a local learning example only: do not put
real/shared credentials there, and do not use these values for deployment.
Prefer environment variables for credentials if expanding this setup.

The local `DATABASES` declaration is annotated as
`dict[str, dict[str, object]]`. The default SQLite settings have a `Path` in
`NAME`, while PostgreSQL connection values are strings. Without a common
annotation, mypy infers incompatible nested dictionary types when the
`local_settings` wildcard import overrides `DATABASES`. The annotation
describes the broad shape needed by these two configurations; it does not
validate Django's database options at runtime.

## 4. `pyproject.toml`: Ruff

Ruff combines a fast Python linter and formatter.

### General Ruff options

```toml
[tool.ruff]
line-length = 100
target-version = "py314"
src = ["mysite"]
```

- `line-length` sets the preferred maximum line width.
- `target-version` tells Ruff which Python syntax/features the project targets.
- `src` identifies the project's import/source root. It must match the
  repository layout; this project uses `mysite/`, not a conventional but
  nonexistent `src/` directory.

### Lint rule selection

`[tool.ruff.lint].select` enables rule families:

- `E`, `F`, `W`: pycodestyle and pyflakes errors/warnings.
- `I`: import sorting.
- `B`: common bugbear correctness patterns.
- `UP`: suggestions for modern Python syntax.
- `SIM`: simplification suggestions.

`ignore = []` means no extra rules are disabled globally. Lint rule sets can
be expanded or narrowed as the project grows; enabling a rule is useful only
if its findings are understood and addressed.

`[tool.ruff.lint.per-file-ignores]` can make exceptions for specific file
patterns. The current `tests/**` pattern is intended for tests, but because the
current app's test module is `mysite/polls/tests.py`, review the pattern if
test-specific Ruff rules are added.

Useful commands:

```bash
uv run --locked ruff check .
uv run --locked ruff check --fix .
uv run --locked ruff format --check .
uv run --locked ruff format .
```

`check --fix` may edit files. Review those edits rather than treating an
automatic fix as proof that the result expresses the intended behavior.

## 5. `pyproject.toml`: mypy and Django stubs

The `[tool.mypy]` section currently enables strict checking:

- `python_version = "3.14"` sets the type-checker's Python language target.
- `strict = true` enables a collection of stronger checks, including requiring
  type annotations in many cases.
- `warn_unused_ignores = true` warns when an ignore comment is no longer
  needed.
- `show_error_codes = true` prints stable identifiers (such as `assignment`)
  that help explain and selectively configure errors.
- `files = ["mysite"]` identifies the configured checking target.
- `plugins = ["mypy_django_plugin.main"]` enables Django-specific type
  behavior.

`[tool.django-stubs]` sets `django_settings_module = "mysite.settings"` so the
plugin can initialize Django with the project's settings. That means mypy
needs environment required during settings import, including `DJANGO_SECRET_KEY`.

Run the check with:

```bash
uv run --locked mypy --config-file=pyproject.toml
```

If settings require environment variables, export them first. Do not respond to
a type error by immediately adding `# type: ignore`: first check whether the
target path is right, whether a dependency needs stubs, whether two inferred
types really differ, and whether an explicit annotation can express the
intended relationship.

## 6. `pyproject.toml`: Bandit

Bandit searches Python source for patterns that may indicate security issues.
It is a static-analysis aid, not a complete security audit and not a substitute
for understanding how application behavior is exposed.

The current `[tool.bandit]` section excludes directories named `tests` and
`.venv` and does not skip any rule IDs (`skips = []`). Separately, the
pre-commit hook excludes files under or named like `test`/`tests`. Because the
current app uses `mysite/polls/tests.py` rather than a `tests/` directory, it is
the hook's file exclusion that keeps that file out of hook scans. If tests
begin to contain security-sensitive code, consider whether they should also
be scanned.

The `bandit[toml]` development dependency enables reading configuration from
`pyproject.toml`. Run Bandit directly with:

```bash
uv run --locked bandit -c pyproject.toml -r mysite
```

Investigate findings in context. Avoid suppressing a rule just to make a check
green; if an exception is truly intentional, document the reason narrowly.

## 7. Pre-commit hooks

The config uses `repo: local` hooks, so each command runs tools installed in
the project's uv environment rather than building a separate hook-managed
environment. Each entry starts with `uv run --locked`, helping local hooks use
the same locked tool versions as CI.

Configured hooks:

1. Ruff lint: checks Python files and can apply safe fixes.
2. Ruff format: formats Python files.
3. Bandit: scans applicable Python files, excluding test paths.
4. mypy: checks the configured project rather than only the changed filenames.

For mypy, `pass_filenames: false` prevents pre-commit from appending only the
changed files to its command. `always_run: true` means it still runs when no
changed file matches the hook's file type selection. This is useful because
type relationships can cross file boundaries. `require_serial: true` avoids
running this whole-project check concurrently multiple times.

Install the Git hook once per checkout:

```bash
uv run --locked pre-commit install
```

Run checks manually:

```bash
uv run --locked pre-commit run --all-files
```

Pre-commit normally checks files Git knows about; newly created untracked files
may not be included by `--all-files`. Stage new files or run Ruff, Bandit, and
mypy directly when validating new work before staging it.

## 8. GitHub Actions CI

The workflow grants only `contents: read`, checks out the repository, installs
Python 3.14 and uv, then runs:

```bash
uv sync --locked --group dev
uv run --locked pre-commit run --all-files
uv run --locked python manage.py check
uv run --locked python manage.py test
```

The lockfile makes the CI development environment consistent with local
development. `manage.py check` runs Django's system checks. `manage.py test`
uses Django's test runner, but at present the `mysite/polls/tests.py` file is only a
placeholder, so the runner finds zero tests. A passing zero-test run confirms
the command works; it does not validate application behavior.

### Important: current workflow triggers

The current workflow trigger is:

```yaml
on:
  push:
    branches-ignore:
      - main
```

Therefore it runs on pushes to branches other than `main`. It does **not**
currently run on pull requests, and it does **not** run on pushes to `main`.
Consequently, the workflow's step guarded by `github.event_name == 'pull_request'`
is currently unreachable; pushes to other branches take the `push` step and
run all hooks. If the intended policy is PR validation and a safety run on
`main`, add the desired `pull_request` and `push` triggers explicitly and
confirm branch filters match the repository's default branch. Trigger
configuration determines whether CI actually protects a branch; having a
workflow file alone does not guarantee it runs for every contribution.

The `fetch-depth: 0` checkout provides full Git history, which is needed for
pre-commit's changed-file comparison when using `--from-ref` and `--to-ref`.
If CI switches to always running `--all-files`, the history requirement may no
longer be necessary.

The concurrency group uses the Git ref and cancels older in-progress runs for
the same ref, saving time when multiple commits arrive quickly. The read-only
permission limits the workflow's repository access because these checks do not
need to write code or create releases.

## 9. Troubleshooting the setup

### "Cannot read file: src"

The configured source path does not exist. Point Ruff/mypy to the actual
package paths, then rerun the exact check.

### mypy reports Django modules as untyped

Install Django's stubs in the development group and configure the Django
plugin. Check that mypy is running from the uv environment and that
`django_settings_module` points to the real settings module.

### mypy reports an incompatible `DATABASES` assignment

Compare the inferred types in the default settings and local override. A
SQLite `NAME` can be a `Path`; a PostgreSQL config commonly uses strings for
all values. Give the override a compatible explicit type rather than broadly
disabling mypy.

### `DJANGO_SECRET_KEY` is missing

Export a development key in the current shell. The shell environment is not
automatically shared with every terminal or editor; set it in the environment
used to run Django, mypy, or the test runner. CI has its own job-level value.

### Pre-commit passes but direct commands fail, or vice versa

Verify that dependencies are synced with `uv sync --locked --group dev`, that
the same Python version is active, and that both invocations use this
repository's config. Pre-commit may filter files; direct commands may scan
more files or use different arguments. Compare the exact commands before
changing the rules.

## 10. Suggested learning sequence

This setup combines several concerns, so learn it incrementally:

1. Run the Django project and understand its URL, settings, and app structure.
2. Add a model and migration; use `manage.py check` to validate configuration.
3. Write a Django test and run it with `manage.py test`.
4. Run Ruff and read the rule explanation before applying a fix.
5. Add type annotations and learn mypy diagnostics in the code you wrote.
6. Review Bandit findings and understand the security pattern it detected.
7. Run the same commands locally that CI runs.

These are advanced-feeling integration tasks because each tool has its own
configuration and assumptions. That is a normal part of learning, not a sign
that a beginner should avoid them. The practical skill is to make one change
at a time, understand which tool produced an error, fix the source of the
problem, and rerun the check that exposed it.
