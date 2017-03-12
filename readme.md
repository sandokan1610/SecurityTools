# Security Tools
Tools for testing system vulnerability.
### Run
Install requirements:
```sh
$ pip install -r requirements.txt
```
Install gecko driver:

Download and unpack: https://github.com/mozilla/geckodriver/releases

Then run from directory:
```sh
$ sudo mv geckodriver /usr/bin
```
Create credentials.json from credentials_default.json with your data

Run from app root folder:
```sh
$ sudo python controller.py
```