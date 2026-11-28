"""Small helper for the token scope tests. Reads DATABRICKS_HOST and DATABRICKS_TOKEN from the environment.
Token values are never printed; they are kept in tests/.tokens.json, which is gitignored."""
import json
import os
import urllib.error
import urllib.request

HOST = os.environ["DATABRICKS_HOST"].rstrip("/")
ADMIN = os.environ["DATABRICKS_TOKEN"]
TOKENS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tokens.json")


def call(path, body=None, token=None, method=None):
    """Return (http status, parsed JSON body). token defaults to your own full-access token."""
    req = urllib.request.Request(
        HOST + path, data=json.dumps(body).encode() if body is not None else None,
        method=method or ("POST" if body is not None else "GET"),
        headers={"Authorization": "Bearer " + (token or ADMIN), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw or b"{}")
        except ValueError:
            return e.code, {"raw": raw.decode(errors="replace")[:500]}


def load_tokens():
    return json.load(open(TOKENS_FILE)) if os.path.exists(TOKENS_FILE) else {}


def write_private(path, data):
    """Write JSON to a file that only the owner can read."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(path, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)


def save_tokens(t):
    write_private(TOKENS_FILE, t)


def create_token(name, scopes, lifetime=3600):
    """Create a short-lived test PAT, keep its value in the local file, print only non-secret fields."""
    st, r = call("/api/2.0/token/create", {"lifetime_seconds": lifetime, "comment": f"token-scopes test: {name}", "scopes": scopes})
    if st == 200:
        t = load_tokens()
        t[name] = {"value": r["token_value"], "token_id": r["token_info"]["token_id"], "scopes": scopes}
        save_tokens(t)
    return st, {k: v for k, v in r.items() if k != "token_value"}
