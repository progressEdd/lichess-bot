from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import random

from dotenv import load_dotenv
import json

import os
import datetime
load_dotenv()

driver = webdriver.Firefox()
driver.set_window_size(1920, 1080)

def login():
    username = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    driver.get('https://lichess.org/')

    # Wait until the login element is visible
    login_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href="/login?referrer=/"].signin.button.button-empty'))
    )
    login_element.click()

    # Wait until the username element is visible
    username_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "form3-username"))
    )
    # username_element.send_keys(username)    
    for char in username:
        username_element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

    time.sleep(5)
    username_element.send_keys(Keys.TAB)

    # You can use the same method for the password element
    password_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "form3-password"))
    )
    
    for char in password:
        password_element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))
    
    # password_element.send_keys(password)
    password_element.send_keys(Keys.ENTER)
    # sign_in_button = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.XPATH, "//a[@class='signin button button-empty']"))
    #     )
    # sign_in_button.click()

def validate_date(date_string):
    if date_string == "":
        return True
    try:
        datetime.datetime.strptime(date_string, '%B %d, %Y')
        return True
    except ValueError:
        return False

def validate_time(hour, minute, period):
    if not (1 <= int(hour) <= 12):
        return False
    if not (0 <= int(minute) <= 59):
        return False
    if period not in ["AM", "PM"]:
        return False
    return True

def get_date_input():
    desired_date = input("Enter the desired date (e.g., 'April 20, 2023', default Wednesday): ")
    while not validate_date(desired_date):
        print("Invalid date format. Please enter again.")
        desired_date = input("Enter the desired date (e.g., 'April 20, 2023'): ")
    return desired_date

def get_time_input():
    desired_hour = input("Enter the desired hour (1-12 format): ")
    desired_minute = input("Enter the desired minute (00-59 format): ")
    desired_period = input("Enter the period (AM/PM): ").upper()
    while not validate_time(desired_hour, desired_minute, desired_period):
        print("Invalid time input. Please enter again.")
        desired_hour = input("Enter the desired hour (1-12 format): ")
        desired_minute = input("Enter the desired minute (00-59 format): ")
        desired_period = input("Enter the period (AM/PM): ").upper()
    return desired_hour, desired_minute, desired_period

def set_date(desired_date, desired_hour, desired_minute, desired_period):
    custom_start_date = driver.find_element(By.CLASS_NAME, "form-control.flatpickr.form-control.input")
    custom_start_date.click()

    # Locate the date picker element
    date_picker = driver.find_element(By.CLASS_NAME, "flatpickr-calendar")

    # Use the desired_date variable to find the specific date element
    specific_date_element = date_picker.find_element(By.CSS_SELECTOR, f".flatpickr-day[aria-label='{desired_date}']")
    specific_date_element.click()

    # Set the desired hour
    hour_input = driver.find_element(By.CLASS_NAME, "numInput.flatpickr-hour")
    hour_input.clear()
    hour_input.send_keys(desired_hour)

    # Set the desired minute
    minute_input = driver.find_element(By.CLASS_NAME, "numInput.flatpickr-minute")
    minute_input.clear()
    minute_input.send_keys(desired_minute)

    # Set AM or PM
    am_pm_input = driver.find_element(By.CLASS_NAME, "flatpickr-am-pm")

    # If the current state of the AM/PM toggle doesn't match the desired period, click to change it.
    if am_pm_input.text != desired_period:
        am_pm_input.click()

def create_arena(arena_name, description_title, entry_code, start_date, start_hour, start_minute, start_period, rated=False):    
    driver.get('https://lichess.org/tournament/new')
    
    # set arena name
    input_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "form3-name"))
        )
    input_element.clear()
    input_element.send_keys(arena_name)

    # set arena description
    description_element = driver.find_element(By.ID, "form3-description")
    description_element.click()
    description_element.send_keys(description_title)

    # set arena to rated
    if(rated == False):
        rated_element = driver.find_element(By.CSS_SELECTOR, 'label[for="form3-rated"]')
        rated_element.click()
    
    # set additional arena options
    advanced_options_element = driver.find_element(By.CLASS_NAME, "show")
    advanced_options_element.click()

    # set arena entry code
    entry_code_element = driver.find_element(By.ID, "form3-password")
    entry_code_element.click()
    entry_code_element.send_keys(entry_code)

    # set arena start date
    set_date(start_date, start_hour, start_minute, start_period)

    # Find the "Create a new tournament" button by its attributes
    create_tournament_button = driver.find_element(By.XPATH, "//button[@data-icon='' and @class='submit button text']")

    # Click the button
    create_tournament_button.click()

def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}

def main():
    config = load_config()
    # Try to get values from the config, and if not found, prompt the user
    arena_name = config.get("arena_name") or input("Enter the arena name: ")
    description_title = config.get("description_title") or input("Enter the arena description: ")
    rated = config.get("rated", None)
    if rated is None:
        rated_response = input("Should the arena be rated? (yes/no): ").lower()
        rated = rated_response == 'yes'
    entry_code = config.get("entry_code") or input("Enter an entry code for the arena: ")
    
    # Similarly for date and time, with the addition of validation functions
    start_date = config.get("start_date") or get_date_input()
    print(start_date)
    if (not start_date or start_date == ""):
        today = datetime.datetime.today()
        days_until_next_wednesday = (2 - today.weekday()) % 7  # Calculate the days until next Wednesday (2 corresponds to Wednesday)
        next_wednesday = today + datetime.timedelta(days=days_until_next_wednesday)
        start_date = next_wednesday.strftime("%B %d, %Y") 
    print(start_date)
    
    start_hour = config.get("start_hour")
    start_minute = config.get("start_minute")
    start_period = config.get("start_period")


    if not start_hour or not start_minute or not start_period:
        start_hour, start_minute, start_period = get_time_input()
    
    driver.get('https://lichess.org/')

    # Login
    login()
    time.sleep(10)

    # Create Arena
    # create_arena(arena_name, description_title, entry_code, start_date, start_hour, start_minute, start_period, rated)
    arena_url = driver.current_url

if __name__ == "__main__":
    main()
