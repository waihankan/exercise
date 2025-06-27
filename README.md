##  Challenge Solutions

Welcome to my write‑up repo for two web‑based CTF puzzles. Each solution lives in its own folder (one/ and two/) and comes with a standalone README.md explaining the exploit path step‑by‑step.

**TL;DR** — Clone, docker compose up, read the per‑folder guides, grab the flags. Nothing sensitive is committed.

📁 Repository Layout

.
├── one/                # Challenge #1 – Nginx auto‑index & .git
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── html/ …         # vulnerable site assets
│   └── README.md       # full exploit write‑up for challenge #1
├── two/                # Challenge #2 – PHP Google2FA OTP bypass
│   ├── otp/ …          # vulnerable PHP application
│   ├── docker-compose.yml
│   └── README.md       # full exploit write‑up for challenge #2
└── README.md           # ← you are here


### References:

Claude Chat Logs: 

One - https://claude.ai/share/889c39a6-b89a-4e06-bdf0-fe30a21d39e7
Two - https://claude.ai/share/fa0a54f5-3a3f-4c48-aa4c-722d1f230ca7
