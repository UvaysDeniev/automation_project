from __future__ import annotations

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from . import config

def get_driver():
    """
    Create a Chrome WebDriver, log into the portal, and return
    the authenticated driver instance.
    """
    chrome_opts = Options()
    chrome_opts.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_opts,
    )
    wait = WebDriverWait(driver, 10)

    print("🔐 Logging in...")
    driver.get(config.LOGIN_URL)
    time.sleep(2)

    # If the login is inside an iframe, switch into it
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    if frames:
        driver.switch_to.frame(frames[0])

    # Username / password fields + login button
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
    ).send_keys(config.USERNAME)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    ).send_keys(config.PASSWORD)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Log In')]"))
    ).click()

    time.sleep(2)
    return driver


def go_home(driver) -> None:
    """Collapse the menu and return to the home screen."""
    btn = driver.find_element(
        By.CSS_SELECTOR,
        'button.navbar-toggle[data-target="#menuBar"]'
    )
    btn.click()
    time.sleep(1)
    

    try:
        # Example:
        # btn = driver.find_element(By.XPATH, "//a[contains(@title, 'Collapse')]")
        # btn.click()
        # time.sleep(1)
        # driver.find_element(By.LINK_TEXT, "Home").click()
        pass
    except Exception:
        #
        pass
