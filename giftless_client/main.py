"""Command line entry point for Giftless-client

This is mainly for testing purposes

# TODO: add upload and download functionality
# TODO: add authentication support and pluggable authenticators
# TODO: can we make this compatible with the Git LFS binary?
"""
import logging

import click

from .client import LfsClient


@click.group()
@click.option('-u', '--server-url', type=str, required=True, help='Git LFS server URL')
@click.option('-b', '--bearer-token', type=str, required=False, help='Bearer token')
def main():
    pass


@main.command()
@click.argument('source_file', type=click.File(mode='rb'))
@click.argument('organization', type=str)
@click.argument('repository', type=str)
def upload(source_file, organization, repository, server_url, bearer_token=None):
    logging.basicConfig(format='%(asctime)-15s %(name)-24s %(levelname)-8s %(message)s',
                        level=logging.DEBUG)
    client = LfsClient(server_url, auth_token=bearer_token)
    client.upload(source_file, organization, repository)


if __name__ == '__main__':
    main()
