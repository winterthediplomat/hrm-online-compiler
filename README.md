hrm-online-compiler
===================

This is a very basic REST interface to compile programs as they're compiled by 
[hrm-compiler](https://github.com/alfateam123/hrm-compiler).

## Install

```bash
git clone https://github.com/alfateam123/hrm-online-compiler
cd hrm-online-compiler
virtualenv .hrm-online-compiler
source ./.hrm-online-compiler/bin/activate
pip install -r requirements.txt
```

## Run

```bash
source ./.hrm-online-compiler/bin/activate

FLASK_APP=main.py flask run
```

## Usage
```bash
curl 'http://127.0.0.1:5000/build' \
    -H 'Accept: */*' \
    --compressed \
    -H 'Content-type: application/x-www-form-urlencoded' \
    -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' \
    --data '{"code":"inbox\noutbox"}'
    
# => {"code": [{"operation": "inbox"}, {"operation": "outbox"}]}
#     as a string
```