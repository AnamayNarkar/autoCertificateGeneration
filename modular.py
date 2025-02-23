import os
import csv
import time
import pathlib
import dotenv as env
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

class constants:
    def __init__(self,email, password, linkToCanvaCertificate, csvFile, elementsToBeFilled):
        self.loginPage = "https://canva.com/en_in/login"
        self.email = email
        self.password = password
        self.linkToCanvaCertificate = linkToCanvaCertificate
        self.csvFile = csvFile
        self.absolute_path = pathlib.Path(csvFile).resolve()
        self.elementsToBeFilled = elementsToBeFilled

def set_up_constants():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    linkToCanvaCertificate = os.getenv("LINK_TO_CANVA_CERTIFICATE")
    csvFile = os.getenv("CSV_FILE")
    elementsToBeFilled = {
        "==Name==": "name",
    }
    return constants(email, password, linkToCanvaCertificate, csvFile, elementsToBeFilled)

def set_up_driver():
    # Set the download directory to the current working directory
    download_dir = str(os.getcwd())  

    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")

    # Initialize undetected ChromeDriver with options
    driver = uc.Chrome(options=chrome_options)

    # Set download behavior using CDP
    params = {"behavior": "allow", "downloadPath": download_dir}
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

    return driver

def googleLogin(driver, constants):

    # Navigate to the Canva login page
    driver.get(constants.loginPage)
    time.sleep(10)  # Wait for the page and Cloudflare check

    # Click the "Continue with Google" button
    google_login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue with Google')]"))
    )
    print("Google login button found successfully.")
    google_login_button.click()
    print("Google login button clicked successfully.")

    # Wait for the new window (Google sign-in) to open
    WebDriverWait(driver, 20).until(lambda d: len(d.window_handles) > 1)
    original_window = driver.current_window_handle

    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            break
    print("Switched to Google sign-in window.")

    # Wait for the email input field and enter the email
    email_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
    )
    email_field.send_keys(constants.email)

    print("Entered email.")

    # Click the "Next" button after email entry
    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Next')]"))
    )
    next_button.click()
    print("Clicked Next after email.")

    time.sleep(5)

    # Wait for the password input field to load
    password_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.whsOnd.zHQkBf"))
    )
    password_field.send_keys(constants.password)
    print("Entered password.")

    # Click the "Next" button after password entry
    password_next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='passwordNext']"))
    )
    password_next_button.click()
    print("Clicked Next after password.")

    try:
        checkFor2FA = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '2-Step Verification')]"))
        )
        print("2FA detected. Please verify manually on your device.")
    except Exception as e:
        print("No 2FA prompt detected, proceeding...")

    # Wait for the success message element that indicates Google is ready to share data with Canva
    twoFAElements = WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(text(), 'By continuing, Google will share')]")
        )
    )
    if twoFAElements:
        allowButton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue')]"))
        )
        allowButton.click()
        print("Clicked Allow button to complete login.")
    else:
        print("2FA verification success elements not found, please check manually.")

    print("2FA verified successfully. Logged in!")

    driver.switch_to.window(original_window)
    print("Switched back to Canva.")

    # Navigate to the Canva certificate link
    driver.get(constants.linkToCanvaCertificate)
    print("Navigated to the Canva certificate link.")

    time.sleep(15)  # Wait for the certificate to load and Canva logins to be saved

def emailLogin(driver, constants):
    driver.get(constants.loginPage)
    time.sleep(5)

    # find the login with email button
    loginWithEmail = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue with email')]"))
    ).click()

    print ("Clicked on the login with email button")

    # find the email input field which has type text and name email
    emailField = WebDriverWait(driver, 20).until(   
        EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @name='email']"))
    ).send_keys(constants.email + Keys.ENTER)

    otp = input("Enter the OTP: ")

    # find an input with placehoder "Enter code"
    otpField = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter code']"))
    ).send_keys(otp + Keys.ENTER)

    time.sleep(10)

    driver.get(constants.linkToCanvaCertificate)

    return

def fill_and_download(driver, constants):
    time.sleep(15)  # Wait for the certificate to load and Canva logins to be saved

    # Click the "Apps" button to open the options table for bulk creation
    bulk_create_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Bulk create')]/preceding-sibling::span[1]"))
    )
    bulk_create_button.click()
    print("Clicked the SVG button above Bulk create.")

    # Click the Upload data button
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//span[contains(text(), 'Upload data')]/ancestor::button/preceding-sibling::input[@type='file']"
        ))
    )
    file_input.send_keys(str(constants.absolute_path))
    print("Uploaded the CSV file.")

    for canva_element, csv_element in constants.elementsToBeFilled.items():
        element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{canva_element}')]"))
        )
        actions = ActionChains(driver)
        actions.context_click(element).perform()
        print(f"Right clicked on the {canva_element} element using ActionChains.")

        connect_data = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Connect data')]"))
        )
        connect_data.click()

        csv_field_inside_dropdown = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//li//button//span//span[2]//span[normalize-space(text())='{csv_element}']")
            )
        )
        print(f"Found the {csv_element} element in the dropdown.")
        csv_field_inside_dropdown.click()
        print(f"Selected the {csv_element} element from the dropdown.")

    continue_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue')]/ancestor::button"))
    )
    continue_button.click()
    print("Clicked the Continue button.")

    with open(constants.csvFile, newline='') as f:
        number_of_rows_in_csv = sum(1 for row in csv.reader(f))
    number_of_rows_in_csv -= 1  # Exclude the header row

    print(f"Number of rows in the CSV file: {number_of_rows_in_csv}")
    designs_text = f"Generate {number_of_rows_in_csv} designs"
    print("The string we are going to search for is: " + designs_text)

    xpathExpression = f"//span[contains(text(), '{designs_text}')]/ancestor::button"
    Generate_designs_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, xpathExpression))
    )
    Generate_designs_button.click()
    print(f"Clicked the {designs_text} button.")

    time.sleep(15)  # Wait for the designs to be generated

    # Switch to the new window
    new_window = driver.window_handles[1]
    driver.switch_to.window(new_window)
    print("Switched to the new window.")

    # Manage download steps:
    # 1. Click on the share button
    share_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button//span[2][contains(text(), 'Share')]"))
    )
    share_button.click()
    print("Clicked the Share button.")

    # 2. Click the download button (located directly above the paragraph with a span containing 'Download')
    download_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//p[.//span[contains(text(),'Download')]]/preceding-sibling::button[1]"))
    )
    download_button.click()
    print("Clicked the Download button.")

    # 3. Click the PNG option to reveal the dropdown
    time.sleep(2)
    png_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'PNG')]"))
    ).click()

    # 4. Select the PDF Print option
    time.sleep(2)
    pdf_print_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'PDF Print')]"))
    ).click()
    print("Selected PDF Print option.")

    # 5. Finally, click on the Download PDF button
    time.sleep(5)
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Download')]/ancestor::button"))
    ).click()
    print("Initiated download.")

    time.sleep(60)  # Wait for the download to complete

def main():
    env.load_dotenv()
    constants = set_up_constants()
    driver = set_up_driver()
    # googleLogin(driver, constants)
    emailLogin(driver,constants)
    fill_and_download(driver, constants)
    driver.quit()

main()    