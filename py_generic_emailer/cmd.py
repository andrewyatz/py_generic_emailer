import argparse
import csv
import configparser
from string import Template
import smtplib
from email.message import EmailMessage
import os


class EmailCmd:
    @classmethod
    def from_args(cls, args):
        return cls(
            template_file=args.template,
            config_file=args.config,
            input_file=args.input,
            verbose=args.verbose,
            live=args.live,
        )

    def __init__(
        self, template_file, config_file, input_file, verbose=False, live=False
    ):
        self.template_file = template_file
        self.config_file = config_file
        self.input_file = input_file
        self.verbose = verbose
        self.live = live
        self._template = None
        self._config = None

    @property
    def template(self):
        if self._template is None:
            with open(self.template_file) as f:
                data = f.read()
                self._template = Template(data)
        return self._template

    @property
    def config(self):
        if self._config is None:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            self._config = config
        return self._config

    def smtp(self):
        c = self.config
        s = smtplib.SMTP(host=c["smtp"]["host"], port=c["smtp"]["port"])
        if c["smtp"].getboolean("secure"):
            s.starttls()
        s.ehlo()
        if c["smtp"]["user"]:
            user = c["smtp"]["user"]
            password = os.getenv('PY_EMAILER_PASSWORD', None)
            if password is None and 'password' in c["smtp"]:
                password = c["smtp"]["password"]
            s.login(user, password)
        return s

    def generate_emails(self):
        config = self.config
        emails = []
        from_email = config["email"]["from"]
        subject_template = Template(config["email"]["subject"])
        template_defaults = dict(config["template.defaults"])
        if self.verbose:
            print(f"Template defaults: {template_defaults}")
        with open(self.input_file, mode="r") as csv_file:
            if self.input_file.endswith(".tsv"):
                csv_reader = csv.DictReader(csv_file, delimiter="\t")
            else:
                csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if self.verbose:
                    print(f"Parsing row for email address {row['email']}")
                    print(f"Values: {row}")
                sub_vars = template_defaults | row
                email_content = self.template.substitute(sub_vars)
                subject = subject_template.substitute(sub_vars)
                emails.append(
                    {
                        "to_email": row["email"],
                        "from_email": from_email,
                        "cc_emails": row.get("cc", ""),
                        "subject": subject,
                        "content": email_content,
                    }
                )
        if self.verbose:
            print(f"Created {len(emails)} email(s)")
        return emails

    def process_emails(self, emails):
        s = None
        if self.live:
            s = self.smtp()
        for email in emails:
            msg = EmailMessage()
            msg["Subject"] = email["subject"]
            msg["From"] = email["from_email"]
            msg["To"] = email["to_email"]
            msg["CC"] = email["cc_emails"]
            msg.set_content(email["content"])
            if self.live:
                print(f"Sending e-mail to {msg['To']}")
                s.send_message(msg)
            else:
                print("=" * 10)
                print(f"From: {msg['From']}")
                print(f"To: {msg['To']}")
                print(f"CC: {msg['CC']}")
                print(f"Subject: {msg['Subject']}")
                print(msg.get_content())

        if s is not None:
            s.quit()


def parse_args():
    p = argparse.ArgumentParser(description="Email lots of people")
    required = p.add_argument_group("required named arguments")
    required.add_argument(
        "-t",
        "--template",
        help="Path to the email template to use",
        type=str,
        required=True,
    )
    required.add_argument(
        "-c",
        "--config",
        help="Path to config file",
        type=str,
        required=True,
    )
    required.add_argument(
        "-i",
        "--input",
        help="Path to a CSV file. Each row will be merged into the template",
        type=str,
        required=True,
    )
    p.add_argument(
        "--live",
        help="Send the emails. Otherwise we print the content to screen",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    p.add_argument(
        "-v",
        "--verbose",
        help="Be chatty. Very chatty",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    return p.parse_args()


def cli():
    args = parse_args()
    cmd = EmailCmd.from_args(args)
    emails = cmd.generate_emails()
    cmd.process_emails(emails)


if __name__ == "__main__":
    cli()
