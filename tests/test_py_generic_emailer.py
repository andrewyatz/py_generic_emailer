from py_generic_emailer import __version__
from py_generic_emailer import cmd
import os

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_config",
)


def _path(filename):
    return os.path.join(FIXTURE_DIR, filename)


def test_version():
    assert __version__ == "0.1.0"


def test_email():
    command = cmd.EmailCmd(
        template_file=_path("test.tmpl"),
        config_file=_path("test.ini"),
        input_file=_path("test.csv"),
    )
    emails = command.generate_emails()
    assert len(emails) == 2

    expected = """Hello Person,

You are a amazing person. Yes you are

Best wishes

A Person
"""
    assert expected == emails[0]["content"]
    assert "person@email.com" == emails[0]["to_email"]
    assert "email@domain.com" == emails[0]["from_email"]
    assert "Hello Person" == emails[0]["subject"]
