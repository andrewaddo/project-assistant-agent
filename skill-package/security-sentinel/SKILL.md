---
name: security-sentinel
description: Proactively scans for secrets, keys, and sensitive data in the project. Use this skill to initialize security baselines, perform ad-hoc scans, or start a background proactive watcher that alerts on new secrets immediately upon save.
---

# Security Sentinel

The Security Sentinel protects your project from accidental secret leakage (API keys, passwords, etc.). It provides both manual auditing and real-time background protection.

## Core Workflows

### 1. Initializing the Baseline
Before starting, you must create a baseline of existing secrets or false positives.
- Run: `python3 -m sentinel.cli init`

### 2. Proactive Monitoring (Background)
To get immediate alerts whenever you save a file containing a secret:
- Run: `python3 -m sentinel.cli watch`
- Note: This process runs in the background and prints warnings to the console.

### 3. Ad-hoc Security Audit
To scan the entire project or a specific file on demand:
- Run: `python3 -m sentinel.cli scan`
- To scan a specific path: `python3 -m sentinel.cli scan --path <relative_path>`

### 4. Resolving Findings
If a secret is detected:
1. **Fix it**: Move the secret to an ignored file (e.g., `.env`).
2. **Approve it**: If it's a false positive, run `sentinel approve` (coming soon) to add it to the baseline.

## Troubleshooting
If `python3 -m sentinel.cli` is not found, ensure you are in the project root and dependencies are installed via `pip install -r requirements.txt`.
