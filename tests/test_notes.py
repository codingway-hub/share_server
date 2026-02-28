import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from share_server import create_app

def test_notes():
    app = create_app()
    client = app.test_client()

    # Create note
    response = client.post('/api/notes',
                          json={'title': 'Test Note', 'content': '# Hello\nThis is a test'})
    assert response.status_code == 201
    result = response.get_json()
    assert result['title'] == 'Test Note'

    note_id = result['id']

    # Get note
    response = client.get(f'/api/notes/{note_id}')
    assert response.status_code == 200
    result = response.get_json()
    assert 'html_content' in result

    # List notes
    response = client.get('/api/notes')
    assert response.status_code == 200

    # Delete note
    response = client.delete(f'/api/notes/{note_id}')
    assert response.status_code == 200

    print("Notes tests passed!")

if __name__ == '__main__':
    test_notes()
