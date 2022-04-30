import os
import easyocr
import requests
from elasticsearch import Elasticsearch, helpers
from SolomonVisionError import SolomonVisionError


class Visioner:
    def __init__(self, logger):
        self.logger = logger
        self.index = "yugioh_cards"
        self.es_endpoint = os.environ["ELASTICSEARCH_ENDPOINT"]
        self.reader = easyocr.Reader(['ja','en'])
        self.es = Elasticsearch(self.es_endpoint)

    def find_fuzzy_card_from_name(self, input_name):
        resp = self.es.search(
            index=self.index,
            query={
                    "match": {
                        "jp_name": input_name
                    }
                }
            )

        cards = resp['hits']['hits']

        return None if len(cards) == 0 else cards[0]

    def find_name(self, img_stream):
        try:
            items = self.reader.readtext(img_stream)
        except ValueError as err:
            self.logger.error("Visioner.find_name", err)
            raise SolomonVisionError("easyOCR could not retrieve value due to invalid input type")

        for item in items:
            text = item[1]

            card = self.find_fuzzy_card_from_name(text)
            
            if card is not None:
                return card["_source"]["name"]

        return None
