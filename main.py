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

    logging.debug(f"{log_prefix}: sending chunk 1 - '{a}'")
    yield str.encode(a)

    logging.debug(f"{log_prefix}: sleeping for {delay}s")
    time.sleep(delay)

    logging.debug(f"{log_prefix}: woke up, sending chunk 2 - '{b}'")
    yield str.encode(b)

def update_key(url, data):
    req = request.Request(url, data = data, method= "PUT")
    response = request.urlopen(req)
    code = response.getcode()
    if code != 200:
        raise NameError("bad code consul KV update: " + str(code))

    return response.read().decode('utf-8') == 'true'
    

def exec_consul_write(log_prefix, url, value, delay):
    logging.info(f"{log_prefix}: Starting request on {url} to update to '{value}'")

    iterator = iterate_data(log_prefix, split_string(value), delay=delay)
    keyUpdated = update_key(url, iterator)
    if keyUpdated:
        logging.info(f"{log_prefix}: key updated. Request Done")
    else:
        logging.info(f"{log_prefix}: key NOT updated. Request Done")

def fetch_key(url):
    url = f"{url}&raw=true"
    data = request.urlopen(url).read()

    logging.info(f"actual key '{data.decode('utf-8')}'")

KEY = "a/race/condition"
CAS = "cas=808"
PATH = f"/v1/kv/{KEY}?{CAS}"
URL_1 = "http://localhost:8500" + PATH
URL_2 = "http://localhost:9500" + PATH
URL_3 = "http://localhost:10500" + PATH

VAL_A = "SEQ-A1" * 1
VAL_B = "val b2" * 1
PREFIX_A = "R-A"
PREFIX_B = "R-B"

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s', datefmt='%M:%S', level=logging.INFO)

    URL_MASTER = URL_2

    DURATION_REQ_A = 1
    DURATION_REQ_B = 0.3
    DELAY_REQ_B = 0.1
    DELAY_GET_KEY = 0.5

    tA = Thread(target = exec_consul_write, args = (PREFIX_A, URL_1, VAL_A, DURATION_REQ_A))
    tB = Thread(target = exec_consul_write, args = (PREFIX_B, URL_2, VAL_B, DURATION_REQ_B))

    tA.start()
    if DELAY_REQ_B != 0.0:
        logging.debug(f"{PREFIX_B}: Delaying by {DELAY_REQ_B}s")
        time.sleep(DELAY_REQ_B)
    tB.start()

    tA.join()
    tB.join()

    time.sleep(DELAY_GET_KEY)
    fetch_key(URL_2)

    logging.info(f"Finished!")