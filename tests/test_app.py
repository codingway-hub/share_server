import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from share_server import create_app
from share_server.models import db, File, Note
import io
import json


def test_file_operations():
    """Test complete file upload, download, list, and delete operations."""
    app = create_app()
    client = app.test_client()

    # Test file upload
    data = {
        'file': (io.BytesIO(b'test content'), 'test.txt'),
    }
    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    result = response.get_json()
    assert 'id' in result
    assert result['filename'] == 'test.txt'
    file_id = result['id']

    # Test file download
    response = client.get(f'/api/files/{file_id}')
    assert response.status_code == 200
    assert b'test content' in response.data

    # Test list files
    response = client.get('/api/files')
    assert response.status_code == 200
    files = response.get_json()
    assert len(files) > 0
    assert any(f['id'] == file_id for f in files)

    # Test file delete
    response = client.delete(f'/api/files/{file_id}')
    assert response.status_code == 200

    # Verify file is deleted
    response = client.get(f'/api/files/{file_id}')
    assert response.status_code == 404

    print("File operations tests passed!")


def test_file_with_password():
    """Test file upload and download with password protection."""
    app = create_app()
    client = app.test_client()

    # Upload file with password
    data = {
        'file': (io.BytesIO(b'secret content'), 'secret.txt'),
        'password': 'test123',
    }
    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    result = response.get_json()
    assert result['has_password'] is True
    file_id = result['id']

    # Try to download without password
    response = client.get(f'/api/files/{file_id}')
    assert response.status_code == 401

    # Download with correct password
    response = client.get(f'/api/files/{file_id}?password=test123')
    assert response.status_code == 200
    assert b'secret content' in response.data

    # Download with wrong password
    response = client.get(f'/api/files/{file_id}?password=wrong')
    assert response.status_code == 401

    # Clean up
    client.delete(f'/api/files/{file_id}')

    print("File password protection tests passed!")


def test_note_operations():
    """Test complete note creation, retrieval, listing, and deletion."""
    app = create_app()
    client = app.test_client()

    # Test note creation
    response = client.post('/api/notes',
                          json={'title': 'Test Note', 'content': '# Hello\nThis is a test'})
    assert response.status_code == 201
    result = response.get_json()
    assert result['title'] == 'Test Note'
    assert result['content'] == '# Hello\nThis is a test'
    note_id = result['id']

    # Test note retrieval
    response = client.get(f'/api/notes/{note_id}')
    assert response.status_code == 200
    result = response.get_json()
    assert 'html_content' in result
    assert '<h1>Hello</h1>' in result['html_content']

    # Test list notes
    response = client.get('/api/notes')
    assert response.status_code == 200
    notes = response.get_json()
    assert len(notes) > 0
    assert any(n['id'] == note_id for n in notes)

    # Test note deletion
    response = client.delete(f'/api/notes/{note_id}')
    assert response.status_code == 200

    # Verify note is deleted
    response = client.get(f'/api/notes/{note_id}')
    assert response.status_code == 404

    print("Note operations tests passed!")


def test_note_with_password():
    """Test note creation and retrieval with password protection."""
    app = create_app()
    client = app.test_client()

    # Create note with password
    response = client.post('/api/notes',
                          json={'title': 'Secret Note', 'content': 'Secret content', 'password': 'secret123'})
    assert response.status_code == 201
    result = response.get_json()
    assert result['has_password'] is True
    note_id = result['id']

    # Try to retrieve without password
    response = client.get(f'/api/notes/{note_id}')
    assert response.status_code == 401

    # Retrieve with correct password
    response = client.get(f'/api/notes/{note_id}?password=secret123')
    assert response.status_code == 200
    result = response.get_json()
    assert result['content'] == 'Secret content'

    # Retrieve with wrong password
    response = client.get(f'/api/notes/{note_id}?password=wrong')
    assert response.status_code == 401

    # Clean up
    client.delete(f'/api/notes/{note_id}')

    print("Note password protection tests passed!")


def test_password_verification():
    """Test password verification endpoint."""
    app = create_app()
    client = app.test_client()

    # Create protected file
    data = {
        'file': (io.BytesIO(b'protected'), 'protected.txt'),
        'password': 'filepass',
    }
    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    file_id = response.get_json()['id']

    # Create protected note
    response = client.post('/api/notes',
                          json={'title': 'Protected', 'content': 'content', 'password': 'notepass'})
    note_id = response.get_json()['id']

    # Test valid password for file
    response = client.post('/api/verify-password',
                          json={'type': 'file', 'id': file_id, 'password': 'filepass'})
    assert response.status_code == 200
    assert response.get_json()['valid'] is True

    # Test invalid password for file
    response = client.post('/api/verify-password',
                          json={'type': 'file', 'id': file_id, 'password': 'wrong'})
    assert response.status_code == 401
    assert response.get_json()['valid'] is False

    # Test valid password for note
    response = client.post('/api/verify-password',
                          json={'type': 'note', 'id': note_id, 'password': 'notepass'})
    assert response.status_code == 200
    assert response.get_json()['valid'] is True

    # Test invalid password for note
    response = client.post('/api/verify-password',
                          json={'type': 'note', 'id': note_id, 'password': 'wrong'})
    assert response.status_code == 401
    assert response.get_json()['valid'] is False

    # Test missing fields
    response = client.post('/api/verify-password',
                          json={'type': 'file'})
    assert response.status_code == 400

    # Test invalid item type
    response = client.post('/api/verify-password',
                          json={'type': 'invalid', 'id': 1, 'password': 'test'})
    assert response.status_code == 400

    # Test invalid JSON
    response = client.post('/api/verify-password',
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 400

    # Test invalid item id
    response = client.post('/api/verify-password',
                          json={'type': 'file', 'id': 'invalid', 'password': 'test'})
    assert response.status_code == 400

    # Clean up
    client.delete(f'/api/files/{file_id}')
    client.delete(f'/api/notes/{note_id}')

    print("Password verification tests passed!")


def test_error_handling():
    """Test various error scenarios."""
    app = create_app()
    client = app.test_client()

    # Test file not found
    response = client.get('/api/files/99999')
    assert response.status_code == 404

    # Test note not found
    response = client.get('/api/notes/99999')
    assert response.status_code == 404

    # Test delete non-existent file
    response = client.delete('/api/files/99999')
    assert response.status_code == 404

    # Test delete non-existent note
    response = client.delete('/api/notes/99999')
    assert response.status_code == 404

    # Test file upload without file
    response = client.post('/api/files', data={}, content_type='multipart/form-data')
    assert response.status_code == 400

    # Test file upload with empty filename
    data = {'file': (io.BytesIO(b'content'), '')}
    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

    # Test note creation without title
    response = client.post('/api/notes', json={'content': 'content'})
    assert response.status_code == 400

    # Test note creation without content
    response = client.post('/api/notes', json={'title': 'title'})
    assert response.status_code == 400

    # Test invalid JSON
    response = client.post('/api/notes', data='invalid json', content_type='application/json')
    assert response.status_code == 400

    # Test verify password with non-existent file
    response = client.post('/api/verify-password',
                          json={'type': 'file', 'id': 99999, 'password': 'test'})
    assert response.status_code == 404

    print("Error handling tests passed!")


def test_page_routes():
    """Test page routes."""
    app = create_app()
    client = app.test_client()

    # Test index page
    response = client.get('/')
    assert response.status_code == 200

    # Test upload page
    response = client.get('/upload')
    assert response.status_code == 200

    # Test files page
    response = client.get('/files')
    assert response.status_code == 200

    # Test notes page
    response = client.get('/notes')
    assert response.status_code == 200

    print("Page routes tests passed!")


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("Running Comprehensive Share Server Test Suite")
    print("="*60 + "\n")

    tests = [
        ("File Operations", test_file_operations),
        ("File Password Protection", test_file_with_password),
        ("Note Operations", test_note_operations),
        ("Note Password Protection", test_note_with_password),
        ("Password Verification", test_password_verification),
        ("Error Handling", test_error_handling),
        ("Page Routes", test_page_routes),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}")
            test_func()
            passed += 1
            print(f"  PASSED\n")
        except AssertionError as e:
            failed += 1
            print(f"  FAILED: {e}\n")
        except Exception as e:
            failed += 1
            print(f"  ERROR: {e}\n")

    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
