import time
import uuid

from keystoneclient.v3 import client


def uid():
    return uuid.uuid4().hex[:6]


def benchmark(method):
    def benchmarked(*args, **kw):
        print 'Benchmarking', method.__name__, '...',
        times = []
        for _ in range(BENCHMARK_ITERATIONS):
            start = time.time()
            result = method(*args, **kw)
            end = time.time()
            times.append(end - start)
        mean_time = sum(times) / BENCHMARK_ITERATIONS
        print '%2.3f seconds' % mean_time
        return result
    return benchmarked


BENCHMARK_ITERATIONS = 100
DEFAULT_DOMAIN_ID = 'default'
ADMIN_USERNAME = uid()
ADMIN_PASSWORD = uid()
ADMIN_PROJECT_NAME = uid()


def bootstrap_admin_client():
    """Bootstraps an admin client using keystone.conf's admin_token."""
    # bootstrap an admin user in the default domain
    c = client.Client(
        token='ADMIN',
        endpoint='http://localhost:35357/v3')

    user = c.users.create(
        name=ADMIN_USERNAME,
        domain=DEFAULT_DOMAIN_ID,
        password=ADMIN_PASSWORD)
    print 'Created user', user.name

    project = c.projects.create(
        name=ADMIN_PROJECT_NAME,
        domain=DEFAULT_DOMAIN_ID)
    print 'Created project', project.name

    # create an 'admin' role only if one does not already exist
    roles_by_name = dict((x.name, x) for x in c.roles.list())
    if 'admin' in roles_by_name:
        role = roles_by_name['admin']
    else:
        role = c.roles.create(
            name='admin')
    print 'Created role', role.name

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
        auth_url='http://localhost:35357/v3')

    # because we haven't set up a catalog yet
    c.management_url = 'http://localhost:35357/v3/'

    return c


def bootstrap_catalog(c):
    services_by_type = dict((x.type, x) for x in c.services.list())

    if 'identity' in services_by_type:
        identity = services_by_type['identity']
    else:
        identity = c.services.create(
            name='keystone',
            type='identity')

    identity_endpoints_by_interface = dict((x.interface, x)
                                           for x in c.endpoints.list()
                                           if x.service_id == identity.id)
    if 'admin' not in identity_endpoints_by_interface:
        c.endpoints.create(
            service=identity,
            interface='admin',
            url='http://localhost:35357/v3/')

    if 'internal' not in identity_endpoints_by_interface:
        c.endpoints.create(
            service=identity,
            interface='internal',
            url='http://localhost:5000/v3/')

    if 'public' not in identity_endpoints_by_interface:
        c.endpoints.create(
            service=identity,
            interface='public',
            url='http://localhost:5000/v3/')


def get_admin_client():
    """Authenticates as admin using the "long" auth flow."""
    c = client.Client(
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        auth_url='http://localhost:35357/v3')
    c.management_url = 'http://localhost:35357/v3'  # FIXME

    # find a project that we have access to
    project = c.projects.list(user=c.auth_ref.user_id).pop()

    return client.Client(
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        project_id=project.id,
        auth_url='http://localhost:35357/v3')


@benchmark
def authenticate():
    get_admin_client()


def main():
    c = bootstrap_admin_client()
    bootstrap_catalog(c)
    c = get_admin_client()

    # exercise a bit
    c.domains.list()
    c.users.list()
    c.projects.list()
    c.roles.list()

    authenticate()


if __name__ == '__main__':
    main()
