# json_helper.py
import json
import os
from logger_mod.logger import setup_logger

logger = setup_logger()

def is_card_already_processed(card_name, filename="extracted_data.json"):
    """
    Checks if a card with the given name is already present in the JSON file.

    Args:
        card_name (str): The name of the card to check.
        filename (str, optional): The name of the JSON file. Defaults to "extracted_data.json".

    Returns:
        bool: True if the card is already processed, False otherwise.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    for item in existing_data:
                        if item.get("name") == card_name:
                            logger.info(f"Card '{card_name}' already processed.")
                            return True
                except json.JSONDecodeError:
                    logger.warning(f"JSON file '{filename}' is empty or invalid.")
                    return False
        else:
            logger.info(f"JSON file '{filename}' not found.")
            return False

        logger.info(f"Card '{card_name}' not found in processed data.")
        return False

    except Exception as e:
        logger.error(f"Error checking card existence: {e}")
        return False