#!/usr/bin/env python3
"""Send a Markdown report as an email message."""

from __future__ import annotations

import argparse
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a Markdown email report.")
    parser.add_argument("--input", required=True, help="Markdown input file.")
    parser.add_argument("--subject", required=True, help="Email subject.")
    parser.add_argument(
        "--from",
        dest="sender",
        default=os.environ.get("WEEKLY_REVIEW_FROM", ""),
        help="Sender email address.",
    )
    parser.add_argument(
        "--to",
        default=os.environ.get("WEEKLY_REVIEW_TO", ""),
        help="Comma-separated recipient list.",
    )
    parser.add_argument(
        "--smtp-host",
        default=os.environ.get("WEEKLY_REVIEW_SMTP_HOST", ""),
        help="SMTP host.",
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        default=int(os.environ.get("WEEKLY_REVIEW_SMTP_PORT", "587")),
        help="SMTP port.",
    )
    parser.add_argument(
        "--smtp-username",
        default=os.environ.get("WEEKLY_REVIEW_SMTP_USERNAME", ""),
        help="SMTP username.",
    )
    parser.add_argument(
        "--smtp-password",
        default=os.environ.get("WEEKLY_REVIEW_SMTP_PASSWORD", ""),
        help="SMTP password.",
    )
    parser.add_argument(
        "--smtp-starttls",
        dest="smtp_starttls",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use STARTTLS before authenticating.",
    )
    return parser.parse_args()


def build_message(subject: str, sender: str, recipients: list[str], markdown: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(markdown)
    message.add_alternative(markdown, subtype="markdown")
    return message


def send_message(
    subject: str,
    sender: str,
    recipients: list[str],
    markdown: str,
    host: str,
    port: int,
    username: str,
    password: str,
    smtp_starttls: bool,
) -> None:
    message = build_message(subject, sender, recipients, markdown)
    if port == 465:
        client: smtplib.SMTP | smtplib.SMTP_SSL = smtplib.SMTP_SSL(host, port, timeout=60)
    else:
        client = smtplib.SMTP(host, port, timeout=60)

    with client as smtp:
        smtp.ehlo()
        if smtp_starttls and port != 465:
            smtp.starttls()
            smtp.ehlo()
        if username:
            smtp.login(username, password)
        smtp.send_message(message)


def main() -> int:
    args = parse_args()
    if not args.sender:
        raise SystemExit("Missing sender address. Set WEEKLY_REVIEW_FROM or pass --from.")
    if not args.to:
        raise SystemExit("Missing recipient list. Set WEEKLY_REVIEW_TO or pass --to.")
    if not args.smtp_host:
        raise SystemExit("Missing SMTP host. Set WEEKLY_REVIEW_SMTP_HOST or pass --smtp-host.")

    input_path = Path(args.input)
    markdown = input_path.read_text(encoding="utf-8")
    recipients = [item.strip() for item in args.to.split(",") if item.strip()]
    if not recipients:
        raise SystemExit("No valid recipients were provided.")

    send_message(
        subject=args.subject,
        sender=args.sender,
        recipients=recipients,
        markdown=markdown,
        host=args.smtp_host,
        port=args.smtp_port,
        username=args.smtp_username,
        password=args.smtp_password,
        smtp_starttls=args.smtp_starttls,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
