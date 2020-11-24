"""Command line entry point for Giftless-client

This is mainly for testing purposes

# TODO: add authentication support and pluggable authenticators
# TODO: can we make this compatible with the Git LFS binary?
"""
import logging
from typing import BinaryIO

import click

from .client import LfsClient


@click.group()
@click.option('-u', '--server-url', type=str, required=True, help='Git LFS server URL')
@click.option('-b', '--bearer-token', type=str, required=False, help='Bearer token')
@click.option('-D', '--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def main(ctx, server_url, debug, bearer_token=None):
    logging.basicConfig(format='%(asctime)-15s %(name)-24s %(levelname)-8s %(message)s',
                        level=logging.DEBUG if debug else logging.INFO)
    ctx.obj = LfsClient(server_url, auth_token=bearer_token)


@main.command()
@click.argument('source_file', type=click.File(mode='rb'))
@click.argument('organization', type=str)
@click.argument('repository', type=str)
@click.pass_obj
def upload(client, source_file, organization, repository):
    client.upload(source_file, organization, repository)


@main.command()
@click.argument('organization', type=str)
@click.argument('repository', type=str)
@click.argument('object_sha', type=str)
@click.argument('expected_size', type=int)
@click.argument('output_file', type=click.File(mode='wb'))
@click.pass_obj
def download(client, organization, repository, object_sha, expected_size, output_file):
    # type: (LfsClient, str, str, str, int, BinaryIO) -> None
    client.download(output_file, object_sha, expected_size, organization, repository)


if __name__ == '__main__':
    main()
