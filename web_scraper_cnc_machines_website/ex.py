import asyncio
from playwright.async_api import async_playwright
from logger_mod.logger import setup_logger
from helper import extract_cnc_data_from_url
# init logger
logger = setup_logger()

async def run():
    async with async_playwright() as p:

        try:
            url = 'https://cncmachines.com/fadal-vmc4525-2024/l/12246'
            #logger.info("Navigating to the URL...")
            #await page.goto(url , timeout=60000)
            #wait page.wait_for_selector('div.listing-detail-container.not-lot')
            #html = await page.query_selector('div.listing-detail-container.not-lot')
            #html = await html.inner_html() if html else 'N/A'
            data = await extract_cnc_data_from_url(url)
            print(data)
        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            return 
        
if __name__ == "__main__":
    try:
        # Initiate the asynchronous run function
        asyncio.run(run())
        
    except Exception as e:
        logger.error(f"Error running the script: {e}")
