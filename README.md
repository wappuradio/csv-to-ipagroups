# CSV file to FreeIPA groups

Takes in a CSV file with rows somewhat resembling users to be added to groups in FreeIPA.

## Installation

```
git clone https://github.com/wappuradio/csv-to-ipagroups
cd csv-to-ipagroups
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip  # required or some dependencies will likely fail to install
pip install -r requirements.txt
```

## Configuration

For varying CSV field configurations see the beginning of import.py

## Usage

You need to have valid FreeIPA kerberos credentials. Use `kinit` on a domain joined host to get a ticket.

To avoid certificate errors you might have to tell requests where to find the CA certificates used by FreeIPA. On a RHEL like:
```
export REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem 
```

Run the tool:
```
python3 import.py <csv file path> <freeipa hostname>
```

The output will be a set of commands that when executed will add users to the groups (also allowing for manual review)
