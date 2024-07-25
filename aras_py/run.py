from loguru import logger
import click
from httpx import Client
from stream_unzip import stream_unzip
from to_file_like_obj import to_file_like_obj
import zipfile
import io
from .datastructures import xml_to_list


@click.group()
@click.option("--base", envvar="ARAS_REST_BASE")
@click.pass_context
def cli(ctx, base):
    ctx.ensure_object(dict)
    ctx.obj["client"] = Client(base_url=base)


@cli.command()
@click.pass_context
def repositories(ctx):
    """Access the ARAS interface via REST to list the available repositories."""
    with ctx.obj["client"] as client:
        r = client.get("/access/repositories")

    logger.debug(f"{r.request.url}")
    print(f"{xml_to_list(r.content)}")


@cli.command()
@click.option("--repository", envvar="ARAS_REPO", default="warc")
@click.option("target_path", "--path", default=".")
@click.argument("idn")
@click.pass_context
def get(ctx, repository, idn, target_path):
    """Access the ARAS interface via REST and write it to the filesystem."""
    for name, bytes_io in get_stream(ctx.obj["client"], repository, idn).items():
        with open(f"{target_path}/{idn}_{name}", mode='wb') as target:
            with bytes_io as bytes:
                target.write(bytes.read())


def get_bytes(client, repository, idn):
    """Access the ARAS interface via REST.
    Get the WARC files of an IDN as bytes."""
    with client as connection:
        r = connection.get(f"/access/repositories/{repository}/artifacts/{idn}")
        logger.debug(f"{r.headers["content-disposition"]}")
        logger.debug(f"{r.headers["content-type"]}")
        assert r.headers["content-type"] == "application/zip"
        z = zipfile.ZipFile(io.BytesIO(r.content))
        logger.debug(f"{z.namelist()}")
        logger.debug(f"{z.infolist()}")
        return {member.filename: z.read(member) for member in z.infolist()}


def get_stream(client, repository, idn):
    """Access the ARAS interface via REST.
    Get the WARC files of an IDN as file-like-object."""
    with client as connection:
        with connection.stream("GET", f"/access/repositories/{repository}/artifacts/{idn}") as r:
            if "content-disposition" in r.headers:
                logger.debug(f"{r.headers["content-disposition"]}")
            logger.debug(f"{r.headers["content-type"]}")
            # assert r.headers["content-type"] == "application/zip"

            for file_name, file_size, unzipped_chunks in stream_unzip(r.iter_bytes()):
                yield file_name.decode("utf-8"), to_file_like_obj(unzipped_chunks)

if __name__ == "__main__":
    cli(obj={})
