Feature: Developer workflow is robust across worktrees
  The repository provides scripts and configuration so tests run reliably
  in both the main checkout and git worktrees.

  @api
  Scenario: Required workflow scripts exist
    Then the file scripts/bootstrap-worktree.sh exists and is executable
    And the file scripts/test.sh exists and is executable

  @api
  Scenario: Pytest markers are registered
    When I run uv run pytest --markers
    Then the command exits with status 0
    And the command output contains "api"
    And the command output contains "ui"

  @api
  Scenario: Worktree bootstrap script syntax is valid
    When I run bash -n scripts/bootstrap-worktree.sh
    Then the command exits with status 0
