import os
import subprocess
from pathlib import Path

from pytest_bdd import scenario, then, when, parsers

PROJECT_ROOT = Path(__file__).parent.parent.parent


@scenario("../workflow.feature", "Required workflow scripts exist")
def test_scripts_exist():
    pass


@scenario("../workflow.feature", "Pytest markers are registered")
def test_pytest_markers():
    pass


@scenario("../workflow.feature", "Worktree bootstrap script syntax is valid")
def test_bootstrap_syntax():
    pass


@then(parsers.parse("the file {path} exists and is executable"))
def file_exists_executable(path):
    full = PROJECT_ROOT / path
    assert full.exists(), f"{path} does not exist"
    assert os.access(full, os.X_OK), f"{path} is not executable"


@when(parsers.parse("I run {command}"))
def run_command(command, ctx):
    proc = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        shell=True,
        capture_output=True,
        text=True,
    )
    ctx["exit_code"] = proc.returncode
    ctx["stdout"] = proc.stdout
    ctx["stderr"] = proc.stderr


@then(parsers.parse("the command exits with status {status:d}"))
def check_exit_status(status, ctx):
    actual = ctx.get("exit_code")
    output = ctx.get("stdout", "") + "\n" + ctx.get("stderr", "")
    assert actual == status, f"expected exit status {status}, got {actual}\n{output}"


@then(parsers.parse('the command output contains "{text}"'))
def check_output_contains(text, ctx):
    output = ctx.get("stdout", "") + ctx.get("stderr", "")
    assert text in output, f"expected {text!r} not found in:\n{output}"
