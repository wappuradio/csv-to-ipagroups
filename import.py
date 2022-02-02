import sys
import os
import csv
from typing import List

FIRST_LINE_HAS_HEADER = True

EMAIL_FIELD = 2
NICK_FIELDS = [3, 4] # TG, IRC
GROUP_FIELD = 9
GROUP_MAPPING = {
    "Tekniikka / Tech": "tekniikka"
}

class FormResponse:
    email: str
    nicknames: list
    groups: list

    def __init__(self, email: str, nicknames: List[str], groups: List[str]):
        self.email = email
        self.nicknames = nicknames
        self.groups = groups

    def __repr__(self):
        return f"<Response: {self.email}, {self.nicknames}, {self.groups}>"


def read_csv(path: str) -> List[str]:
    with open(path, 'r') as f:
        l = list(csv.reader(f))
        return l[1:] if FIRST_LINE_HAS_HEADER else l


def parse_responses(responses: List[str]) -> List[FormResponse]:
    parsed = []
    for response in responses:
        email = response[EMAIL_FIELD]
        nicks = []
        for field in NICK_FIELDS:
            if response[field]:
                nick = response[field].replace('@', '').lower()
                if nick not in nicks:
                    nicks.append(nick)
        groups = []
        for group in response[GROUP_FIELD].split(';'):
            if group in GROUP_MAPPING.keys():
                groups.append(GROUP_MAPPING[group])
        parsed.append(FormResponse(email=email, nicknames=nicks, groups=groups))
    return parsed


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input.csv>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"{path} is not a file")
        sys.exit(1)

    responses = parse_responses(read_csv(path))
    print(responses)


if __name__ == "__main__":
    main()
