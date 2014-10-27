import json
import time
import random
import datetime
import requests
from settings import BASE_URL, DUMP_FILE

POTS = 4

def pull():
    pots_moistures = _get_pots_moistures()
    with open(DUMP_FILE, 'w+') as outfile:
        _log("Dumping %s" % pots_moistures)
        _wait()
        json.dump(pots_moistures, outfile)

def _get_pots_moistures():
    pot_moistures = []
    for i in range(POTS):
        pot_moistures.append(_get_pot_moisture(i))
        _wait()
    return pot_moistures

def _get_pot_moisture(i, tries=1):
    url = BASE_URL + "/arduino/analog/%i" % i
    timeout = 5 + ((i + 1) * 1.5)
    _log("Trying %s (tries=%i, timeout=%f)" % (url, tries, timeout))

    try:
        response = requests.get(url, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return _retry(i, tries)

    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError,
            requests.exceptions.ReadTimeout):
        response.connection.close()
        return _retry(i, tries)

    _log("Pot %i moisture fetched!" % i)

    return int(response.content.split(' ')[-1])

def _retry(i, tries):
    _wait()
    tries += 1
    return _get_pot_moisture(i, tries)

def _wait():
    seconds = random.uniform(1.05, 4.05)
    _log("Waiting %f seconds" % seconds)
    time.sleep(seconds)

def _log(s):
    print datetime.datetime.now().time(), s


if __name__ == "__main__":
    print "Trying to get info, Ctrl+C to kill me"
    while True:
        pull()
