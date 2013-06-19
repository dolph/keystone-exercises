# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import sys

import pkg_resources


__version__ = pkg_resources.require('keystone-workout')[0].version
PROJECT_NAME = pkg_resources.require('keystone-workout')[0].project_name


def cli():
    parser = argparse.ArgumentParser(
        prog=PROJECT_NAME,
        description='Exercise keystone using python-keystoneclient')
    parser.add_argument(
        '--os-token', default='ADMIN')
    parser.add_argument(
        '--os-endpoint', default='http://localhost:35357/v3')
    parser.add_argument(
        '--default-domain-id', default='default')
    parser.add_argument(
        '--version', action='store_true',
        help='Show version number and exit')

    subparsers = parser.add_subparsers(title='subcommands')

    for attr in dir(subcommands):
        ref = getattr(subcommands, attr)
        # find classes extending of SubCommand
        if (type(ref) is type
                and ref != subcommands.SubCommand
                and issubclass(ref, subcommands.SubCommand)):
            subparser = subparsers.add_parser(ref.command)
            ref.configure_parser(subparser)
            subparser.set_defaults(func=ref())

    args = parser.parse_args()

    if args.version:
        print pkg_resources.require(PROJECT_NAME)[0]
        sys.exit()

    args.func(args)


if __name__ == '__main__':
    cli()
