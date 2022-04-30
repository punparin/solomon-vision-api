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
def cards():
    img = request.data

    try:
        card_info = visioner.find_name(img)

        body = {
            "en_name": card_info.en_name,
            "jp_name": card_info.jp_name,
            "set_code": card_info.set_code
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

if __name__ == '__main__':
    app.run(host="0.0.0.0")
