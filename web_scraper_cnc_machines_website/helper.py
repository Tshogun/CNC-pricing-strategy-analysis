import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re
from logger_mod.logger import setup_logger #make sure to adjust this import
# init logger
logger = setup_logger()

async def extract_cnc_data_from_url(url):
    """Asynchronously extracts CNC machine data from a URL using Playwright and BeautifulSoup."""

    data = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            try:
                logger.info(f"Navigating to {url}")
                await page.goto(url)
                await page.wait_for_selector('.detail-grid')
            except Exception as nav_e:
                logger.error(f"Error navigating to {url}: {nav_e}")
                return []

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            product = {}

            # Product Description (including "Read More")
            try:
                description_element = await page.query_selector('.description-copy')
                if description_element:
                    read_more_span = await page.query_selector('.read-more-dots')
                    if read_more_span:
                        await read_more_span.click()
                        await page.wait_for_selector('.description-copy')
                        description_element = await page.query_selector('.description-copy')
                        product['description'] = await description_element.inner_text()
                    else:
                        product['description'] = await description_element.inner_text()
                else:
                    product['description'] = None
            except Exception as desc_e:
                logger.error(f"Error extracting description: {desc_e}")
                product['description'] = None

            # Basic Info (Cleaned Up)
            product['basic_info'] = {}
            try:
                basic_info_rows = soup.select('.brand-model-cat-links-in-main-desc.lot-main-desc .row')
                for row in basic_info_rows:
                    category_name = row.select_one('.category-name').text.strip().replace(':', '').lower()
                    category_content = row.select_one('.category-content').text.strip()
                    if category_name not in ['share', '']:  # Remove share and buy now
                        product['basic_info'][category_name] = category_content
            except Exception as basic_e:
                logger.error(f"Error extracting basic info: {basic_e}")

           # Technical Specifications (Regex Parsing)
            product['technical_specifications'] = {}
            try:
                spec_rows_element = soup.select_one('div.lot-description-wrapper div.lot-description-content')
                if spec_rows_element:
                    text_content = spec_rows_element.get_text(strip=True)
                    if text_content:
                        # Use regex to find key-value pairs
                        matches = re.findall(r'([A-Za-z\s]+):\s*([^A-Za-z\s][^A-Za-z\s:]*)', text_content)
                        for key, value in matches:
                            product['technical_specifications'][key.strip().lower().replace(' ', '_')] = value.strip()
            except Exception as spec_e:
                logger.error(f"Error extracting technical specs: {spec_e}")
            
            # Price and Payment
            try:
                price_element = soup.select_one('.lot-details-buy-now-button')
                product['price'] = price_element.text.strip() if price_element else None
                payment_element = soup.select_one('.financing-monthly-payment span:first-child')
                product['payment'] = payment_element.text.strip() if payment_element else None
            except Exception as price_e:
                logger.error(f"Error extracting price/payment: {price_e}")

            data.append(product)
            await browser.close()

    except Exception as e:
        print(f"Error extracting data: {e}")

    return data