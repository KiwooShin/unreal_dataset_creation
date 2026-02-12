# Plan: Explore Unreal Engine MCP Server

**Date:** February 8, 2026
**Status:** Planned

## Goal
Explore and evaluate the Unreal Engine MCP (Model Context Protocol) server to potentially improve the workflow for controlling Unreal Engine from external tools.

## Repository
- URL: https://github.com/flopperam/unreal-engine-mcp.git
- Purpose: MCP server for Unreal Engine integration

## Background
Currently using a custom HTTP API server (`unreal_api_server_v2.py`) to control Unreal Engine. An MCP server could provide:
- Standardized protocol for tool integration
- Better integration with AI assistants (Claude)
- Potentially more robust communication

## Exploration Tasks

### 1. Clone and Review Repository
```bash
git clone https://github.com/flopperam/unreal-engine-mcp.git
```
- Review README and documentation
- Understand architecture and dependencies
- Check Unreal Engine version compatibility (need 5.6+)

### 2. Understand MCP Protocol
- What is MCP (Model Context Protocol)?
- How does it differ from HTTP API approach?
- What tools/resources does the server expose?

### 3. Analyze Features
- [ ] Scene manipulation capabilities
- [ ] Object spawning support
- [ ] Material/texture support
- [ ] Camera control
- [ ] Screenshot capture
- [ ] Asset management

### 4. Compare with Current Implementation
| Feature | Current HTTP API | MCP Server |
|---------|-----------------|------------|
| Scene setup | Yes | ? |
| Material support | Yes (new) | ? |
| Screenshot capture | Yes | ? |
| Camera control | Yes | ? |
| AI integration | Manual | Native |

### 5. Integration Assessment
- Can it replace `unreal_api_server_v2.py`?
- Can it complement existing workflow?
- What modifications would be needed?

## Expected Outcomes
- Understanding of MCP server capabilities
- Decision on whether to adopt, adapt, or continue with current approach
- If adopting: migration plan
- If not: documented reasons and potential feature ideas to borrow

## Notes
- Keep current implementation working during exploration
- Document any useful patterns or code from the MCP server
