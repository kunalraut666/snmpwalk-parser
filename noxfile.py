import nox

@nox.session(python=["3.8", "3.9", "3.10"])
def tests(session):
    session.install("pytest", "pytest-cov", "coverage")
    session.install("-e", ".[test]")
    session.run("pytest")

@nox.session
def lint(session):
    session.install("black", "isort", "flake8")
    session.run("black", "--check", ".")
    session.run("isort", "--check-only", ".")
    session.run("flake8", "snmpwalk_parser", "tests")

@nox.session
def typecheck(session):
    session.install("mypy")
    session.run("mypy", "snmpwalk_parser")
