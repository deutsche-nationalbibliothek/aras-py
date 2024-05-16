# Access the Repository via ARAS

This tool helps to retrieve artifacts from the DNB Repository via ARAS.

See:
- http://etc.dnb.de/aras/
- https://wiki.dnb.de/display/FACHBEREICHIT/Version+2.x

There is a SOAP interface but the WSDL does not work, so we do it with REST.

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
