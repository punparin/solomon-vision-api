import json
from PIL import Image
from flask import Flask, request, Response
from Visioner import Visioner
from Logger import Logger
from SolomonVisionError import SolomonVisionError


app = Flask(__name__)

logger = Logger()
visioner = Visioner(logger)

@app.route('/search-card', methods=['POST'])
def cards():
    file = request.files['image']
    img_stream = Image.open(file.stream)

    try:
        name = visioner.find_name(img_stream)

        if name is None:
            response = Response(response=json.dumps({"message": "Name not found"}),
                        status=404,
                        mimetype="application/json"
                        )
        else:
            response = Response(response=json.dumps({"name": name}),
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
