Feature: Wikipedia homepage core functionalities

  As a user
  I want to use the main features available on the Wikipedia homepage
  So that I can complete common tasks successfully

  Scenario: Search Wikipedia Article
    Given the user is on the Wikipedia homepage
    When Automate the process of searching for an article using the main search input and verifying that the article page loads.
    Then the primary experience should be available

  Scenario: User Sign‑In
    Given the user is on the Wikipedia homepage
    When Automate signing in to a Wikipedia account via the login link and confirm successful authentication.
    Then the primary experience should be available

  Scenario: Navigate Primary Site Sections
    Given the user is on the Wikipedia homepage
    When Automate navigation through the primary navigation menu to key Wikipedia sections such as Main page, Contents, and Current events.
    Then the primary experience should be available

  Scenario: Access Random Article
    Given the user is on the Wikipedia homepage
    When Automate the action of opening a random Wikipedia article to test content loading and navigation stability.
    Then the primary experience should be available
