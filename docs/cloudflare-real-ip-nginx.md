# Cloudflare → nginx real client IP

**Why:** the whole site sits behind Cloudflare, so nginx only ever sees
Cloudflare's edge address. The access log proves it:

```
162.158.217.38 - - [30/Oct/2026:15:26:30 +0000] "POST /api/users/users/bulk-delete/ HTTP/1.1" 200 42 ...
162.159.122.140 - - [30/Oct/2026:15:36:06 +0000] "POST /api/users/users/bulk-delete/ HTTP/1.1" 200 42 ...
```

`162.158.0.0/15` and `162.159.0.0/16` are Cloudflare's ranges. Without
this change the real client address is never written to any log, so an
incident can never be attributed to a person.

**What it changes:** nginx verifies the peer is a Cloudflare address and
*then* trusts `CF-Connecting-IP`. A request that reaches the origin
directly (bypassing Cloudflare) is NOT from a trusted range, so a
forged `CF-Connecting-IP` is ignored and the real peer address is kept.
That is the trust anchor — the Django side trusts `X-Real-IP` because
only nginx sets it.

---

## 1. Inspect the current config first

```bash
cat /etc/nginx/sites-enabled/sakrshipping-backend
```

Note whether it already has `set_real_ip_from` / `real_ip_header`, and
whether its `proxy_set_header` block passes `X-Real-IP` to gunicorn.

---

## 2. Add this INSIDE the `server { }` block

Put it near the top of the `server` block, above any `location`
directives — `set_real_ip_from` and `real_ip_header` are valid in
`http`, `server` and `location` context, but they must be in effect
*before* the `location` that handles the request.

```nginx
# ---------------------------------------------------------------------
# Cloudflare real client IP
#
# Trust ONLY Cloudflare's published ranges. Because the trust list is
# limited to Cloudflare, a request that reaches the origin directly is
# never allowed to spoof CF-Connecting-IP.
#
# Ranges from https://www.cloudflare.com/ips/ -- re-check when adding
# new ones; this list is also useful for a firewall rule that keeps
# the origin reachable only through Cloudflare.
# ---------------------------------------------------------------------
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
set_real_ip_from 103.31.4.0/22;
set_real_ip_from 141.101.64.0/18;
set_real_ip_from 108.162.192.0/18;
set_real_ip_from 190.93.240.0/20;
set_real_ip_from 188.114.96.0/20;
set_real_ip_from 197.234.240.0/22;
set_real_ip_from 198.41.128.0/17;
set_real_ip_from 162.158.0.0/15;
set_real_ip_from 104.16.0.0/13;
set_real_ip_from 104.24.0.0/14;
set_real_ip_from 172.64.0.0/13;
set_real_ip_from 131.0.72.0/22;
set_real_ip_from 2400:cb00::/32;
set_real_ip_from 2606:4700::/32;
set_real_ip_from 2803:f800::/32;
set_real_ip_from 2405:b500::/32;
set_real_ip_from 2405:8100::/32;
set_real_ip_from 2a06:98c0::/29;
set_real_ip_from 2c0f:f248::/32;

# Use the single, Cloudflare-overwritten client address as $remote_addr.
real_ip_header CF-Connecting-IP;
real_ip_recursive on;
```

---

## 3. Pass the verified address to gunicorn

Find the `location` block that proxies to `127.0.0.1:8000` and make sure
it contains:

```nginx
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

`$remote_addr` is the **verified** client address at this point,
because `real_ip_header` already rewrote it. Django reads `X-Real-IP`
first, then `CF-Connecting-IP`, then `X-Forwarded-For`.

---

## 4. Apply and verify

```bash
nginx -t && systemctl reload nginx
```

The default nginx `log_format` uses `$remote_addr`, so the access log
starts showing the real client IP with no log-format change needed.

```bash
# should now show a real client address instead of 162.158.x / 162.159.x
grep -h 'bulk-delete' /var/log/nginx/*access*.log | tail -5
```

Do one bulk action from a browser (or any request) and re-check.

---

## 5. Optional but recommended: lock the origin to Cloudflare

The `set_real_ip_from` list stops header spoofing, but the origin is
still directly reachable on its own IP. Restricting 80/443 to
Cloudflare's ranges means the only path in is through Cloudflare, which
also protects against a second class of attack (origin IP discovery
plus Host-header spoofing):

```bash
# check whether the origin answers a direct request right now
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: backend.sakrshipping.com" http://194.164.76.107/
```

If it answers `200`/`301`/`403`, the origin is open. UFW example:

```bash
ufw default deny incoming
ufw allow 22/tcp
for r in 173.245.48.0/20 103.21.244.0/22 103.22.200.0/22 103.31.4.0/22 \
         141.101.64.0/18 108.162.192.0/18 190.93.240.0/20 188.114.96.0/20 \
         197.234.240.0/22 198.41.128.0/17 162.158.0.0/15 104.16.0.0/13 \
         104.24.0.0/14 172.64.0.0/13 131.0.72.0/22; do ufw allow from $r to any port 80 proto tcp; ufw allow from $r to any port 443 proto tcp; done
ufw enable
```

> Keep port 22 open and make sure you can still reach hPanel/SSH before
> enabling the firewall. If Hostinger manages the firewall for you, do
> this in the hPanel UI instead of via UFW.

---

## 6. Retroactive attribution (for the three accounts deleted on 30 Oct)

nginx cannot recover the client address for requests that are already
logged. **Cloudflare can** — it still knows the real client IP behind
`162.158.217.38` / `162.159.122.140`.

In the Cloudflare dashboard for `sakrshipping.com`:

1. **Security → Events**
2. Filter: `URI contains bulk-delete`, and the time window
   **30 Oct 2026, 14:00–15:40 UTC**
3. Each event shows the **real client IP** and the country/ASN

If the plan keeps events long enough, that gives you the actual address
of whoever ran those three bulk-deletes. For events older than the
retention window, Logpush (or a Workers-based export) is the way to
keep a permanent copy going forward.

---

## 7. Matching logins to the deletes (same-session evidence)

The audit trail now records the actor for every destructive action, but
for the three deletions that already happened the strongest remaining
evidence is the login that preceded them. In nginx's log, the client
address and the path are both recorded, so the session is visible even
though the address is Cloudflare's:

```bash
grep -hE 'POST /api/login/|bulk-delete' /var/log/nginx/*access*.log \
  | grep '30/Oct/2026:1[45]:' | tail -40
```

A successful login returns a large body (the JWT pair, ~1000+ bytes);
a rejected one returns a small error body. So the log tells you which
login attempts *succeeded* — and the audit trail deployed alongside
this change records the account email for every future login, so the
two sources line up from now on.
