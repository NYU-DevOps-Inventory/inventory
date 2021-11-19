Feature: The inventory service back-end
    As an Inventory Owner
    I need a RESTful catalog service
    So that I can keep track of all my inventory

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory REST API Service"
    And  I should not see "404 Not Found"
