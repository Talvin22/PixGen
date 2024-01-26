import requests
from aiogram.types import FSInputFile
import logging


class ImageParse:
    @staticmethod
    def url_to_img(image_url: str, filename: str = 'generated_img.png'):
        try:
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(filename, "wb") as file_img:
                    file_img.write(img_response.content)

                return FSInputFile(filename)
            else:
                logging.error("There was an error loading the image: HTTP Status Code %d", img_response.status_code)
                return None
        except Exception as e:
            logging.error("Error occurred: %s", str(e))
            return None
