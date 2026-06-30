# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-30

### Added

- Initial release of tmux-cursor-agent as an open-source project
- Extracted from the cursor-agent-delegate Hermes skill
- Core state detection engine (`core/watch.py`) with EXECUTING/STOPPED classification
- Pane reading utility (`core/read.py`) with adaptive line counts
- Monitoring daemon (`core/monitor.py`) with per-group polling
- State file registry (`core/registry.py`) for persistent state tracking
- Structured logging (`core/monitor_log.py`)
- Shell helper library (`core/cursor-watch-lib.sh`)
- Calibration fixtures and test framework for state detection
- Comprehensive documentation (quickstart, session lifecycle, state detection, messaging protocol, monitoring daemon, pitfalls)
- MIT License

### Changed

- Project renamed from `cursor-agent-delegate` to `tmux-cursor-agent`
- Python scripts refactored into the `core/` package with relative imports
- All project-specific references (huichang-stock-picker, team workflows, trading strategies) removed
- Git worktree, team role management, and multi-role workflow removed from scope
- Documentation rewritten for general-purpose usage
