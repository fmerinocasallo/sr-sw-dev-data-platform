"""
This module provides a social networking application.

The application allows users to post messages to their own timeline.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta

class Post:
    """
    A post on a user's timeline.

    Attributes:
        content:
            The content of the post.
        timestamp:
            The timestamp of the post.
    """

    def __init__(self, content: str):
        """
        Initializes a post.

        Args:
            content:
                The content of the post.
        """
        self.content = content
        self.timestamp = datetime.now().replace(second=0, microsecond=0)

    def __eq__(self, other: "Post") -> bool:
        """Checks if two posts are equal."""
        return self.content == other.content and self.timestamp == other.timestamp

    def __str__(self) -> str:
        """Returns a string representation of the post."""
        return f"{self.content} ({self._format_elapsed_time()})"

    def get_content(self) -> str:
        """Returns the content of the post."""
        return self.content

    def is_recent(self) -> bool:
        """Checks if the post is recent."""
        return (
            datetime.now().replace(second=0, microsecond=0) - self.timestamp
        ).total_seconds() <= 60

    def _format_elapsed_time(self) -> str:
        """Returns the elapsed time since the post was created."""
        delta = relativedelta(
            datetime.now().replace(second=0, microsecond=0),
            self.timestamp,
        )

        parts = []
        if delta.years > 0:
            parts.append(f"{delta.years} year{'s' if delta.years != 1 else ''}")

        if delta.months > 0:
            parts.append(f"{delta.months} month{'s' if delta.months != 1 else ''}")

        # Only show the days if the total elapsed time is less than a year.
        # Otherwise, the elapsed days are not meaningful.
        if (delta.days > 0) and (delta.years == 0):
            parts.append(f"{delta.days} day{'s' if delta.days != 1 else ''}")

        # Only show the hours if the total elapsed time is less than a month.
        # Otherwise, the elapsed hours are not meaningful.
        if (delta.hours > 0) and (delta.years == 0) and (delta.months == 0):
            parts.append(f"{delta.hours} hour{'s' if delta.hours != 1 else ''}")

        # Only show the minutes if the total elapsed time is less than a day.
        # Otherwise, the elapsed minutes are not meaningful.
        if (
            (delta.minutes > 0)
            and (delta.years == 0)
            and (delta.months == 0)
            and (delta.days == 0)
        ):
            parts.append(f"{delta.minutes} minute{'s' if delta.minutes != 1 else ''}")

        if len(parts) == 2:
            elapsed_time = f"{parts[0]} and {parts[1]} ago"
        elif len(parts) == 1:
            elapsed_time = f"{parts[0]} ago"
        else:
            # If the elapsed time is less than a minute, show "just now".
            elapsed_time = "just now"

        return elapsed_time


class User:
    """
    A user of a social network.

    Attributes:
        name:
            The name of the user.
        posts:
            The posts of the user.
    """

    def __init__(self, name: str):
        """
        Initializes a user.

        Args:
            name:
                The name of the user.
        """
        self.name = name
        self.posts = []

    def __eq__(self, other: "User") -> bool:
        """Checks if two users are equal."""
        return (self.name == other.name) and (self.posts == other.posts)

    def get_name(self) -> str:
        """Returns the name of the user."""
        return self.name

    def has_posts(self) -> bool:
        """Checks if the user has any posts."""
        return bool(self.posts)

    def count_posts(self) -> int:
        """Returns the number of posts the user has."""
        return len(self.posts)

    def get_posts(self) -> list[Post]:
        """Returns the posts of the user."""
        return [str(post) for post in self.posts]

    def add_post(self, post: str):
        """Adds a post to the user's timeline."""
        self.posts.append(Post(post))


class SocialNetwork:
    """
    A social network.

    Attributes:
        users:
            The users of the social network.
    """

    def __init__(self):
        """Initializes a social network."""
        self.users = {}

    def has_users(self) -> bool:
        """Checks if the social network has any users."""
        return bool(self.users)

    def add_user(self, name: str):
        """Adds a user to the social network."""
        self.users[name] = User(name)

    def has_user(self, name: str) -> bool:
        """Checks if the social network has a user with the given name."""
        return name in self.users

    def count_users(self) -> int:
        """Returns the number of users in the social network."""
        return len(self.users)

    def add_post(self, name: str, post: str):
        """
        Adds a post to the user's timeline.

        Args:
            name:
                The name of the user.
            post:
                The post to add.

        Raises:
            ValueError:
                If the user does not exist.
        """
        if not self.has_user(name):
            raise ValueError(f"User {name} does not exist")
        else:
            self.users[name].add_post(post)

    def get_user_posts(self, name: str) -> list[str]:
        """Returns the posts of the user."""
        if not self.has_user(name):
            raise ValueError(f"User {name} does not exist")
        return self.users[name].get_posts()


class Application:
    """
    A social networking application.

    Attributes:
        social_network:
            The social network of the application.
        commands:
            The commands of the application.
    """

    def __init__(self):
        """Initializes a social networking application."""
        self.social_network = SocialNetwork()
        self.commands = {
            "->": "posting",
        }.copy()

    def has_social_network(self) -> bool:
        """Checks if the application has a social network."""
        return bool(self.social_network)

    def get_social_network(self) -> SocialNetwork:
        """Returns the social network of the application."""
        return self.social_network

    def has_commands(self) -> bool:
        """Checks if the application has commands to execute."""
        return bool(self.commands)
    
    def parse_command(self, command: str):
        """Parses and executes a command.

        Args:
            command:
                The command to parse and execute.

        Raises:
            ValueError:
                If the command is invalid.
        """
        # Strip whitespace from command
        command = command.strip()

        # Check if the command is valid
        username, action, predicate = None, None, None
        for cmd in self.commands:
            if cmd in command:
                username, predicate = command.split(cmd)

                # Strip whitespace from username and predicate
                username = username.strip()
                predicate = predicate.strip()
                action = self.commands[cmd]
                break

        if action == "posting":
            if username and predicate:
                # If the user does not exist, add them to the social network
                if not self.social_network.has_user(username):
                    self.social_network.add_user(username)

                # Add the post to the user's timeline
                self.social_network.add_post(username, predicate)
            else:
                if not username:
                    # We expect a username
                    raise ValueError("Invalid posting command: username is empty")
                else:
                    # We expect a predicate
                    raise ValueError("Invalid posting command: message is empty")
        elif self.get_social_network().has_user(command):
            return None
        else:
            # Assume the command is invalid
            raise ValueError(f"Invalid command: {command}")