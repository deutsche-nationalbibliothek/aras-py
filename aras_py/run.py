from loguru import logger
import click
from httpx import Client
import zipfile
import io
from .datastructures import xml_to_list

@click.group()
@click.option('--base', envvar='ARAS_REST_BASE')
@click.pass_context
def cli(ctx, base):
    ctx.ensure_object(dict)
    ctx.obj["client"] = Client(base_url=base)


@cli.command()
@click.pass_context
def repositories(ctx):
    """Access the ARAS interface via REST to list the available repositories."""
    with ctx.obj["client"] as client:
        r = client.get(f'/access/repositories')

    logger.debug(f"{r.request.url}")
    logger.debug(f"{xml_to_list(r.content)}")


@cli.command()
@click.option('--repository', envvar='ARAS_REPO', default="warc")
@click.option("target_path", '--path', default=".")
@click.argument('idn')
@click.pass_context
def get(ctx, repository, idn, target_path):
    """Access the ARAS interface via REST"""
    with ctx.obj["client"] as client:
        r = client.get(f'/access/repositories/{repository}/artifacts/{idn}')
        logger.debug(f"{r.headers["content-disposition"]}")
        logger.debug(f"{r.headers["content-type"]}")
        assert r.headers["content-type"] == "application/zip"
        z = zipfile.ZipFile(io.BytesIO(r.content))
        logger.debug(f"{z.namelist()}")
        assert len(z.namelist()) == 1
        z.extract(z.namelist()[0], path=target_path)


if __name__ == '__main__':
    cli(obj={})
