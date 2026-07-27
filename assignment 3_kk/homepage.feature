Feature: Flipkart homepage core functionalities

  As a user
  I want to use the main features available on the Flipkart homepage
  So that I can complete common tasks successfully

  Scenario: Product Search
    Given the user is on the Flipkart homepage
    When User searches for a product using the main search box and initiates the search.
    Then the primary experience should be available

  Scenario: User Sign‑In
    Given the user is on the Flipkart homepage
    When Existing user logs into their Flipkart account via the sign‑in button.
    Then the primary experience should be available

  Scenario: Add Product to Cart
    Given the user is on the Flipkart homepage
    When User selects a product from search or category results and adds it to the shopping cart.
    Then the primary experience should be available

  Scenario: View Cart and Proceed to Checkout
    Given the user is on the Flipkart homepage
    When User opens the cart to review items and initiates the checkout process.
    Then the primary experience should be available

  Scenario: Browse Daily Deals
    Given the user is on the Flipkart homepage
    When User navigates to the deals/offers section to view discounted products.
    Then the primary experience should be available

  Scenario: Navigate Through Top Categories
    Given the user is on the Flipkart homepage
    When User uses the top navigation menu to explore different product categories.
    Then the primary experience should be available

  Scenario: Access Account Options
    Given the user is on the Flipkart homepage
    When After signing in, user opens the account dropdown to manage profile, orders, or logout.
    Then the primary experience should be available
