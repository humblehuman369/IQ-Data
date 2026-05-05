import os

os.environ['DATABASE_URL'] = 'postgresql+psycopg://flipcycle:flipcycle@localhost:5432/flipcycle_test'

from fastapi.testclient import TestClient

from main import app


def test_healthz_contract() -> None:
    client = TestClient(app)
    response = client.get('/healthz')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'service': 'flipcycle-api'}
