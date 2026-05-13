# Security Sentinel: Universal Agent Guide

The Security Sentinel is an agnostic security layer for this project. It provides proactive scanning and commit-time enforcement.

## 🛠 Integration for AI Agents

### 1. Claude Code (Native MCP)
The Sentinel includes an MCP server. You can connect Claude to it by adding this to your Claude config:
```json
{
  "mcpServers": {
    "security-sentinel": {
      "command": "python3",
      "args": ["-m", "sentinel.mcp_server"]
    }
  }
}
```

### 2. Standard IDE Agents (Gemini, Copilot, etc.)
If you are an AI agent operating in this codebase, use the `sentinel` CLI to help the user manage security findings.

**Available Commands:**
- `python3 -m sentinel.cli scan`: Run an audit.
- `python3 -m sentinel.cli status`: Check findings.
- `python3 -m sentinel.cli watch`: Start real-time background monitoring.
- `python3 -m sentinel.cli init`: Reset/Initialize baseline.

## 🛡 Security Policy
- **Never commit unapproved secrets.**
- If you find a secret, move it to a `.env` file (which is in `.gitignore`).
- If a finding is a **false positive**, run `sentinel approve` (or ask the user to) to add it to the `.secrets.baseline` file.

## 👁 Proactive Alerts
The background watcher provides real-time console output. If you see a `[PROACTIVE ALERT]` in the terminal, address it immediately.
