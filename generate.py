import string
import secrets
import logging
import subprocess


_alphanumeric = string.ascii_letters + string.digits


def ssid():
    with open("cities.txt", "r") as file:
        cities = file.readlines()

    city = secrets.choice(cities).strip()
    postfix = "".join(secrets.choice(_alphanumeric) for _ in range(2))

    return f"{city}-{postfix.upper()}"


def password(length: int):
    try:
        return subprocess.check_output(["pwgen", str(length), "1"]).decode().strip()
    except FileNotFoundError:
        logging.warning(
            "pwgen not found, using fallback implementation which produces less memorable passwords."
        )

    while True:
        password = "".join(secrets.choice(_alphanumeric) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
        ):
            return password
