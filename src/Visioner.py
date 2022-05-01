import re
import os
import requests
from google.cloud import vision
from elasticsearch import Elasticsearch, helpers
from SolomonVisionError import SolomonVisionError
from CardInfo import CardInfo


class Visioner:
    def __init__(self, logger):
        self.logger = logger
        self.index = "yugioh_cards"
        self.score_threshold = float(os.environ["SCORE_THRESHOLD"])
        self.es_endpoint = os.environ["ELASTICSEARCH_ENDPOINT"]
        self.vision_client = vision.ImageAnnotatorClient()
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

    def jaccard_similarity(self, text_1, text_2):
        intersection_cardinality = len(set.intersection(*[set(text_1), set(text_2)]))
        union_cardinality = len(set.union(*[set(text_1), set(text_2)]))

        return intersection_cardinality / float(union_cardinality)

    def find_name(self, img):
        texts = []
        card_info = CardInfo()
        img_stream = vision.Image(content=img)

        response = self.vision_client.text_detection(image=img_stream)
        document  = response.full_text_annotation

        if response.error.message:
            self.logger.error("Visioner.find_name", response.error.message)
            raise SolomonVisionError("Vision API could not process data")

        for page in document.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    text = ""
                    for word in paragraph.words:
                        for symbol in word.symbols:
                            text += symbol.text
                    texts.append(text[:-1])

        for text in texts:
            card = self.find_fuzzy_card_from_name(text)
            
            if card is not None:
                en_name = card["_source"]["name"]
                jp_name = card["_source"]["jp_name"]
                img_url = "https://storage.googleapis.com/ygoprodeck.com/pics_small/" + str(card["_source"]["id"]) + ".jpg"
                score = self.jaccard_similarity(text, card["_source"]["jp_name"])

                if score >= self.score_threshold:
                    card_info.en_name = en_name
                    card_info.jp_name = jp_name
                    card_info.img_url = img_url
                    break

        for text in texts:
            isIdMatched = re.search("^[0-9]*[A-Z]+[0-9]*\-[A-Z]*[0-9]*$", text)
            if isIdMatched:
                card_info.set_code = text
                break

        return card_info
