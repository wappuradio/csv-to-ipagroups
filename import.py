import datetime
import sys
import os
import csv
from typing import List, Tuple
from python_freeipa import ClientMeta

# CSV format
# <date>,<name>,<email>,<tg>,<irc>,...,GROUP1;GROUP2;GROUP3,...

FIRST_LINE_HAS_HEADER = True

# Field indices
EMAIL_FIELD = 2
NICK_FIELDS = [3, 4]  # TG, IRC
GROUP_FIELD = 9

# CSV "group" to FreeIPA group prefix map
GROUP_MAPPING = {
    "Tekniikka / Tech": "tekniikka",
    "Grafiikka / Graphics": "grafiikka",
}
# Add all users to this group
DEFAULT_GROUP = "toimittajat"


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


def read_csv(path: str) -> List[List[str]]:
    """
    Take a path to a CSV file and return a list of rows (which are lists of columns)
    """
    with open(path, 'r') as f:
        l = list(csv.reader(f))
        return l[1:] if FIRST_LINE_HAS_HEADER else l


def parse_responses(responses: List[List[str]]) -> List[FormResponse]:
    """
    Take in the data decoded from the CSV file and parse the rows in the FormResponse objects
    """
    parsed = []
    for response in responses:
        email = response[EMAIL_FIELD]
        nicks = []
        for field in NICK_FIELDS:
            if response[field]:
                nick = response[field].replace('@', '').lower()
                if nick not in nicks:
                    nicks.append(nick)
        groups = [DEFAULT_GROUP]
        for group in response[GROUP_FIELD].split(';'):
            if group in GROUP_MAPPING.keys():
                groups.append(GROUP_MAPPING[group])
        parsed.append(FormResponse(email=email, nicknames=nicks, groups=groups))
    return parsed


# Type alias
IpaUser = dict


def get_ipausers(ipa) -> List[IpaUser]:
    """
    Get the full user listing from FreeIPA. This is expected to be much faster than to do individual queries.
    """
    return ipa.user_find()['result']


def match_users(responses: List[FormResponse], ipausers: List[IpaUser]) -> List[Tuple[FormResponse, IpaUser]]:
    """
    Take form responses and FreeIPA user data, trying to find matches using either emails or nicknames
    """
    matches = []

    for response in responses:
        for ipauser in ipausers:
            if response.email in ipauser.get('mail', []):
                matches.append((response, ipauser))
                continue
            if ipauser['uid'][0] in response.nicknames:
                matches.append((response, ipauser))

    return matches


def parse_args() -> Tuple[str, str]:
    """
    Collect CLI arguments or exit if the input is invalid
    """
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <ipaserver>")
        sys.exit(1)

    path = sys.argv[1]
    ipaserver = sys.argv[2]

    if not os.path.isfile(path):
        print(f"{path} is not a file")
        sys.exit(1)

    return path, ipaserver


def main():
    year = datetime.datetime.now().strftime('%Y')
    path, ipaserver = parse_args()

    responses = parse_responses(read_csv(path))

    freeipa = ClientMeta(ipaserver)
    freeipa.login_kerberos()
    ipausers = get_ipausers(freeipa)

    matches = match_users(responses, ipausers)

    for match in matches:
        for group in match[0].groups:
            if f"{group}-{year}" not in match[1]['memberof_group']:
                print(f"ipa group-add-member {group}-{year} --users={match[1]['uid'][0]}")


if __name__ == "__main__":
    main()
