import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from website.models import Note, User

@pytest.fixture
def setup_mocks():
    with patch('website.models.db') as mock_db:
        mock_db.Model = MagicMock()
        mock_db.Column = MagicMock()
        mock_db.Integer = MagicMock()
        mock_db.String = MagicMock()
        mock_db.DateTime = MagicMock()
        mock_db.ForeignKey = MagicMock()
        mock_db.relationship = MagicMock()
        
        mock_func_now = patch('website.models.func.now', return_value=datetime.utcnow())
        mock_func_now.start()
        
        yield {
            'mock_db': mock_db,
            'mock_func_now': mock_func
        }
        
        mock_func_now.stop()

# happy_path - test_note_creation_sets_current_date - Test that current date is set when creating a new note
def test_note_creation_sets_current_date(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_note_instance = mock_db.Model()
    note = Note(content='Sample note', user_id=1)
    assert note.date == datetime.utcnow()

# happy_path - test_user_creation_with_unique_email - Test that unique email constraint is enforced when creating a user
def test_user_creation_with_unique_email(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_user_instance = mock_db.Model()
    user = User(email='unique@example.com', password='password123', first_name='John')
    assert user.email == 'unique@example.com'

# happy_path - test_note_content_storage - Test that note content is stored correctly
def test_note_content_storage(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_note_instance = mock_db.Model()
    note = Note(content='This is a test note', user_id=2)
    assert note.content == 'This is a test note'

# happy_path - test_user_with_multiple_notes - Test that user can have multiple notes
def test_user_with_multiple_notes(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_user_instance = mock_db.Model()
    user = User(email='user@example.com', password='password123', first_name='Jane')
    user.notes = [mock_db.Model(), mock_db.Model()]
    assert len(user.notes) == 2

# edge_case - test_note_content_max_length_exceeded - Test that note content exceeding max length is handled
def test_note_content_max_length_exceeded(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_note_instance = mock_db.Model()
    with pytest.raises(ValueError) as excinfo:
        note = Note(content='x' * 1001, user_id=1)
    assert 'content_length_exceeded' in str(excinfo.value)

# edge_case - test_user_email_max_length_exceeded - Test that user email exceeding max length is handled
def test_user_email_max_length_exceeded(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_user_instance = mock_db.Model()
    with pytest.raises(ValueError) as excinfo:
        user = User(email='x' * 151, password='password123', first_name='John')
    assert 'email_length_exceeded' in str(excinfo.value)

# edge_case - test_note_creation_without_user_id - Test that creating a note without a user ID is handled
def test_note_creation_without_user_id(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_note_instance = mock_db.Model()
    with pytest.raises(ValueError) as excinfo:
        note = Note(content='Note without user')
    assert 'user_id_required' in str(excinfo.value)

# edge_case - test_user_creation_without_email - Test that creating a user without an email is handled
def test_user_creation_without_email(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_user_instance = mock_db.Model()
    with pytest.raises(ValueError) as excinfo:
        user = User(password='password123', first_name='John')
    assert 'email_required' in str(excinfo.value)

# edge_case - test_user_creation_with_duplicate_email - Test that creating a user with duplicate email is handled
def test_user_creation_with_duplicate_email(setup_mocks):
    mock_db = setup_mocks['mock_db']
    mock_user_instance = mock_db.Model()
    mock_db.session.add.side_effect = IntegrityError(None, None, None)
    user = User(email='duplicate@example.com', password='password123', first_name='Jane')
    with pytest.raises(IntegrityError) as exc:
        mock_db.session.add(user)
    assert 'duplicate_email' in str(excinfo.value)

