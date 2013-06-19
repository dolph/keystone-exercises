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

import uuid

import keystoneclient
from keystoneclient.v3 import client

from keystoneworkout import benchmark


ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'secrete'
ADMIN_PROJECT_NAME = 'admin'
ADMIN_ROLE_NAME = 'admin'


def uid():
    return uuid.uuid4().hex[:6]


class SubCommand(object):
    command = None

    @classmethod
    def configure_parser(cls, parser):
        pass


class AdminCommand(object):
    def get_admin_client(self, args):
        """Authenticates as admin using the "long" auth flow."""
        c = client.Client(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            auth_url=args.os_endpoint)
        c.management_url = args.os_endpoint  # FIXME

        # find a project that we have access to
        project = c.projects.list(user=c.auth_ref.user_id).pop()

        return client.Client(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            project_id=project.id,
            auth_url=args.os_endpoint)


class BootstrapAdmin(SubCommand):
    """Bootstraps an admin user using a pre-existing token & endpoint.

    For the purpose of bootstrapping, the token is assumed to be
    keystone.conf's admin_token, and the endpoint is assumed to refer to the v3
    API.

    """
    command = 'bootstrap-admin'

    def _get_by_name(self, manager, name):
        collection = manager.list(name=name)
        collection_by_name = dict((x.name, x) for x in collection)
        return collection_by_name[name]

    def __call__(self, args):
        c = client.Client(
            token=args.os_token,
            endpoint=args.os_endpoint)

        try:
            user = c.users.create(
                name=ADMIN_USERNAME,
                domain=args.default_domain_id,
                password=ADMIN_PASSWORD)
        except keystoneclient.exceptions.Conflict:
            user = self._get_by_name(c.users, ADMIN_USERNAME)
        else:
            print 'Created user', user.name

        try:
            project = c.projects.create(
                name=ADMIN_PROJECT_NAME,
                domain=args.default_domain_id)
        except keystoneclient.exceptions.Conflict:
            project = self._get_by_name(c.projects, ADMIN_PROJECT_NAME)
        else:
            print 'Created project', project.name

        try:
            role = c.roles.create(
                name=ADMIN_ROLE_NAME)
        except keystoneclient.exceptions.Conflict:
            role = self._get_by_name(c.roles, ADMIN_ROLE_NAME)
        else:
            print 'Created role', role.name

        try:
            c.roles.check(
                user=user,
                project=project,
                role=role)
        except keystoneclient.exceptions.NotFound:
            c.roles.grant(
                user=user,
                project=project,
                role=role)
            print 'Assigned role', role.name,
            print 'to user', user.name,
            print 'on project', project.name

        # try to authenticate as our new admin user
        c = client.Client(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            project_name=ADMIN_PROJECT_NAME,
            auth_url=args.os_endpoint)


class BootstrapCatalog(SubCommand, AdminCommand):
    command = 'bootstrap-catalog'

    def __call__(self, args):
        c = client.Client(
            token=args.os_token,
            endpoint=args.os_endpoint)

        services_by_type = dict((x.type, x) for x in c.services.list())

        if 'identity' in services_by_type:
            identity = services_by_type['identity']
        else:
            identity = c.services.create(
                name='keystone',
                type='identity')

        identity_endpoints_by_interface = dict(
            (x.interface, x) for x in c.endpoints.list()
            if x.service_id == identity.id)

        if 'admin' not in identity_endpoints_by_interface:
            c.endpoints.create(
                service=identity,
                interface='admin',
                url=args.os_endpoint)

        if 'internal' not in identity_endpoints_by_interface:
            c.endpoints.create(
                service=identity,
                interface='internal',
                url=args.os_endpoint)

        if 'public' not in identity_endpoints_by_interface:
            c.endpoints.create(
                service=identity,
                interface='public',
                url=args.os_endpoint)


class BenchmarkAuth(SubCommand, AdminCommand):
    command = 'benchmark-auth'

    @classmethod
    def configure_parser(cls, parser):
        parser.add_argument(
            '--benchmark-iterations', '-n',
            type=int,
            default=20,
            help='Total number of of iterations to perform in each benchmark')

    def __call__(self, args):
        @benchmark.Benchmark(iterations=args.benchmark_iterations)
        def long_authentication_flow():
            self.get_admin_client(args)

        long_authentication_flow()
