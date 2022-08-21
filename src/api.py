import json
from PIL import Image
from flask import Flask, request, Response
from Visioner import Visioner
from Logger import Logger
from SolomonVisionError import SolomonVisionError
from CardInfo import CardInfo


app = Flask(__name__)

logger = Logger()
visioner = Visioner(logger)

@app.route('/search-card', methods=['POST'])
def card():
    img = request.data

    try:
        card_info = visioner.find_card(img)

        body = {
            "en_name": card_info.en_name,
            "jp_name": card_info.jp_name,
            "type": card_info.type,
            "set_code": card_info.set_code,
            "img_url": card_info.img_url
        }
        response = Response(response=json.dumps(body),
                    status=201,
                    mimetype="application/json"
                    )
    except SolomonVisionError as err:
        response = Response(response=json.dumps({"message": str(err)}),
                    status=400,
                    mimetype="application/json"
                    )

    return response

@app.route('/search-cards', methods=['POST'])
def cards():
    args = request.args
    similarity_threshold = float(args.get("similarity_threshold"))
    img = request.data

    try:
        card_infos = visioner.find_cards(img, similarity_threshold)

        body = []
        for card_info in card_infos:
            body.append({
                "en_name": card_info.en_name,
                "jp_name": card_info.jp_name,
                "type": card_info.type,
                "set_code": card_info.set_code,
                "img_url": card_info.img_url
            })
        response = Response(response=json.dumps(body),
                    status=201,
                    mimetype="application/json"
                    )
    except SolomonVisionError as err:
        response = Response(response=json.dumps({"message": str(err)}),
                    status=400,
                    mimetype="application/json"
                    )

    return response

@app.route('/health', methods=['GET'])
def health():
    return Response(response="OK", status=200)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
