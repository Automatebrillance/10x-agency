import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import airtable

# Airtable setup with hard-coded values for demonstration
AIRTABLE_API_KEY = 'patW58995GtHx4BN4.28075217beda1a18795645d602af45b8db94675a421782ccf402168428d00a54'
BASE_ID = 'appI64PUzTzKr7r5H'
TABLE_NAME = 'your_table_name'  # Replace with your actual table name

# Initialize Airtable connection
at = airtable.Airtable(BASE_ID, TABLE_NAME, AIRTABLE_API_KEY)

def fetch_airtable_data(last_run_time=None):
    """
    Fetches data from Airtable. If last_run_time is provided, only fetch records created after that time.
    """
    try:
        if last_run_time:
            # Format the time for Airtable's query (ISO 8601 format)
            filter_formula = f"IS_AFTER(CREATED_TIME(), '{last_run_time.isoformat()}')"
            records = at.get_all(filterByFormula=filter_formula)
        else:
            records = at.get_all()
        return records
    except Exception as e:
        print(f"Error fetching data from Airtable: {e}")
        return None

def login_to_facebook(driver, email, password):
    """Logs into Facebook using provided credentials."""
    try:
        driver.get('https://www.facebook.com/login')
        email_elem = driver.find_element('name', 'email')
        password_elem = driver.find_element('name', 'pass')
        email_elem.send_keys(email)
        password_elem.send_keys(password)
        password_elem.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for login to complete
        print("Login successful.")
    except NoSuchElementException as e:
        print(f"Error during login: {e}")
    except TimeoutException:
        print("Login process timed out.")

def navigate_to_group(driver, group_url):
    """Navigates to the specified Facebook group."""
    try:
        driver.get(group_url)
        time.sleep(5)  # Wait for the group page to load
        print("Navigated to group.")
    except TimeoutException:
        print("Navigation to group timed out.")

def main():
    # Track the last run time; you could persist this across runs if needed
    last_run_time = datetime.utcnow() - timedelta(hours=1)  # Example: fetch records from the last hour

    # Fetch data from Airtable filtered by time
    records = fetch_airtable_data(last_run_time)
    if not records:
        return

    # Initialize browser automation
    driver = webdriver.Chrome(ChromeDriverManager().install())

    try:
        # Extract Facebook login details from Airtable
        for record in records:
            facebook_email = record['fields'].get('Facebook Phone Number/Email')
            facebook_password = record['fields'].get('Facebook Password')
            group_url = record['fields'].get('Group URL')

            if not facebook_email or not facebook_password or not group_url:
                print("Missing required fields in Airtable record.")
                continue

            # Log in to Facebook
            login_to_facebook(driver, facebook_email, facebook_password)

            # Navigate to Group and send messages
            navigate_to_group(driver, group_url)

            # Add logic here to send messages
            # Example:
            # message_elem = driver.find_element_by_xpath('xpath_to_message_input')
            # message_elem.send_keys('Your message here')
            # message_elem.send_keys(Keys.RETURN)

    finally:
        driver.quit()
        print("Browser session ended.")

if __name__ == "__main__":
    main()
