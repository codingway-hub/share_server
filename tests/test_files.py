import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from share_server import create_app
import io

def test_file_upload():
    app = create_app()
    client = app.test_client()

    # Create a test file
    data = {
        'file': (io.BytesIO(b'test content'), 'test.txt'),
    }

    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    result = response.get_json()
    assert 'id' in result
    assert result['filename'] == 'test.txt'

    # Test list files
    response = client.get('/api/files')
    assert response.status_code == 200
    files = response.get_json()
    assert len(files) > 0

    print("File upload tests passed!")

if __name__ == '__main__':
    test_file_upload()
