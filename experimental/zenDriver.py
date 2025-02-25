import asyncio
import time
import os
import pathlib
import dotenv as env

import zendriver as zd
from zendriver import cdp

async def context_click_element(tab, element):
    result = await tab.send(cdp.dom.get_content_quads(node_id=element.node_id))
    if not result["quads"]:
        raise Exception("No quads returned for element.")
    quad = result["quads"][0]

    xs = quad[0::2]
    ys = quad[1::2]
    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)

    device_pixel_ratio = await tab.evaluate("window.devicePixelRatio")
    adjusted_x = center_x / device_pixel_ratio
    adjusted_y = center_y / device_pixel_ratio

    await tab.send(cdp.input.dispatch_mouse_event(
        type_="mousePressed",
        x=adjusted_x,
        y=adjusted_y,
        button="right",
        clickCount=1
    ))
    await asyncio.sleep(0.1)
    await tab.send(cdp.input.dispatch_mouse_event(
        type_="mouseReleased",
        x=adjusted_x,
        y=adjusted_y,
        button="right",
        clickCount=1
    ))



async def closeCollapseButton(tab):
        collapse_button = await tab.query_selector_all("button")
        for button in collapse_button:
            if button.attributes:
                for i in range (len(button.attributes)):
                    if button.attributes[i] == "aria-label" and button.attributes[i+1] == "Collapse":
                        collapse_button = button
                        break
        
        if not collapse_button:
            customLogger("Collapse button not found")
            raise Exception("Collapse button not found")
    
        await collapse_button.click()
        customLogger("Clicked the Collapse button")

async def clickBulkCreateButton(tab):
    bulk_create_button = None

    all_divs = await tab.query_selector_all("div")
    for div in all_divs:
        if div.attributes:
            for i in range (len(div.attributes)):
                if div.attributes[i] == "title" and div.attributes[i+1] == "Bulk create":
                    bulk_create_button = div
                    break

    if not bulk_create_button:
        customLogger("Bulk create button not found")
        raise Exception("Bulk create button not found")

    await bulk_create_button.click()
    customLogger("Clicked the Bulk create button")

async def wait_for_dom_ready(tab):
    """Waits for the DOMContentLoaded equivalent event."""
    await tab.send(cdp.page.set_lifecycle_events_enabled(enabled=True))
    await tab.wait_for_event("Page.domContentEventFired")
    print("DOM is fully loaded!")

def customLogger(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

class userDefinedConstants:
    def __init__(self, email, password, linkToCanvaCertificate, csvFile, elementsToBeFilled):
        self.email = email
        self.password = password
        self.linkToCanvaCertificate = linkToCanvaCertificate
        self.csvFile = csvFile
        self.absolute_path = pathlib.Path(csvFile).resolve()
        self.elementsToBeFilled = elementsToBeFilled

def setup_constants():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    linkToCanvaCertificate = os.getenv("LINK_TO_CANVA_CERTIFICATE")
    csvFile = "test.csv"
    elementsToBeFilled = {
        "===Name===": "name",
    }
    return userDefinedConstants(email, password, linkToCanvaCertificate, csvFile, elementsToBeFilled)

async def setup_driver():
    browser = await zd.Browser.create(headless=False)
    tab = await browser.get("https://canva.com/en_in/login")
    # await browser.grant_all_permissions()
    await tab.set_download_path(path = os.path.join(os.getcwd(), "downloads"))
    return browser, tab

async def loginUsingEmail(browser, tab, constants):
    await tab.wait_for_ready_state("complete")
    await tab.wait_for(selector = "span", text = "Continue with email", timeout = 10)
    customLogger("Found the login with email button")

    #this is an array of type <class 'zendriver.core.element.Element'>
    array_of_all_elements_with_span_tag = await tab.query_selector_all("span")
    for element in array_of_all_elements_with_span_tag:
        if element.text == "Continue with email":
            login_with_email_button = element
            break
    
    await login_with_email_button.click()
    customLogger("Clicked the login with email button")

    await tab.wait_for(selector = "input[type='text']", timeout = 10)
    customLogger("Found the email input field")

    all_input_fields = await tab.query_selector_all("input")
    for i in range (len(all_input_fields)):
        for j in range (len(all_input_fields[i].attributes)):
            if all_input_fields[i].attributes[j] == "name" and all_input_fields[i].attributes[j+1] == "email":
                email_input_field = all_input_fields[i]
                break
    
    await email_input_field.send_keys(text=constants.email)
    customLogger("Entered the email")

    await tab.wait_for(selector = "span", text = "Continue", timeout = 10)
    customLogger("Found the continue button")

    array_of_all_elements_with_span_tag = await tab.query_selector_all("span")
    for element in array_of_all_elements_with_span_tag:
        if element.text == "Continue":
            continue_button = element
            break
    
    await continue_button.click()
    customLogger("Clicked the continue button")

    await asyncio.sleep(10)

    await tab.wait_for(selector = "input", timeout = 10)
    customLogger("Found the password input field")

    all_input_fields = await tab.query_selector_all("input")
    for i in range (len(all_input_fields)):
        for j in range (len(all_input_fields[i].attributes)):
            if all_input_fields[i].attributes[j] == "placeholder" and all_input_fields[i].attributes[j+1] == "Enter code":
                otp_input_field = all_input_fields[i]
                break

    if not otp_input_field:
        customLogger("OTP input field not found. login probably failed.")
        raise Exception("OTP input field not found")

    # wait for user input
    otp = input("Enter the OTP and press enter : ")
    await otp_input_field.send_keys(text = str(otp))

    customLogger("Entered the OTP")

    await asyncio.sleep(10)
    print(tab.url)
    await tab.save_screenshot(filename = "./downloads/hopefullyhomepage.png", full_page = True, format = "png")

    if tab.url == "https://www.canva.com/":
        customLogger("Successfully logged in")
    else:
        customLogger("Login failed")
        raise Exception("Login failed")

async def changeTabUrlToCertificate(browser, tab, constants):
    await tab.get(constants.linkToCanvaCertificate)
    await asyncio.sleep(10)
    print (tab.url)
    print (constants.linkToCanvaCertificate)
    print (tab.url == constants.linkToCanvaCertificate)

    if tab.url == constants.linkToCanvaCertificate:
        customLogger("Navigated to the certificate page")
        await tab.save_screenshot(filename = "./downloads/certificatepage.png", full_page = True, format = "png")
    else:
        customLogger("Navigation failed")
        raise Exception("Navigation failed")

async def selectBulkCreateAndUploadCsvAndConnectData(browser, tab, constants):
    await  asyncio.sleep(5)
    await tab.wait_for(selector = "span", text = "Bulk create", timeout = 10)
    bulk_create_button = None

    all_divs = await tab.query_selector_all("div")
    for div in all_divs:
        if div.attributes:
            for i in range (len(div.attributes)):
                if div.attributes[i] == "title" and div.attributes[i+1] == "Bulk create":
                    bulk_create_button = div
                    break

    if not bulk_create_button:
        customLogger("Bulk create button not found")
        raise Exception("Bulk create button not found")

    await bulk_create_button.click()
    customLogger("Clicked the Bulk create button")

    await asyncio.sleep(5)
    await tab.wait_for(selector = "span", text = "Upload data", timeout = 10)

    file_input = None

    all_input_fields = await tab.query_selector_all("input")
    for input_field in all_input_fields:
        if input_field.attributes:
            for i in range (len(input_field.attributes)):
                if input_field.attributes[i] == "accept" and input_field.attributes[i+1] == "text/csv,text/tab-separated-values,.xlsx":
                    file_input = input_field
                    break
    
    if not file_input:
        customLogger("File input field not found")
        raise Exception("File input field not found")
    else:
        customLogger("Found the file input field")
    
    await file_input.send_file(constants.absolute_path)
    customLogger("Uploaded the CSV file")

    for canva_element, csv_element in constants.elementsToBeFilled.items():
        element = await tab.wait_for(selector = "span", text = "{canva_element}", timeout = 100)
        customLogger("Element found")
        await element.click()

        parent_div = element.parent
        parent_2_div = parent_div.parent if parent_div else None
        parent_3_div = parent_2_div.parent if parent_2_div else None
        parent_4_div = parent_3_div.parent if parent_3_div else None    

        # await tab.set_window_state(state="fullscreen")
        # asyncio.sleep(1)

        # position = await parent_4_div.get_position()

        # customLogger(position)

        # center = position.center

        # await asyncio.gather(tab.send(cdp.input_.dispatch_mouse_event(
        #     type_= "mousePressed",
        #     x=center[0],
        #     y=center[1],
        #     button=cdp.input_.MouseButton("left"),
        #     click_count=1
        # )))

        # await asyncio.sleep(0.1) 
        # await asyncio.gather(tab.send(cdp.input_.dispatch_mouse_event(
        #     type_="mouseReleased",
        #     x=center[0],
        #     y=center[1],
        #     button=cdp.input_.MouseButton("left"),
        #     buttons=0,
        #     click_count=1
        # )))
    
    # await centered_div.apply("""
    await element.apply("""
    (el) => {
        (function() {
            const target = Array.from(document.querySelectorAll('span')).find(el => el.innerText.trim() === "===Name===");
            if (target) {
                const pointerDown = new PointerEvent('pointerdown', {
                bubbles: true,
                cancelable: true,
                pointerType: 'mouse',
                button: 2
                });
                const pointerUp = new PointerEvent('pointerup', {
                bubbles: true,
                cancelable: true,
                pointerType: 'mouse',
                button: 2
                });
                const contextMenu = new PointerEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                pointerType: 'mouse',
                button: 2
                });
                target.dispatchEvent(pointerDown);
                target.dispatchEvent(pointerUp);
                target.dispatchEvent(contextMenu);
                console.log('Right-click pointer events dispatched.');
            } else {
                console.log('Target element not found.');
            }
        })();
    }
    """)

    # print (f"Right clicked on the {canva_element} element")

    await context_click_element(tab, element)
    customLogger(f"Right clicked on the {canva_element} element")

    #do a normal click

    # await element.apply("""
    #     (el) => {
    #         target = Array.from(document.querySelectorAll('span')).find(el => el.innerText.trim() === "===Name===");
    #         if (target) {
    #             target.click();
    #             console.log('Normal click dispatched.');
    #         } else {
    #             console.log('Target element not found.');
    #         }
    #     }
    # """)
        # await element.mouse_move(x = element_pos["x"] + 10, y = element_pos["y"] + 10)
        # await element.mouse_move()

        # asyncio.sleep(1)
        # await element.mouse_click(button = "right")
        # customLogger(f"Right clicked on the {canva_element} element")


async def main():
    env.load_dotenv()
    constants = setup_constants()
    browser, tab = await setup_driver()
    await loginUsingEmail(browser, tab, constants)
    await changeTabUrlToCertificate(browser, tab, constants)

    await selectBulkCreateAndUploadCsvAndConnectData(browser, tab, constants)
    await asyncio.sleep(200)
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())