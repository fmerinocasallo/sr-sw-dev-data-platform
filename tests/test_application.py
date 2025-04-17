"""This module provides tests for the Application class."""

from datetime import datetime, timedelta

from freezegun import freeze_time
import pytest

from src.sr_sw_dev.social_networking import Application


def test_application_init():
    """Checks that an application is initialized correctly."""
    application = Application()
    assert application.has_social_network(), "Application should have a social network"
    assert application.has_commands(), "Application should have commands to execute"

def test_application_parse_command_posting():
    """Checks that an application can parse postings."""
    application = Application()
    application.parse_command("Alice -> I love the weather today!")
    
    assert application.get_social_network().get_user_posts("Alice") == ["I love the weather today! (just now)"], "Post should be visible in user's timeline"

def test_application_parse_command_posting_empty_user():
    """Checks that an application can parse postings with an empty user."""
    application = Application()

    with pytest.raises(ValueError, match="Invalid posting command: username is empty"):
        application.parse_command("-> I love the weather today!")

def test_application_parse_command_posting_empty_message():
    """Checks that an application can parse postings with an empty message."""
    application = Application()

    with pytest.raises(ValueError, match="Invalid posting command: message is empty"):
        application.parse_command("Alice ->")

def test_application_parse_command_reading():
    """Checks that an application can parse readings."""
    application = Application()

    with freeze_time(datetime.now() - timedelta(minutes=5)):
        application.parse_command("Alice -> I love the weather today!")

    with freeze_time(datetime.now() - timedelta(minutes=2)):
        application.parse_command("Bob -> Damn! We lost!")

    with freeze_time(datetime.now() - timedelta(minutes=1)):
        application.parse_command("Bob -> Good game though.")
    
    print(f"Alice's timeline: {application.parse_command('Alice')}")
    print(f"Bob's timeline: {application.parse_command('Bob')}")

    assert application.parse_command("Alice") == ["I love the weather today! (5 minutes ago)"], "Timeline should contain Alice's post"

    assert application.parse_command("Bob") == ["Good game though. (1 minute ago)", "Damn! We lost! (2 minutes ago)"], "Timeline should contain Bob's posts"

def test_application_parse_command_reading_nonexistent_user():
    """Checks that an application can parse readings with a nonexistent user."""
    application = Application()

    with pytest.raises(ValueError, match="Invalid user: Charlie"):
        application.parse_command("Charlie")

def test_application_parse_command_invalid_command():
    """Checks that an application can parse a command with an invalid command."""
    application = Application()

    with pytest.raises(ValueError, match="Invalid command: Alice reacts"):
        application.parse_command("Alice reacts")
