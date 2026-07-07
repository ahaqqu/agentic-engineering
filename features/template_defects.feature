Feature: Template scaffolding defects are fixed
  The baseline template uses additive migrations and Pydantic validators on mutation routes.

  Background:
    Given I am signed in as "ada@example.com"

  @api
  Scenario: Create item with valid title returns the row fragment
    When I POST to create item with title "Buy milk"
    Then the response status is 201
    And the response HTML contains an element "[data-archived='false']"

  @api
  Scenario: Create item with empty title returns 422
    When I POST to create item with title ""
    Then the response status is 422

  @api
  Scenario: Create item with too-long title returns 422
    When I POST to create item with title "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    Then the response status is 422

  @api
  Scenario: New items have archived default false after additive migration
    When I POST to create item with title "Survivor"
    Then the response status is 201
    And the response HTML contains an element "[data-archived='false']"
