import logging

from behave import then, when
from compare import ensure, expect
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait


def __get_element_id(element_name: str) -> str:
    return 'inventory_' + "_".join(element_name.lower().split())


@when(u'I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)


@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)


@then(u'I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)


@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    # e.g. 'PRODUCT ID' -> 'inventory_product_id'
    element_id = __get_element_id(element_name)
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


@when(u'I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = __get_element_id(element_name)
    element = Select(context.driver.find_element_by_id(element_id))
    element.select_by_visible_text(text)


@then(u'I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = __get_element_id(element_name)
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)


@then(u'the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = __get_element_id(element_name)
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

##################################################################
# These two function simulate copy and paste
##################################################################


@when(u'I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = __get_element_id(element_name)
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)


@when(u'I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = __get_element_id(element_name)
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when(u'I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + "-btn"
    context.driver.find_element_by_id(button_id).click()


@then(u'I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"),
            message
        )
    )
    expect(found).to_be(True)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Product_ID field has an id='inventory_product_id'
# We can then lowercase the name and prefix with inventory_ to get the id
##################################################################


@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = __get_element_id(element_name)
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)


@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = __get_element_id(element_name)
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
