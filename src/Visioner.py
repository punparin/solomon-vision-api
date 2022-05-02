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

    def find_fuzzy_cards_from_name(self, input_name):
        cards = []
        max_score = 0

        resp = self.es.search(
            index=self.index,
            query={
                    "match": {
                        "jp_name": input_name
                    }
                }
            )

        for card in resp['hits']['hits']:
            score = int(card["_score"])

            if score >= max_score:
                cards.append(card)
                max_score = score

        return cards

    def jaccard_similarity(self, text_1, text_2):
        intersection_cardinality = len(set.intersection(*[set(text_1), set(text_2)]))
        union_cardinality = len(set.union(*[set(text_1), set(text_2)]))

        return intersection_cardinality / float(union_cardinality)

    def find_texts_from_image(self, img):
        texts = []
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

        return texts

    def get_set_code(self, texts):
        for text in texts:
            isIdMatched = re.search("^[0-9]*[A-Z]+[0-9]*\-[A-Z]*[0-9]*$", text)
            if isIdMatched:
                return text

    def get_card_from_text(self, text, card, similarity_threshold):
        if card is not None:
            en_name = card["_source"]["name"]
            jp_name = card["_source"]["jp_name"]
            card_type = card["_source"]["type"]
            img_url = "https://storage.googleapis.com/ygoprodeck.com/pics_small/" + str(card["_source"]["id"]) + ".jpg"
            score = self.jaccard_similarity(text, card["_source"]["jp_name"])

            if score >= similarity_threshold:
                return CardInfo("", card_type, en_name, jp_name, img_url)

        return None

    def find_cards(self, img, similarity_threshold):
        cards = []

        texts = self.find_texts_from_image(img)
        set_code = self.get_set_code(texts)

        for text in texts:
            found = False
            possible_cards = self.find_fuzzy_cards_from_name(text)

            for card in possible_cards:
                card = self.get_card_from_text(text, card, similarity_threshold)

                if card is not None:
                    card_info = card
                    card_info.set_code = set_code
                    cards.append(card_info)

        return cards

    def find_card(self, img, similarity_threshold=None):
        card_info = CardInfo()
        
        texts = self.find_texts_from_image(img)
        card_info.set_code = self.get_set_code(texts)

        for text in texts:
            found = False
            possible_cards = self.find_fuzzy_cards_from_name(text)

            for card in possible_cards:
                card = self.get_card_from_text(text, card, self.score_threshold)

                if card is not None:
                    card_info = card
                    found = True
                    break

        return card_info
