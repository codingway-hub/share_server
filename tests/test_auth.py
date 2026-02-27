import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from share_server import create_app
import json

def test_verify_password():
    app = create_app()
    client = app.test_client()

    # Test missing fields
    response = client.post('/api/verify-password',
                          json={'type': 'file'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

    # Test invalid item type
    response = client.post('/api/verify-password',
                          json={'type': 'invalid', 'id': 1, 'password': 'test'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

    # Test invalid JSON
    response = client.post('/api/verify-password',
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 400

    # Test invalid item id
    response = client.post('/api/verify-password',
                          json={'type': 'file', 'id': 'invalid', 'password': 'test'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

    print("All auth tests passed!")
