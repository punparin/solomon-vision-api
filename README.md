# solomon-vision-api

is an API retrieving Yugioh card's name from image using OCR

## Usage

```sh
curl --request POST 'http://localhost:8080/search-card' \
--header 'Content-Type: image/jpeg' \
--data-binary <IMAGE_FILE>
```

```json
{
  "en_name": "Formula Synchron",
  "jp_name": "フォーミュラ・シンクロン",
  "set_code": "HC01-JP02"
}
```

## For development

### Setup development environment

```sh
virtualenv venv
# For fish
source venv/bin/activate.fish
# For shell
source venv/bin/activate
pip install -r requirements.txt
```

### Running on local

```sh
# Run on machine
gunicorn --bind 0.0.0.0:8080 --pythonpath src wsgi:app

# Run on docker
earthly +compose-up
earthly +compose-down
```

### Release

```sh
earthly --build-arg TAG=<TAG> --push +release
```
