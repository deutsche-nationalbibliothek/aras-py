# Access the Repository via ARAS

This tool helps to retrieve artifacts from the DNB Repository via ARAS via its REST interface.

To test the interplay you can mock an ARAS REST API with [mockils](https://github.com/deutsche-nationalbibliothek/mockils).

This projects uses [poetry](https://python-poetry.org/).

## Installation

```
$ poetry install
```

## Run

List the available repositories

```
$ poetry run aras-py repositories
```

Get a WARC file

```
# To the current directory
$ poetry run aras-py get 1176522620
```

```
# To a specific path
$ poetry run aras-py get --path archive 1176522620
```
