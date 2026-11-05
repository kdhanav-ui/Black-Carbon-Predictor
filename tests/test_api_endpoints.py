from fastapi.testclient import TestClient
from src.api import app

def test_api_health_and_meta():
    client = TestClient(app)
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'healthy'
    
    r_meta = client.get('/api/meta')
    assert r_meta.status_code == 200
    assert 'bc_percentiles' in r_meta.json()

def test_api_tables():
    client = TestClient(app)
    r = client.get('/api/tables')
    assert r.status_code == 200
    assert 'virtual_sensor_leaderboard' in r.json()['tables']
    
    r_table = client.get('/api/tables/virtual_sensor_leaderboard')
    assert r_table.status_code == 200
    assert len(r_table.json()) > 0

def test_api_estimate_and_whatif():
    client = TestClient(app)
    r = client.post('/api/estimate', json={'readings': {'PM25': 80, 'WS': 1.0, 'AT': 22}})
    assert r.status_code == 200
    data = r.json()
    assert 'bc6_ng_m3' in data
    assert 'interval_90' in data
    assert 'explanation' in data

    r_sweep = client.post('/api/whatif/sweep', json={'readings': {'PM25': 80}, 'variable': 'CO', 'steps': 5})
    assert r_sweep.status_code == 200
    assert len(r_sweep.json()['ys']) == 5
