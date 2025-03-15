# scraper.py (or whatever you want to call this script)
import asyncio
from playwright.async_api import async_playwright
from sampler import clean_product_data
from logger.logger import setup_logger

# Initialize the logger
logger = setup_logger()

async def product_data(url):
    async with async_playwright() as p:
        try:
            logger.info("Launching the browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return
        product_data = {'url': url}

        try:
            logger.info("Navigating to the product page...")
            await page.goto(url, timeout=60000)
            await page.wait_for_selector('div.listing-detail-page-wrapper', timeout=60000)
            product_title = await page.query_selector('h1.listing-lot-header')
            product_title = await product_title.inner_text() if product_title else 'N/A'
            product_description = await page.query_selector('div.listing-details-description span')
            product_description = await product_description.inner_text() if product_description else 'N/A'
                        
            product_data['product_title'] = product_title
            product_data['url'] = url
            product_data['product_description'] = product_description

            logger.info("Waiting for the product rows to load...")
            await page.wait_for_selector('div.listing-info-and-specs-wrapper', timeout=60000)
        except Exception as e:
            logger.error(f"Error while navigating or waiting for page elements: {e}")
            await browser.close()
            return

        try:
            logger.info("Selecting divs inside the listing-info...")
            info_divs = await page.query_selector_all('div.listing-info-and-specs-wrapper div')
        except Exception as e:
            logger.error(f"Error selecting divs inside the listing-info: {e}")
            await browser.close()
            return

        
        # Loop through each 'info' div to find the rows and extract data
        for div_idx, div in enumerate(info_divs):
            try:
                logger.debug(f"Processing div {div_idx + 1}...")

                # Extract directly from the div if it's not a row or contains rows
                name_element = await div.query_selector('div.lot-description-header')
                content_element = await div.query_selector('div.lot-description-content')

                if name_element and content_element:
                    product_name = await name_element.inner_text()
                    product_content = await content_element.inner_text()

                    if product_name and product_content:
                        product_data[f'product_{product_name}'] = product_content
                        logger.debug(f"Product name: {product_name}, Content: {product_content}")
                    else:
                        logger.warning(f"Incomplete data in div {div_idx + 1}, skipping...")
                else:
                    # If there are no direct div elements, proceed with rows
                    rows = await div.query_selector_all('div.row')

                    if rows:
                        for row_idx, row in enumerate(rows):
                            try:
                                logger.debug(f"Row {row_idx + 1}: Extracting data...")

                                # Extract the product name from 'div.category-name'
                                name_element = await row.query_selector('div.col.category-name')
                                if name_element:
                                    product_name = await name_element.inner_text()
                                else:
                                    product_name = 'N/A'
                                    logger.warning(f"Product name not found for row {row_idx + 1} in div {div_idx + 1}")

                                # Skip if the product name is 'share' or 'buy_now'
                                if product_name.lower() in ['share', 'buy_now']:
                                    logger.info(f"Skipping product with name: {product_name}")
                                    continue

                                # Extract the link text from the 'a' tag inside 'div.category-content'
                                link_element = await row.query_selector('div.category-content')
                                if link_element:
                                    link_text = await link_element.inner_text()
                                else:
                                    link_text = 'N/A'
                                    logger.warning(f"Link not found for row {row_idx + 1} in div {div_idx + 1}")

                                if link_text == 'N/A' and product_name == 'N/A':
                                    continue

                                # Add the product data to the dictionary
                                product_data[f'product_{product_name}'] = link_text

                                logger.debug(f"Product name: {product_name}")
                                logger.debug(f"Link: {link_text}")

                            except Exception as e:
                                logger.error(f"Error extracting data from row {row_idx + 1} in div {div_idx + 1}: {e}")
                    else:
                        logger.warning(f"No rows found in div {div_idx + 1}")

            except Exception as e:
                logger.error(f"Error occurred while processing div {div_idx + 1}: {e}")

        # Clean the product data
        product_data = clean_product_data(product_data)

        try:
            await browser.close()
        except Exception as e:
            logger.error(f"Error while closing the browser: {e}")
            
        return product_data

