# Let's Lunch!

A simple script to schedule lunch/coffee on Google Calendar for random pairs from a group of people.

For example, you can use this script to schedule monthly 1-on-1 lunch among your team.

## Prerequisites

* [pip](https://pypi.python.org/pypi/pip)
* [virtualenv](http://www.virtualenv.org/)

## Get Started

1. Get Google Account for use as a client.
2. Create project [here](https://console.developers.google.com/project).
3. Download client secrets in json format by selecting the project > `APIs $ auth` > `Credentials` > `Download JSON`.
4. Copy the downloaded contents into `config/client_secrets.json`.
5. Copy `config_example/members.json` into `config/members.json`.
6. Edit `members.json` as you need.
7. Copy `config_example/settings.json` into `config/settings.json`.
8. Edit `settings.json` as you need.
9. `virtualenv ve`
10. `source ve/bin/activate`
11. `pip install -r requirement.txt`
12. `python match.py`
