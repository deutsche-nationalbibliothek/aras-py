from loguru import logger
from httpx import Client
from pathlib import Path

from aras_py.run import get_stream


def test_aras_get_stream(tmp_path):

    client = Client(base_url="http://localhost:8080/")

    repository = "example"
    idn = "123"

    target_path = tmp_path
    target_path = Path("/tmp/aras")
    #/access/repositories/example/artifacts/123


    for name, bytes_io in get_stream(client, repository, idn):
        with open(f"{target_path}/{idn}_{name}", mode='wb') as target:
            target.write(bytes_io.read())

    assert len(list(tmp_path.iterdir())) == 2
