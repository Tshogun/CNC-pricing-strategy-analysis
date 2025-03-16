import asyncio
import json
import os  # Import the os module
from playwright.async_api import async_playwright
from logger_mod.logger import setup_logger
from helper import extract_cnc_data_from_url
from json_helper import is_card_already_processed

# init logger
logger = setup_logger()

# Data list to store product names and URLs
data = []

def save_data_to_json(data, filename="extracted_data.json"):
    """Saves the given data to a JSON file in the same directory as the script."""
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full file path
        file_path = os.path.join(script_dir, filename)

        if os.path.exists(file_path):
            with open(file_path, "r+", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = [] # if file is empty
                existing_data.extend(data)
                f.seek(0)
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
                f.truncate()
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")

async def parse_card_url(page, card):
    """User-defined function to parse and process card URL and name."""
    try:
        link = await card.query_selector('a.lot-box-link-wrapper')
        url = await link.get_attribute('href') if link else 'N/A'
        name_element = await card.query_selector('.product-name')  # Change this selector if needed
        name = await name_element.inner_text() if name_element else 'N/A'

        # Check if card is already processed
        if is_card_already_processed(name):
            return  # Skip processing if already processed

        card_data = await extract_cnc_data_from_url(url) # await here
        if card_data:
          data.append({'name': name, 'url': url, 'card_data': card_data[0] if card_data else {}}) #append card data
          save_data_to_json(data) #save data to json after adding new item
        logger.info(f"Extracted: {name} - {url}")
    except Exception as e:
        logger.error(f"Error processing card URL and name: {e}")
                
async def navigate_pages(page):
    """Function to handle pagination and process each page."""
    try:
        while True:
            logger.info("Processing current page...")
            await page.wait_for_selector('div.cnc-product-wrapper', timeout=60000)
            cards = await page.query_selector_all('div.listing-card-new-wrapper')
            for card in cards:
                await parse_card_url(page, card)

            next_button = await page.query_selector('li.ant-pagination-next a')  # Assuming the pagination button has this aria-label
            if next_button:
                logger.info("Clicking on 'Next' button to go to the next page...")
                await next_button.click()
                await page.wait_for_timeout(10000)
            else:
                logger.info("No 'Next' button found, reached last page.")
                break
    except Exception as e:
        logger.error(f"Error during pagination or card processing: {e}")

async def run():
    async with async_playwright() as p:
        # Launching Chromium browser
        try:
            logger.info("Launching the browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return

        # Navigating to the URL
        try:
            logger.info("Navigating to the URL...")
            await page.goto('https://cncmachines.com/cnc-mill/for-sale', timeout=60000)
            await navigate_pages(page)  # Process the pages with pagination
        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            return

# Run the script
if __name__ == "__main__":
    try:
        # Initiate the asynchronous run function
        asyncio.run(run())

    except Exception as e:
        logger.error(f"Error running the script: {e}")

    # Optionally, print out the final data list
    print("Extracted Data:")
    print(data)