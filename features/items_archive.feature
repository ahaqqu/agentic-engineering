Feature: Archive items
  Signed-in users archive items without losing them.

  Background:
    Given I am signed in as "ada@example.com"
    And an item "Buy milk" exists

  @api
  Scenario: Archive endpoint returns the updated row fragment
    When I POST to the archive endpoint for "Buy milk"
    Then the response status is 200
    And the response HTML contains an element "[data-archived='true']"

  @api
  Scenario: A non-member cannot archive the item
    Given I am signed in as "mallory@example.com"
    When I POST to the archive endpoint for "Buy milk"
    Then the response status is 404

  @api
  Scenario: Unauthenticated archive attempt is rejected
    Given I have no session
    When I POST to the archive endpoint for "Buy milk"
    Then the response status is 401

  @ui
  Scenario: Toggling archive updates the row without a page reload
    When I open the items page
    And I click the archive button on "Buy milk"
    Then the row for "Buy milk" shows the archived badge
    And the page did not perform a full navigation

  @ui
  Scenario: Archived state survives a refresh
    When I open the items page
    And I click the archive button on "Buy milk"
    And I reload the page
    Then the row for "Buy milk" shows the archived badge
