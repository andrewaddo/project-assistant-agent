---
name: sentinel
description: Proactively scans for secrets, keys, and sensitive data in the project. Use this skill to initialize security baselines, perform ad-hoc scans, or start a background proactive watcher that alerts on new secrets immediately upon save.
---

# Security Sentinel

The Security Sentinel protects your project from accidental secret leakage (API keys, passwords, etc.). It provides both manual auditing and real-time background protection.

## 🕹 Command Interface (Expansion)

When the user mentions "Sentinel" or "/sentinel", follow these rules:

1.  **No Subcommand**: If the user just says "Sentinel", **immediately use the `ask_user` tool** to provide a choice menu with: `scan`, `watch`, `stop`, and `init`.
2.  **With Subcommand**: If the user specifies a command (e.g., "sentinel scan"), execute the corresponding tool immediately without asking.

## Available Tools (Subcommands)

As the Security Sentinel agent, you have access to several native tools. 
To execute them universally across any environment, you **MUST** locate the `scripts/` directory within this skill's `<available_resources>`. 
Then, from the user's project root, use the `run_shell_command` tool with the following pattern to inject your scripts into the python path:

`PYTHONPATH=<absolute_path_to_skill_scripts> python3 -m sentinel.cli <command>`

### 1. `scan`
**Usage**: `PYTHONPATH=... python3 -m sentinel.cli scan [--path <path>]`
**Purpose**: Perform an on-demand audit. Use this when the user asks for a security check or before a major operation.

### 2. `watch`
**Usage**: `PYTHONPATH=... python3 -m sentinel.cli watch --background`
**Purpose**: Start the proactive background watcher. Use this to enable real-time protection.

### 3. `approve`
**Usage**: `PYTHONPATH=... python3 -m sentinel.cli approve <file_path> <line_number>`
**Purpose**: Appends a specific finding to the baseline as an approved exception. Use this when the user confirms a finding is a false positive.

### 4. `stop`
**Usage**: `PYTHONPATH=... python3 -m sentinel.cli stop`
**Purpose**: Stop the background watcher.

### 5. `init`
**Usage**: `PYTHONPATH=... python3 -m sentinel.cli init`
**Purpose**: Create or reset the security baseline (`.secrets.baseline`).

## Core Workflows

### 1. Initializing the Baseline
Before starting, you must create a baseline of existing secrets or false positives using the `init` tool.

### 2. Proactive Monitoring (Background)
To enable real-time alerts, start the background process using the `watch` tool.

### 3. Ad-hoc Security Audit
To scan the entire project or a specific file on demand, use the `scan` tool.

### 4. Resolving Findings
If a secret is detected:
1. **Fix it**: Move the secret to an ignored file (e.g., `.env`).
2. **Approve it**: If it's a false positive, run the `approve` tool to add it to the baseline.

## Troubleshooting
Ensure dependencies are installed via `pip install -r <absolute_path_to_skill_assets>/requirements.txt` if modules are missing.
