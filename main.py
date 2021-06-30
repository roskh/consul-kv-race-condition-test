from urllib import request
import time
import logging
from threading import Thread

KEY = "a/race/condition"
URL = "http://localhost:8500/v1/kv/" + KEY

def split_string(s):
    return (
        s[0:len(s)//2],
        s[len(s)//2: len(s)]
    )

def iterate_data(log_prefix, pair, sleep_time = 0.5):
    a, b = pair

    logging.info(f"{log_prefix}: sending chunk '{a}'")
    yield str.encode(a)

    logging.info(f"{log_prefix}: sleeping for {sleep_time}s")
    time.sleep(sleep_time)

    logging.info(f"{log_prefix}: woke up, sending chunk '{b}'")
    yield str.encode(b)

def exec_consul_write(log_prefix, value):
    logging.info(f"{log_prefix}: Starting request on {URL} to update to '{value}'")

    iterator = iterate_data(log_prefix, split_string(value))
    req = request.Request(URL, data = iterator, method= "PUT")
    response = request.urlopen(req)
    code = response.getcode()
    if code != 200:
        raise NameError("bad code " + str(code))

    logging.info(f"{log_prefix}: Request done")

def validate_request():
    time.sleep(0.1)

    url = f"{URL}?raw=true"
    data = request.urlopen(url).read()

    logging.info(f"actual key '{data.decode('utf-8')}'")


if __name__ == "__main__":
    valA = "val-A"
    valB = "val-B"

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s -- %(created).7fs', datefmt='%M:%S', level=logging.INFO)

    t1 = Thread(target = exec_consul_write, args = ("REQUEST-A", valA))
    t2 = Thread(target = exec_consul_write, args = ("REQUEST-B", valB))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    validate_request()

    logging.info(f"Finished!")