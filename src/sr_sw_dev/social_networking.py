"""
This module provides a social networking application.

The application allows users to:
- post messages to their own timeline (e.g. "Alice -> I love the weather today!").
- read the timeline of another user (e.g. "Alice").
- follow other users (e.g. "Alice follows Bob").
- read the wall of another user (e.g. "Alice wall").
"""

import configparser
from datetime import datetime
from functools import total_ordering
import logging
import logging.config
import os

from dateutil.relativedelta import relativedelta

from src.sr_sw_dev import paths

# Create log directory if it doesn't exist
os.makedirs(paths.log_dir, exist_ok=True)

# Read and format the logging configuration
config = configparser.ConfigParser()
config.read(paths.config_dir / "logger.ini")

# Format the log directory in the file handler args
args = config.get("handler_file", "args")
args = args.format(log_dir=paths.log_dir)
config.set("handler_file", "args", args)

# Apply the logging configuration
logging.config.fileConfig(config, defaults={"log_dir": paths.log_dir})

log = logging.getLogger(__name__)


@total_ordering
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
        self.timestamp = datetime.now().replace(microsecond=0)

        log.debug(f"Post initialized: {self.content} ({self.timestamp})")

    def __eq__(self, other: "Post") -> bool:
        """Checks if this post is equal to another post."""
        return self.content == other.content and self.timestamp == other.timestamp

    def __lt__(self, other: "Post") -> bool:
        """Checks if this post is less than another post."""
        return self.timestamp < other.timestamp

    def __str__(self) -> str:
        """Returns a string representation of the post."""
        return f"{self.content} ({self._format_elapsed_time()})"

    def signed_copy(self, author: str) -> "Post":
        """Returns a copy of the post with the author's name."""
        post = Post(f"{author} - {self.content}")
        post.timestamp = self.timestamp

        return post

    def get_content(self) -> str:
        """Returns the content of the post."""
        return self.content

    def is_recent(self) -> bool:
        """Checks if the post is recent."""
        return (
            datetime.now().replace(microsecond=0) - self.timestamp
        ).total_seconds() < 1

    def _format_elapsed_time(self) -> str:
        """Returns the elapsed time since the post was created."""
        delta = relativedelta(
            datetime.now().replace(microsecond=0),
            self.timestamp,
        )

        # Only show the most meaningful time unit
        elapsed_time = ""
        if delta.years > 0:
            elapsed_time = f"{delta.years} year{'s' if delta.years != 1 else ''} ago"
        elif delta.months > 0:
            elapsed_time = f"{delta.months} month{'s' if delta.months != 1 else ''} ago"
        elif delta.days > 0:
            elapsed_time = f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        elif delta.hours > 0:
            elapsed_time = f"{delta.hours} hour{'s' if delta.hours != 1 else ''} ago"
        elif delta.minutes > 0:
            elapsed_time = (
                f"{delta.minutes} minute{'s' if delta.minutes != 1 else ''} ago"
            )
        elif delta.seconds > 0:
            elapsed_time = (
                f"{delta.seconds} second{'s' if delta.seconds != 1 else ''} ago"
            )
        else:
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
        following:
            The users that the user is following.
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
        self.following = []

        log.debug(f"User initialized: {self.name}")

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

    def get_posts(self, signed: bool = False) -> list[Post]:
        """
        Returns the posts of the user chronologically sorted.

        Args:
            signed:
                Whether to return signed posts.
        """
        if signed:
            posts = [post.signed_copy(self.name) for post in self.posts]
        else:
            posts = list(reversed(self.posts))

        return posts

    def add_post(self, post: str):
        """Adds a post to the user's timeline."""
        self.posts.append(Post(post))

        log.debug(f"Post added to {self.name}'s timeline: {post}")

    def get_timeline(self) -> list[str]:
        """Returns the timeline of the user."""
        return [str(post) for post in self.get_posts(signed=False)]

    def follows(self, user: "User"):
        """Adds a user to the user's following list."""
        self.following.append(user)

        log.debug(f"{self.name} follows {user.name}")

    def get_following(self) -> list["User"]:
        """Returns the users that the user is following."""
        return self.following

    def get_wall(self) -> list[str]:
        """Returns the wall of the user."""
        wall = self.get_posts(signed=True)
        wall.extend(
            [post for user in self.following for post in user.get_posts(signed=True)]
        )
        wall.sort()
        return [str(post) for post in wall]


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

        log.debug("Social network initialized")

    def has_users(self) -> bool:
        """Checks if the social network has any users."""
        return bool(self.users)

    def add_user(self, name: str):
        """Adds a user to the social network."""
        self.users[name] = User(name)

        log.debug(f"User added to social network: {name}")

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

        log.debug(f"Post added to {name}'s timeline in social network: {post}")

    def get_user_timeline(self, name: str) -> list[str]:
        """Returns the timeline of the user."""
        if not self.has_user(name):
            raise ValueError(f"User {name} does not exist")
        else:
            return [str(post) for post in self.users[name].get_posts(signed=False)]

    def follows(self, name: str, following: str):
        """Adds a user to the user's following list."""
        if not self.has_user(name):
            raise ValueError(f"User {name} does not exist")
        elif not self.has_user(following):
            raise ValueError(f"User {following} does not exist")
        else:
            self.users[name].follows(self.users[following])

            log.debug(f"{name} follows {following} in social network")

    def get_following(self, name: str) -> list[str]:
        """Returns the users that the user is following."""
        if not self.has_user(name):
            raise ValueError(f"User {name} does not exist")
        else:
            return [user.get_name() for user in self.users[name].get_following()]

    def get_user_wall(self, name: str) -> list[str]:
        """Returns the wall of the user."""
        if not self.has_user(name):
            raise ValueError(f"User {name} does not exist")
        else:
            wall = self.users[name].get_posts(signed=True)
            wall.extend(
                [
                    post
                    for user in self.users[name].get_following()
                    for post in user.get_posts(signed=True)
                ]
            )
            wall.sort(reverse=True)

            return [str(post) for post in wall]


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
            "follows": "following",
            "wall": "wall",
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

    def parse_command(self, command: str) -> list[str] | None:
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

        # Execute the command
        if action == "posting":
            log.debug(f"Posting command: {username} {predicate}")
            if username and predicate:
                if not self.social_network.has_user(username):
                    self.social_network.add_user(username)

                self.social_network.add_post(username, predicate)
            else:
                if not username:
                    raise ValueError("Invalid posting command: username is empty")
                else:
                    raise ValueError("Invalid posting command: message is empty")
        elif action == "following":
            log.debug(f"Following command: {username} {predicate}")
            if username and predicate:
                self.social_network.follows(username, predicate)
            else:
                if not username:
                    raise ValueError("Invalid following command: username is empty")
                else:
                    raise ValueError(
                        "Invalid following command: user to follow is empty"
                    )
        elif action == "wall":
            log.debug(f"Wall command: {username}")
            if username:
                return self.social_network.get_user_wall(username)
            else:
                raise ValueError("Invalid wall command: username is empty")
        elif self.get_social_network().has_user(command):
            # It is a reading command
            log.debug(f"Reading command: {command}")
            return self.get_social_network().get_user_timeline(command)
        elif len(command.split(" ")) == 1:
            # Assume the user is trying to read the timeline of a nonexistent user
            log.error(f"Invalid user: {command}")
            raise ValueError(f"Invalid user: {command}")
        else:
            # Assume the command is invalid
            log.error(f"Invalid command: {command}")
            raise ValueError(f"Invalid command: {command}")


if __name__ == "__main__":
    app = Application()

    while True:
        try:
            command = input("> ")
            if command.lower() == "exit":
                break
            else:
                result = app.parse_command(command)
                if result:
                    print("\n".join(result))
        except (KeyboardInterrupt, EOFError):
            print("Exit")
            break
        except ValueError as e:
            print(e)
