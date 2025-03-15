# data_cleaner.py
import re
from logger.logger import setup_logger

# Initialize the logger
logger = setup_logger()

def clean_product_data(product_data):
    logger.debug("Original product data: %s", product_data)  # Log the original data

    cleaned_data = {}

    # Remove unwanted fields (product_Share, product_)
    unwanted_fields = ['product_Share:', 'product_']  # List the exact unwanted fields
    for key in list(product_data.keys()):
        if key in unwanted_fields:
            logger.info(f"Removing field: {key}")  # Log the field being removed
            del product_data[key]
    
    #logger.debug("Product data after removal of unwanted fields: %s", product_data)

    # Add non-spec fields (product_Brand, product_Model, etc.) to cleaned_data at the front
    for key, value in product_data.items():
        if key != 'product_Specs:':  # Avoid adding product_Specs again
            new_key = key.replace('product_', '').lower()  # Remove 'product_' prefix and convert to lowercase
            logger.debug(f"Adding field: {new_key} = {value}")  # Log the field being added
            cleaned_data[new_key] = value
    
    #logger.debug("Cleaned data after adding non-spec fields: %s", cleaned_data)

    # Flatten product specs into individual key-value pairs
    if 'product_Specs:' in product_data:
        specs = product_data['product_Specs:']
        logger.debug("Parsing specs: %s", specs)  # Log raw specs string
        specs_lines = specs.split('\n')

        for line in specs_lines:
            logger.debug(f"Processing line: {line}")  # Log the current line being processed
            match = re.match(r'([A-Za-z\s]+):\s*(.*)', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                if key and value:  # Avoid adding empty keys/values
                    logger.debug(f"Found spec: {key} = {value}")  # Log the key-value pair
                    cleaned_data[key] = value

    #logger.debug("Final cleaned data: %s", cleaned_data)

    return cleaned_data

