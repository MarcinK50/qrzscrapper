# qrzscrapper
qrz.com scrapper with REST API
This app scraps [qrz.com](https://qrz.com) page
# How to configure
Due to restriction of max 100 requests on qrz.com, you will need to create some multiaccounts. Every multiaccount = 100 views.
Copy `config.example.json` into `config.json` and enter your passes.
e.g
```json
[
    ["user1", "p@ssw0rd"],
    ["user2", "p@ssw0rd"],
    ["user3", "p@ssw0rd"],
    ["user4", "p@ssw0rd"],
    ["user5", "p@ssw0rd"]
]
```
# How to start
Create venv and download required libs using pip
```sh
python3 -m venv .venv
pip install BeautifulSoup4 requests Flask
```
Start API with
```sh
flask --app main.py run
```
You should now have an API running on http://127.0.0.1:5000
# How to use this
Currently, there is only one endpoint `/get_data?call=N0NAME`
It takes ham radio callsign as a parameter and gives info in JSON format

This code for now need some refactors, but it should work. Feel free to create a PR to improve this.

73! de SP6FU
