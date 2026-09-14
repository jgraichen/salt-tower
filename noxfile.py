import os

import nox
from nox import Session

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@nox.session
@nox.parametrize(
    "python,salt",
    [
        # Python versions as shipped in salt's onedir packages, to test
        # against what users actually run.
        nox.param("3.11", 3006, id="salt3006"),
        nox.param("3.14", 3008, id="salt3008"),
    ],
)
def test(s: Session, salt: int) -> None:
    s.install(
        "--verbose",
        ".",
        f"salt~={salt}.0",
        "--group=test",
    )

    s.run("uv", "pip", "list")

    s.run("salt", "--versions-report")

    # Load the pillar and renderer modules from the installed package
    # via salt's loader entry points instead of the test fixtures.
    s.run("pytest", *s.posargs, env={"USE_PACKAGE": os.getenv("USE_PACKAGE", "yes")})
    s.run("pylint", "salt_tower", "test")


@nox.session
def lint(s: Session) -> None:
    s.install("--group=lint")
    s.run("uv", "pip", "list")

    s.run("ruff", "check", "--no-fix", ".")
    s.run("ruff", "format", "--diff", "--check", ".")
