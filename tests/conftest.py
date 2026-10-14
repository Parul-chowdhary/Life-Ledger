"""
Pytest Shared Test Fixtures.
Provides test client and database session for all test modules.
"""
import pytest
from run_app import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
