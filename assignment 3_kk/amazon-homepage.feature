Feature: Amazon homepage core functionalities

  As a user
  I want to use the main features available on the Amazon homepage
  So that I can complete common tasks successfully

  Scenario: Search Product
    Given the user is on the Amazon homepage
    When Search for products
    Then the primary experience should be available
