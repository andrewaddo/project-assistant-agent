# Security Sentinel: Universal Agent Guide

The Security Sentinel is an agnostic security layer for this project, packaged as a **Gemini CLI Extension**.

## 🛠 Installation (Gemini CLI)

To install the extension and enable native dropdown commands:
```bash
gemini extensions install ./sentinel-extension --scope workspace
/commands reload
```

## 🕹 Native Slash Commands
Once installed, use these in the Gemini CLI dropdown:
- `/sentinel:scan`: Run an audit.
- `/sentinel:watch`: Start background monitoring.
- `/sentinel:stop`: Stop background monitoring.
- `/sentinel:init`: Setup/Reset baseline.

## 🛠 Integration for Other Agents

### 1. Claude Code (Native MCP)
The extension bundles an MCP server. Connect Claude by adding this to your config:
```json
{
  "mcpServers": {
    "security-sentinel": {
      "command": "python3",
      "args": ["-m", "sentinel-extension.sentinel.mcp_server"]
    }
  }
}
```

### 2. Standard IDE Agents (Copilot, etc.)
Use the `sentinel` engine directly via Python:
- `python3 -m sentinel-extension.sentinel.cli scan`
- `python3 -m sentinel-extension.sentinel.cli watch --background`

## 🛡 Security Policy
- **Never commit unapproved secrets.**
- Findings are tracked in `.secrets.baseline`. False positives must be approved via the Sentinel.
