# Implementation Plan - Portable Security Sentinel Skill

This plan outlines the development of the "Security Sentinel," a Python-based security scanner designed for dual-mode operation: **Ad-hoc scanning** (via CLI/MCP) and **Automatic detection** (via a background watcher). It is packaged for interoperability across multiple AI agent platforms.

## Objective
Develop a single-codebase scanning system that provides real-time automatic alerts and manual ad-hoc scanning capabilities, integrated via MCP and Git hooks.

## Proposed Architecture
- **Sentinel Engine (Single Codebase)**: A unified Python tool providing the core scanning logic.
  - **Ad-hoc Mode**: CLI commands (`sentinel scan`, `sentinel status`) for manual or agent-driven checks.
  - **Automatic Mode**: A `sentinel watch` command that runs a background process using `watchdog` to scan files instantly upon modification/save.
- **MCP Adapter**: A thin wrapper within the codebase to expose ad-hoc tools to agents like Claude Code.
- **Git Hook Adapter**: A pre-commit configuration to enforce ad-hoc scans on staged changes.
- **Gemini CLI Skill**: A package that teaches Gemini CLI how to use both the ad-hoc commands and manage the watcher.

## Key Files & Structure
- `sentinel/`: Unified Python package.
  - `engine.py`: Core scanning, baseline logic, and severity scoring.
  - `watcher.py`: Logic for the persistent file system monitor (`sentinel watch`).
  - `cli.py`: The CLI entry point for all modes.
  - `mcp_server.py`: MCP adapter for external agent integration.
- `skill/`: Gemini CLI Skill package.
  - `SKILL.md`: Procedural instructions for triggering ad-hoc scans or starting the watcher.
- `requirements.txt`: Dependencies (`detect-secrets`, `watchdog`, `mcp`, `pre-commit`).
- `.pre-commit-config.yaml`: Git enforcement.

## Implementation Steps

### Phase 1.1: Unified Engine & CLI
1. Implement `sentinel/engine.py` for ad-hoc scanning logic.
2. Build the `sentinel` CLI with subcommands: `scan`, `status`, `approve`, and `watch`.

### Phase 1.2: Automatic Background Watcher
1. Implement the `watch` subcommand in `sentinel/watcher.py`.
2. Configure it to provide non-intrusive console alerts when a new secret is saved.
3. Add a "auto-remediation" hint in the alert (e.g., "Run `sentinel approve` to allow").

### Phase 1.3: MCP & Agent Connectivity
1. Implement `sentinel/mcp_server.py` to expose the ad-hoc `scan` and `status` tools.
2. Draft `AGENT_GUIDE.md` for non-MCP agents to explain the CLI usage.

### Phase 1.4: Git & Skill Packaging
1. Set up the `pre-commit` hook to run an ad-hoc scan.
2. Package the Gemini CLI Skill using `package_skill.cjs`.

### Phase 1.5: Verification
1. **Ad-hoc Validation**: Run `sentinel scan` and verify detection.
2. **Automatic Validation**: Run `sentinel watch`, save a "dirty" file, and verify the immediate alert.
3. **Cross-Agent Test**: Verify the MCP tools appear in a simulated MCP client.

## Verification Plan
1. **Real-time Test**: Save a mock secret while `sentinel watch` is running; verify alert within <1s.
2. **Commit Block Test**: Attempt `git commit` with a secret; verify blockage.
3. **Approval Flow**: Use `sentinel approve` to move a secret to baseline and verify it no longer triggers alerts.
