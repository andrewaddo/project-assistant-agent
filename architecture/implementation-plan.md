# Implementation Plan - Security Sentinel Extension

This plan outlines the development of the "Security Sentinel," a Python-based security scanner packaged as a **Gemini CLI Extension** for native UI integration and multi-agent interoperability.

## Objective
Develop a single-codebase scanning system that provides real-time automatic alerts and manual ad-hoc scanning capabilities, integrated via native Slash Commands, MCP, and Git hooks.

## Proposed Architecture
- **Sentinel Extension**: A unified package containing:
  - **Manifest**: `gemini-extension.json` for name and MCP registration.
  - **Slash Commands**: TOML definitions for `/sentinel:scan`, `watch`, `stop`, `init`.
  - **Agent Skill**: Bundled instructions for AI-driven security workflows.
  - **Python Engine**: Core scanning and lifecycle management logic.
- **Git Hook Adapter**: Pre-commit configuration for local enforcement.

## Key Files & Structure
- `sentinel-extension/`:
  - `gemini-extension.json`: Extension manifest.
  - `commands/sentinel/`: Slash command definitions.
  - `skills/security-sentinel/`: Bundled Gemini skill.
  - `sentinel/`: Core Python engine.
- `requirements.txt`: Dependencies.
- `.pre-commit-config.yaml`: Git enforcement.

## Implementation Steps

### Phase 1.1: Extension Foundation
1. Define the extension structure and migrate existing Python logic.
2. Create the `gemini-extension.json` manifest with MCP server configuration.

### Phase 1.2: Native Slash Commands
1. Implement TOML definitions for all Sentinel subcommands in `commands/sentinel/`.
2. Verify that commands appear in the Gemini CLI dropdown menu.

### Phase 1.3: Skill & MCP Integration
1. Bundle the existing `security-sentinel` skill into the extension.
2. Ensure the MCP server is correctly exposed via the extension manifest.

### Phase 1.4: Packaging & Distribution
1. Package the extension for installation via Git.
2. Update the `AGENT_GUIDE.md` to reflect the new slash command interface.

### Phase 1.5: Final Verification
1. **UI Test**: Verify `/sentinel` triggers the dropdown and executes correctly.
2. **Agent Test**: Confirm the bundled skill still triggers for natural language requests.
3. **E2E Test**: Verify real-time alerts and commit-time blocking still function within the new structure.

## Verification Plan
1. **Real-time Test**: Save a mock secret while `sentinel watch` is running; verify alert within <1s.
2. **Commit Block Test**: Attempt `git commit` with a secret; verify blockage.
3. **Approval Flow**: Use `sentinel approve` to move a secret to baseline and verify it no longer triggers alerts.
