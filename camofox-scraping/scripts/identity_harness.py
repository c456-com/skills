#!/usr/bin/env python3
"""CamoFox identity-persistence harness — raw-response version (no shell pipe noise)."""
import json
import subprocess
import sys
import time

B = "http://127.0.0.1:9378"
O = "http://127.0.0.1:8899"


def curl(method, path, body=None, timeout=40):
    cmd = ["curl", "-s", "-m", str(timeout), "-X", method, f"{B}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"_raw": r.stdout[:300], "_rc": r.returncode}


def oracle(path):
    r = subprocess.run(["curl", "-s", "-m", "5", f"{O}{path}"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"_raw": r.stdout[:200]}


def newtab(user, key):
    return curl("POST", "/tabs", {"userId": user, "sessionKey": key}).get("tabId")


def nav(user, tab, url):
    return curl("POST", f"/tabs/{tab}/navigate", {"userId": user, "url": url})


def dom(user, tab):
    r = curl("POST", f"/tabs/{tab}/evaluate",
             {"userId": user, "expression": "document.body.innerText.trim()"})
    if "result" in r:
        return r["result"]
    return f"<EVAL-ERR {json.dumps(r, ensure_ascii=False)[:200]}>"


def login(user, who):
    tab = newtab(user, "login")
    nav(user, tab, f"{O}/login?u={who}")
    nav(user, tab, f"{O}/who")
    identity = dom(user, tab)
    nav(user, tab, f"{O}/idb-set")
    idb = dom(user, tab)
    return tab, identity, idb


def probe(user, label):
    tab = newtab(user, "probe-" + label)
    out = {"label": label, "userId": user, "tab": tab}
    for name, path in (("who", "/who"), ("localStorage", "/lsread"), ("IndexedDB", "/idb-read")):
        n = nav(user, tab, f"{O}{path}")
        out[name] = dom(user, tab) if "error" not in n else f"<NAV-ERR {json.dumps(n)[:160]}>"
    curl("DELETE", f"/tabs/{tab}", {"userId": user})
    return out


def show(title, obj):
    print(f"\n--- {title}")
    if isinstance(obj, str):
        print("  " + obj)
        return
    for k, v in obj.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    U = "harness-main"

    if mode in ("all", "login"):
        print("=== oracle live sessions before:", oracle("/status"))
        tab, ident, idb = login(U, "harness-tester")
        show("P1 登录后（同进程同会话）", {"tab": tab, "who": ident, "idb": idb})
        show("P2 会话内探针", probe(U, "same-session"))
        show("P3 关会话 → 触发 checkpoint", curl("DELETE", f"/sessions/{U}"))

    if mode in ("all", "after-restart"):
        print("\n=== oracle live sessions now:", oracle("/status"), "(服务端真源必须仍活)")
        show("P4 跨进程重启后探针（同 userId）", probe(U, "after-restart"))
        show("P5 对照：全新 userId 读同一登录态", probe("harness-stranger", "stranger"))

    if mode in ("all", "cleanup"):
        show("P6 清除落盘状态", curl("DELETE", f"/sessions/{U}/storage_state"))
        show("P7 清后再读（同 userId，应登出）", probe(U, "after-reset"))
        show("P8 收尾 health", curl("GET", "/health"))
