import time
import pytest
import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def docker_network():
    """
    Creates an isolated Docker bridge network for inter-container communication.

    Yields:
        Network: Testcontainers network instance allowing containers to reach
                 each other by container name/alias within the Docker daemon.
    """
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def postgres_container(docker_network):
    """
    Spins up a PostgreSQL database container, connects it to the shared Docker network,
    and executes DDL statements to seed the required database schema.

    Args:
        docker_network (Network): Shared Docker network instance.

    Yields:
        PostgresContainer: Running PostgreSQL container instance.
    """
    postgres = (
        PostgresContainer("postgres:16-alpine")
        .with_network(docker_network)
        .with_name("postgres-db")
        .with_bind_ports(5432, None)
    )
    with postgres:
        # Initialize the database schema for the REST API
        postgres.exec(
            "psql -U test -d test -c "
            "\"CREATE TABLE todos (id SERIAL PRIMARY KEY, title TEXT NOT NULL, completed BOOLEAN DEFAULT FALSE);\""
        )
        yield postgres


@pytest.fixture(scope="session")
def api_container(docker_network, postgres_container):
    """
    Spins up a PostgREST API container linked to the PostgreSQL container,
    and performs a polling wait strategy until the HTTP service returns 200 OK.

    Args:
        docker_network (Network): Shared Docker network instance.
        postgres_container (PostgresContainer): Dependency ensuring DB is initialized first.

    Yields:
        str: Dynamically mapped base URL of the API container accessible from the host.
    """
    db_uri = "postgres://test:test@postgres-db:5432/test"

    api = (
        DockerContainer("postgrest/postgrest:v12.0.2")
        .with_network(docker_network)
        .with_env("PGRST_DB_URI", db_uri)
        .with_env("PGRST_DB_SCHEMA", "public")
        .with_env("PGRST_DB_ANON_ROLE", "test")
        .with_bind_ports(3000, None)
    )

    with api:
        host = api.get_container_host_ip()
        port = api.get_exposed_port(3000)
        base_url = f"http://{host}:{port}"

        # Polling wait strategy: ensure the API is accepting HTTP connections
        timeout = 30
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(base_url, timeout=2.0)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            pytest.fail("API Container failed to start within timeout.")

        yield base_url


@pytest.fixture
def api_client(api_container):
    """
    Provides a per-test HTTP client session pre-configured with the dynamic base URL.

    Args:
        api_container (str): Base URL of the running API container.

    Yields:
        requests.Session: Configured requests session instance closed after test execution.
    """
    session = requests.Session()
    session.base_url = api_container
    yield session
    session.close()