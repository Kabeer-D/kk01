Feature: Github homepage core functionalities

  As a user
  I want to use the main features available on the Github homepage
  So that I can complete common tasks successfully

  Scenario: Open homepage
    Given the user is on the homepage
    When they view the main page
    Then they should see the primary navigation and search entry points
