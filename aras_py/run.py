from loguru import logger
import click
from httpx import Client
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
    for name, bytes in get_bytes(ctx.obj["client"], repository, idn).items():
        open(f"{target_path}/{idn}_{name}", mode='wb').write(bytes)


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


if __name__ == "__main__":
    cli(obj={})
