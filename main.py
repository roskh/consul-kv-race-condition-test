from urllib import request
import time
import logging
from threading import Thread


def split_string(s):
    return (
        s[0:len(s)//2],
        s[len(s)//2: len(s)]
    )

def iterate_data(log_prefix, pair, delay):
    a, b = pair

    logging.info(f"{log_prefix}: sending chunk 1 - '{a}'")
    yield str.encode(a)

    logging.info(f"{log_prefix}: sleeping for {delay}s")
    time.sleep(delay)

    logging.info(f"{log_prefix}: woke up, sending chunk 2 - '{b}'")
    yield str.encode(b)

def update_key(url, data):
    req = request.Request(url, data = data, method= "PUT")
    response = request.urlopen(req)
    code = response.getcode()
    if code != 200:
        raise NameError("bad code consul KV update: " + str(code))

def exec_consul_write(log_prefix, url, value, delay):
    logging.info(f"{log_prefix}: Starting request on {url} to update to '{value}'")

    iterator = iterate_data(log_prefix, split_string(value), delay=delay)
    update_key(url, iterator)

    logging.info(f"{log_prefix}: Request done")

def fetch_key(url):
    url = f"{url}?raw=true"
    data = request.urlopen(url).read()

    logging.info(f"actual key '{data.decode('utf-8')}'")

KEY = "a/race/condition"
URL = "http://localhost:8500/v1/kv/" + KEY

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s -- %(created).7fs', datefmt='%M:%S', level=logging.INFO)

    DELAY_REQ_A = 0.5
    DELAY_REQ_B = 0.5
    VAL_A = "SEQ-A"
    VAL_B = "val b"

    t1 = Thread(target = exec_consul_write, args = ("R-A", URL, VAL_A, DELAY_REQ_A))
    t2 = Thread(target = exec_consul_write, args = ("R-B", URL, VAL_B, DELAY_REQ_B))

    t1.start()
    time.sleep(0.10)
    t2.start()

    t1.join()
    t2.join()

    time.sleep(0.1)
    fetch_key(URL)

    logging.info(f"Finished!")