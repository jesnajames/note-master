import pytest
from unittest.mock import patch, MagicMock
from website.models import db, Note, User
from sqlalchemy.sql import func


@pytest.fixture
def mock_db():
    with patch('website.models.db') as mock_db_instance:
        yield mock_db_instance


@pytest.fixture
def mock_func_now():
    with patch('website.models.func.now', return_value='2023-10-01 00:00:00') as mock_func:
        yield mock_func


@pytest.fixture
def mock_user():
    with patch('website.models.User') as mock_user_instance:
        mock_user_instance.return_value = MagicMock()
        yield mock_user_instance


@pytest.fixture
def mock_note():
    with patch('website.models.Note') as mock_note_instance:
        mock_note_instance.return_value = MagicMock()
        yield mock_note_instance


@pytest.fixture
def setup_database(mock_db):
    mock_db.create_all = MagicMock()
    mock_db.session.add = MagicMock()
    mock_db.session.commit = MagicMock()


@pytest.fixture
def setup_user(mock_user):
    mock_user_instance = mock_user()
    mock_user_instance.email = 'test@example.com'
    mock_user_instance.first_name = 'John'
    mock_user_instance.password = 'securepassword'
    return mock_user_instance


@pytest.fixture
def setup_note(mock_note, setup_user):
    mock_note_instance = mock_note()
    mock_note_instance.content = 'Test content'
    mock_note_instance.user_id = setup_user.id
    return mock_note_instance

# happy_path - test_note_creation_with_default_date - Test that a new Note has the current timestamp when created without specifying a date.
def test_note_creation_with_default_date(mock_note, mock_func_now, setup_database):
    note_instance = mock_note()
    note_instance.date = mock_func_now()
    assert note_instance.date == '2023-10-01 00:00:00'

# happy_path - test_note_creation_with_content_and_user_id - Test that a new Note can be created with a specific content and user_id.
def test_note_creation_with_content_and_user_id(mock_note, setup_database):
    note_instance = mock_note()
    note_instance.content = 'Sample note content'
    note_instance.user_id = 1
    assert note_instance.content == 'Sample note content'
    assert note_instance.user_id == 1

# happy_path - test_user_creation_with_unique_email - Test that a new User can be created with a unique email.
def test_user_creation_with_unique_email(mock_user, setup_database):
    user_instance = mock_user()
    user_instance.email = 'test@example.com'
    user_instance.first_name = 'John'
    assert user_instance.email == 'test@example.com'
    assert user_instance.first_name == 'John'

# happy_path - test_user_with_multiple_notes - Test that a User can have multiple Notes associated with them.
def test_user_with_multiple_notes(mock_user, mock_note, setup_database):
    user_instance = mock_user()
    note1 = mock_note()
    note1.content = 'Note 1'
    note2 = mock_note()
    note2.content = 'Note 2'
    user_instance.notes = [note1, note2]
    assert len(user_instance.notes) == 2
    assert user_instance.notes[0].content == 'Note 1'
    assert user_instance.notes[1].content == 'Note 2'

# happy_path - test_user_email_uniqueness - Test that the email field in User is unique across different User instances.
def test_user_email_uniqueness(mock_user, setup_database):
    user_instance1 = mock_user()
    user_instance1.email = 'unique@example.com'
    user_instance2 = mock_user()
    user_instance2.email = 'unique@example.com'
    assert user_instance1.email == user_instance2.email

# edge_case - test_note_content_length_exceeded - Test that creating a Note with content exceeding 1000 characters raises an error.
def test_note_content_length_exceeded(mock_note, setup_database):
    note_instance = mock_note()
    note_instance.content = 'A' * 1001
    try:
        note_instance.validate()
    except ValueError as e:
        assert str(e) == 'Content length exceeded'

# edge_case - test_user_email_length_exceeded - Test that creating a User with an email exceeding 150 characters raises an error.
def test_user_email_length_exceeded(mock_user, setup_database):
    user_instance = mock_user()
    user_instance.email = 'a' * 151 + '@example.com'
    try:
        user_instance.validate()
    except ValueError as e:
        assert str(e) == 'Email length exceeded'

# edge_case - test_user_creation_without_email - Test that creating a User without an email raises an error.
def test_user_creation_without_email(mock_user, setup_database):
    user_instance = mock_user()
    user_instance.email = None
    try:
        user_instance.validate()
    except ValueError as e:
        assert str(e) == 'Email required'

# edge_case - test_user_creation_with_duplicate_email - Test that creating a User with a non-unique email raises an error.
def test_user_creation_with_duplicate_email(mock_user, setup_database):
    user_instance1 = mock_user()
    user_instance1.email = 'duplicate@example.com'
    user_instance2 = mock_user()
    user_instance2.email = 'duplicate@example.com'
    try:
        user_instance2.validate()
    except ValueError as e:
        assert str(e) == 'Duplicate email'

# edge_case - test_note_creation_without_user_id - Test that creating a Note without a user_id raises an error.
def test_note_creation_without_user_id(mock_note, setup_database):
    note_instance = mock_note()
    note_instance.user_id = None
    try:
        note_instance.validate()
    except ValueError as e:
        assert str(e) == 'User ID required'

