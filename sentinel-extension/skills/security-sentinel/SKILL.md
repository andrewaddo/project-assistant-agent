---
name: security-sentinel
description: Proactively scans for secrets, keys, and sensitive data in the project. Use this skill to initialize security baselines, perform ad-hoc scans, or start a background proactive watcher that alerts on new secrets immediately upon save.
---

# Security Sentinel

The Security Sentinel protects your project from accidental secret leakage (API keys, passwords, etc.). It provides both manual auditing and real-time background protection.

## 🕹 Command Interface (Expansion)

When the user mentions "Sentinel" or "/sentinel", follow these rules:

1.  **No Subcommand**: If the user just says "Sentinel", **immediately use the `ask_user` tool** to provide a choice menu with: `scan`, `watch`, `stop`, and `init`.
2.  **With Subcommand**: If the user specifies a command (e.g., "sentinel scan"), execute the corresponding tool immediately without asking.

## Available Tools (Subcommands)

As the Security Sentinel agent, you have access to the following native tools. Execute them using `python3 -m sentinel.cli <command>` from the project root.
...

### 1. `scan`
**Usage**: `python3 -m sentinel.cli scan [--path <path>]`
**Purpose**: Perform an on-demand audit. Use this when the user asks for a security check or before a major operation.

### 2. `watch`
**Usage**: `python3 -m sentinel.cli watch --background`
**Purpose**: Start the proactive background watcher. Use this to enable real-time protection.

### 3. `stop`
**Usage**: `python3 -m sentinel.cli stop`
**Purpose**: Stop the background watcher.

### 4. `init`
**Usage**: `python3 -m sentinel.cli init`
**Purpose**: Create or reset the security baseline (`.secrets.baseline`).

## Core Workflows

### 1. Initializing the Baseline
Before starting, you must create a baseline of existing secrets or false positives.
- Run: `python3 -m sentinel.cli init`

### 2. Proactive Monitoring (Background)
To enable real-time alerts:
- Run: `python3 -m sentinel.cli watch --background`

### 3. Ad-hoc Security Audit
To scan the entire project or a specific file on demand:
- Run: `python3 -m sentinel.cli scan`

### 4. Resolving Findings
If a secret is detected:
1. **Fix it**: Move the secret to an ignored file (e.g., `.env`).
2. **Approve it**: If it's a false positive, run `sentinel approve` (coming soon) to add it to the baseline.

## Troubleshooting
If `python3 -m sentinel.cli` is not found, ensure you are in the project root and dependencies are installed via `pip install -r requirements.txt`.
