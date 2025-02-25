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
    def __init__(self, email, password, linkToCanvaCertificate, csvFile, elementsToBeFilled):
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
        "===Name===": "name",
    }
    return constants(email, password, linkToCanvaCertificate, csvFile, elementsToBeFilled)

def set_up_driver():
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")

    driver = uc.Chrome(options=chrome_options, headless=False)
    params = {"behavior": "allow", "downloadPath": download_dir}
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

    return driver, download_dir

def wait_for_download(download_dir, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(download_dir)
        if any(file.endswith(".crdownload") for file in files):
            print("File is still downloading...")
            time.sleep(2)
        elif any(file.endswith(".pdf") for file in files):
            print("File download complete.")
            return files
        else:
            time.sleep(2)
    raise Exception("Download timed out.")

def googleLogin(driver, constants):
    driver.get(constants.loginPage)
    time.sleep(10)

    google_login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue with Google')]"))
    )
    google_login_button.click()

    WebDriverWait(driver, 20).until(lambda d: len(d.window_handles) > 1)
    original_window = driver.current_window_handle

    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            break

    email_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
    )
    email_field.send_keys(constants.email)

    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Next')]"))
    )
    next_button.click()

    time.sleep(5)

    password_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.whsOnd.zHQkBf"))
    )
    password_field.send_keys(constants.password)

    password_next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='passwordNext']"))
    )
    password_next_button.click()

    try:
        checkFor2FA = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '2-Step Verification')]"))
        )
        print("2FA detected. Please verify manually on your device.")
    except Exception as e:
        print("No 2FA prompt detected, proceeding...")

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
    else:
        print("2FA verification success elements not found, please check manually.")

    driver.switch_to.window(original_window)
    driver.get(constants.linkToCanvaCertificate)

def emailLogin(driver, constants):
    driver.get(constants.loginPage)
    time.sleep(5)

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue with email')]"))
    ).click()

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @name='email']"))
    ).send_keys(constants.email + Keys.ENTER)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter code']"))
        )
    except Exception as e:
        print("OTP input field not found. login probably failed.")
        return

    otp = input("Enter the OTP: ")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter code']"))
    ).send_keys(otp + Keys.ENTER)

    time.sleep(10)
    driver.get(constants.linkToCanvaCertificate)
    return

def fill_and_download(driver, constants, download_dir):
    time.sleep(15)

    bulk_create_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Bulk create')]/preceding-sibling::span[1]"))
    )
    bulk_create_button.click()

    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//span[contains(text(), 'Upload data')]/ancestor::button/preceding-sibling::input[@type='file']"
        ))
    )
    file_input.send_keys(str(constants.absolute_path))

    for canva_element, csv_element in constants.elementsToBeFilled.items():
        element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{canva_element}')]"))
        )
        actions = ActionChains(driver)
        actions.context_click(element).perform()

        connect_data = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Connect data')]"))
        )
        connect_data.click()

        csv_field_inside_dropdown = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//li//button//span//span[2]//span[normalize-space(text())='{csv_element}']")
            )
        )
        csv_field_inside_dropdown.click()

    continue_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue')]/ancestor::button"))
    )
    continue_button.click()

    with open(constants.csvFile, newline='') as f:
        number_of_rows_in_csv = sum(1 for row in csv.reader(f))
    number_of_rows_in_csv -= 1

    designs_text = f"Generate {number_of_rows_in_csv} designs"

    xpathExpression = f"//span[contains(text(), '{designs_text}')]/ancestor::button"
    Generate_designs_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, xpathExpression))
    )
    Generate_designs_button.click()

    WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)

    new_window = driver.window_handles[1]
    driver.switch_to.window(new_window)

    share_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button//span[2][contains(text(), 'Share')]"))
    )
    share_button.click()

    download_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//p[.//span[contains(text(),'Download')]]/preceding-sibling::button[1]"))
    )
    download_button.click()

    time.sleep(2)
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'PNG')]"))
    ).click()

    time.sleep(2)
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'PDF Print')]"))
    ).click()

    time.sleep(5)
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Download')]/ancestor::button"))
    ).click()

    downloaded_files = wait_for_download(download_dir)
    if not downloaded_files:
        print("No files were downloaded.")
        return

    driver.quit()

def main():
    env.load_dotenv()
    constants_instance = set_up_constants()
    driver, download_dir = set_up_driver()
    emailLogin(driver, constants_instance)
    fill_and_download(driver, constants_instance, download_dir)

main()