Feature: The inventory service back-end
    As an Inventory Owner
    I need a RESTful catalog service
    So that I can keep track of all my inventory

Background:
    Given the following inventory
        | product_id | condition | quantity | restock_level | available |
        | 1          | NEW       | 300      | 100           | True      |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory Demo RESTful Service" in the title
    And  I should not see "404 Not Found"

Scenario: Create an Inventory
    When I visit the "Home Page"
    And I set the "Product ID" to "2"
    And I select "NEW" in the "Condition" dropdown
    And I set the "Quantity" to "300"
    And I set the "Restock Level" to "100"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Product ID" field
    And I press the "Clear" button
    Then the "Product ID" field should be empty
    And the "Quantity" field should be empty
    And the "Restock Level" field should be empty
    When I paste the "Product ID" field
    And I select "NEW" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "2" in the "Product ID" field
    And I should see "NEW" in the "Condition" dropdown
    Then I should see "300" in the "Quantity" field
    Then I should see "100" in the "Restock Level" field
    And I should see "True" in the "Available" dropdown
