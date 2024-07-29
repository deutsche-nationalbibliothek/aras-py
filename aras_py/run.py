from loguru import logger
import click
from httpx import Client
from to_file_like_obj import to_file_like_obj
import io
from rich.progress import Progress
from .datastructures import xml_to_list
import xml.etree.ElementTree as ET
from contextlib import contextmanager

ns = {'mets': 'http://www.loc.gov/METS/', "xlink": "http://www.w3.org/1999/xlink"}

@click.group()
@click.option("--base", envvar="ARAS_REST_BASE")
@click.pass_context
def cli(ctx, base):
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base


@cli.command()
@click.pass_context
def repositories(ctx):
    """Access the ARAS interface via REST to list the available repositories."""
    with Client(base_url=ctx.obj["base_url"]) as client:
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
    for name, bytes_io, metadata in get_stream(ctx.obj["base_url"], repository, idn):
        with open(f"{target_path}/{idn}_{name}", mode='wb') as target, bytes_io() as bytes:
            logger.info(f"Prepare file write with size: {metadata["size"]}")
            with Progress() as progress:
                task = progress.add_task(f"[blue]Downloading {name}...", total=metadata["size"])
                while True:
                    chunk = bytes.read(io.DEFAULT_BUFFER_SIZE)
                    if chunk:
                        target.write(chunk)
                        progress.update(task, advance=io.DEFAULT_BUFFER_SIZE)
                    else:
                        break


def get_stream(base_url, repository, idn):
    """Access the ARAS interface via REST.
    Get the WARC files of an IDN as file-like-object."""
    with Client(base_url=base_url) as connection:
        r = connection.get(f"/access/repositories/{repository}/artifacts/{idn}/objects")
        logger.debug(f"content: {r.content}")
        tree = ET.fromstring(r.content)
        logger.debug(f"tree: {tree}")
        files = tree.findall("./mets:fileSec/mets:fileGrp/mets:file", ns)
        logger.debug(f"files: {files}")
        for file in files:
            logger.debug(f"file: {file}")
            id = file.attrib["ID"]
            size = int(file.attrib["SIZE"])
            file_name = file.find("./mets:FLocat[@LOCTYPE='URL']", ns).get(f"{{{ns["xlink"]}}}href")
            logger.debug(f"file_name: {file_name}")

            @contextmanager
            def stream_lambda():
                logger.debug(f"base_url: {base_url}")
                with Client(base_url=base_url) as new_connection:
                    with new_connection.stream("GET", f"/access/repositories/{repository}/artifacts/{idn}/objects/{id}") as r:
                        logger.debug(f"r: {r.url}")
                        yield to_file_like_obj(r.iter_bytes())
            yield file_name, stream_lambda, {"size": size}

if __name__ == "__main__":
    cli(obj={})
