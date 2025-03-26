import logging

import pytest
from httpx import ASGITransport, AsyncClient

from src.app.core.config import create_app, Settings
from src.app.core.containers import Container, TestContainer
from src.app.main import app


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_container():
    container = Container()
    test_container = TestContainer()
    test_container.config.from_pydantic(Settings())

    container.override(test_container)

    try:
        yield container

        test_container.reset_override()
        container.reset_override()
    finally:
        pass


@pytest.fixture(scope="session")
def async_client():
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://0.0.0.0:8000",
    )
    yield client
