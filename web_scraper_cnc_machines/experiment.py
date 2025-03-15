import asyncio
from playwright.async_api import async_playwright
from logger.logger import setup_logger
from row_scrapper_ex import product_data
import csv
# Initialize the logger
logger = setup_logger()

def dicts_to_csv(data, filename):
    # Dynamically extract fieldnames from all dictionaries in the data
    fieldnames = set()
    for entry in data:
        fieldnames.update(entry.keys())
    
    # Convert the set of fieldnames back to a list
    fieldnames = list(fieldnames)

    # Write to CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


async def run():
    data = []
    # Start the Playwright browser session asynchronously
    async with async_playwright() as p:
        # Launch the browser (headless mode is True by default)
        try:
            logger.info("Launching the browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return

        try:
            # Navigate to the target URL (CNC machine listings page)
            logger.info("Navigating to the URL...")
            await page.goto('https://cncmachines.com/cnc-mill/for-sale', timeout=60000)

            # Wait for the product listing cards to appear on the page
            logger.info("Waiting for product listings to load...")
            await page.wait_for_selector('div.listing-card-new-wrapper', timeout=60000)

            # List to store the scraped data
            

            # Track already visited URLs
            visited_urls = set()

            # Loop through each product card
            product_cards = await page.query_selector_all('div.listing-card-new-wrapper')

            for idx, card in enumerate(product_cards):
                logger.debug(f"Processing card {idx + 1} of {len(product_cards)}")

                try:
                    # Check for card link (assuming each card has a clickable link for details)
                    card_link_element = await card.query_selector('a')  # Assuming the product link is within an <a> tag
                    if card_link_element:
                        card_link = await card_link_element.get_attribute('href')

                        # Skip if this card's link has already been visited
                        if card_link in visited_urls:
                            logger.info(f"Skipping already scraped card {idx+1}...")
                            continue

                        # Add the link to the visited URLs set
                        visited_urls.add(card_link)
                        product_data_card = await product_data(card_link)
                        data.append(product_data_card)
                except Exception as e:
                    # If an error occurs while processing a specific card, log the error and continue to the next card
                    logger.error(f"Error occurred for card {idx + 1}: {e}")
                    continue

            # Close the browser after the scraping process is complete
            await browser.close()

            # Output the scraped data to the console for review
            logger.info(f"Scraping completed. Scraped data: {data}")

        except Exception as e:
            # Catch any errors that occur during the initial page navigation or setup
            logger.error(f"An error occurred while navigating to the page: {e}")
    
    dicts_to_csv(data, "data.csv")

# Run the script
if __name__ == "__main__":
    try:
        # Initiate the asynchronous run function
        asyncio.run(run())
        
    except Exception as e:
        logger.error(f"Error running the script: {e}")
