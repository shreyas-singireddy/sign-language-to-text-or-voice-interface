# Sign-Language Computer Control Agent Specification

## Overview
This feature introduces a multi-agent system that allows users to control operating system processes, files, and folders using sign language gestures (visual commands).

## Requirements
- **Must Have**:
  - Webcam capture integration (Phase 1).
  - Gesture mapping to raw sign words (Phase 2).
  - Normalization of gesture sequences into textual commands (Phase 3).
  - Intent classification and target parameter extraction from natural language using the LLM Engine (Phase 4).
  - Step-by-step action planning (Phase 5).
  - Safe subprocess execution of computer automation commands (Notepad, Chrome, Downloads, etc.) (Phase 6).
  - Confirmation status reporting and Text-to-Speech vocalized feedback (Phase 7).
  - Isolation and mocking capabilities during tests to prevent side effects.
- **Nice to Have**:
  - Keyboard shortcut overrides for quick activation/deactivation.
  - Interactive process timeline on the Streamlit interface.
- **Non-goals**:
  - Arbitrary remote shell command execution. The system will restrict executed commands to a safe whitelist of system utilities.

## User Experience
- **Target User**: Sign language users seeking touchless or accessibility-oriented computer interaction, or system administrators configuring gesture dashboards.
- **Workflow**:
  1. User toggles the camera in the Sign Control dashboard.
  2. User signs a whitelisted command (e.g. `HELLO` + `YES` / `THANKS`) or inputs a custom text query.
  3. UI displays the real-time processing stream (Signs → Text → Intent → Plan → Execute).
  4. The system opens the targeted resource and speaks the status output back to the user.

## Architecture
- **Components affected**:
  - New service [computer_control_service.py](file:///c:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/ai_agent/computer_control_service.py) handles reasoning, planning, and execution.
  - New Streamlit page [computer_control.py](file:///c:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/computer_control.py) hosts the interface.
- **Dependencies**:
  - OpenCV, PyTorch/ONNX, LLMEngine, AudioService.

## Security & Privacy
- **Command Whitelisting**: The agent is restricted to standard application launchers (`notepad.exe`, `chrome.exe`, Explorer directories). No arbitrary shell execution is permitted.
- **Mock Mode**: During testing, the agent overrides active subprocess triggers to prevent execution.

## Testing Strategy
- **Unit Tests**:
  - Test intent extraction.
  - Test planning algorithm.
  - Test whitelisted application lookups.
  - Assert coverage is maintained >80% globally.
