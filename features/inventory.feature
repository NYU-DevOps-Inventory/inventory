Feature: The inventory service back-end
    As an Inventory Owner
    I need a RESTful catalog service
    So that I can keep track of all my inventory

Background:
    Given the following inventory
        | product_id | condition | quantity | restock_level | available |
        | 1          | NEW       | 300      | 100           | True      |
        | 4          | NEW       | 200      | 100           | True      |
        | 8          | NEW       | 100      | 100           | False     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory Demo RESTful Service" in the title
    And  I should not see "404 Not Found"

Scenario: Retrieve an Inventory
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1" in the "Product ID" field
    And I should see "NEW" in the "Condition" dropdown
    And I should see "300" in the "Quantity" field
    And I should see "100" in the "Restock Level" field
    And I should see "True" in the "Available" dropdown

Scenario: Update an Inventory
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I set the "Quantity" to "200"
    And I set the "Restock Level" to "400"
    And I press the "Update" button
    Then I should see the message "Success"
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1" in the "Product ID" field
    And I should see "NEW" in the "Condition" dropdown
    And I should see "200" in the "Quantity" field
    And I should see "400" in the "Restock Level" field
    And I should see "True" in the "Available" dropdown

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

Scenario: Search all Inventory
    When I visit the "Home Page"
    And I select "NEW" in the "Condition" dropdown
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" in the results
    And I should see "4" in the results
    When I press the "Clear" button
    And I set the "Quantity" to "300"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "4" in the results
    And I should see "1" in the results
    And I should see "300" in the "Quantity" field
    And I should see "100" in the "Restock Level" field
    And I should see "True" in the "Available" dropdown
    When I press the "Clear" button
    And I set the "Quantity_low" to "300"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "200" in the results
    And I should see "300" in the results
    When I press the "Clear" button
    And I set the "Quantity_high" to "200"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "300" in the results
    And I should see "200" in the results

Scenario: Delete an Inventory
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Delete" button
    Then I should see the message "Inventory has been Deleted!"
    When I press the "Retrieve" button
    Then I should see the message "404 Not Found: Inventory with product_id '1' and condition 'NEW' was not found."
    And I should not see "Inventory has been Deleted!"

Scenario: Activate an Inventory
    When I visit the "Home Page"
    And I set the "Product ID" to "8"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Activate" button
    Then I should see the message "Success"
    When I visit the "Home Page"
    And I set the "Product ID" to "8"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "8" in the "Product ID" field
    And I should see "NEW" in the "Condition" dropdown
    And I should see "100" in the "Quantity" field
    And I should see "100" in the "Restock Level" field
    And I should see "True" in the "Available" dropdown

Scenario: Deactivate an Inventory
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Deactivate" button
    Then I should see the message "Success"
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1" in the "Product ID" field
    And I should see "NEW" in the "Condition" dropdown
    And I should see "300" in the "Quantity" field
    And I should see "100" in the "Restock Level" field
    And I should see "False" in the "Available" dropdown
