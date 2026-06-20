import os
import subprocess

from ai_engine.ai_agent.llm_engine import llm_engine
from config.logger import setup_logger

logger = setup_logger("ai_agent.computer_control")


class ComputerControlService:
    def __init__(self):
        # Whitelisted commands to prevent security violations
        self.whitelisted_apps = {
            "chrome": ["chrome", "google chrome"],
            "notepad": ["notepad", "editor"],
        }
        self.whitelisted_folders = {
            "downloads": ["downloads", "download folder"],
            "documents": ["documents", "documents folder"],
        }
        self.whitelisted_files = {
            "resume.pdf": ["resume", "resume.pdf", "cv.pdf"],
        }

    def parse_intent(self, command: str) -> dict:  # noqa: PLR0911
        """
        Uses LLM Engine or rule-based fallback to extract intent and target from command text.
        """
        cleaned_cmd = command.strip().lower()
        if not cleaned_cmd:
            return {"intent": "UNKNOWN", "target": "", "error": "Empty command"}

        system_prompt = (
            "You are a command parser. Convert user commands into structured JSON.\n"
            "Format: {\"intent\": \"INTENT_NAME\", \"target\": \"TARGET_NAME\"}\n"
            "Supported Intents: OPEN_APPLICATION, OPEN_FOLDER, OPEN_FILE\n"
            "Supported Targets: chrome, notepad, downloads, documents, resume.pdf\n"
            "Respond ONLY with valid JSON."
        )
        prompt = f"Command: {command}"

        try:
            response = llm_engine.generate_completion(prompt, system_prompt=system_prompt)
            # Try to locate JSON block
            if response and "{" in response and "}" in response:
                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                json_str = response[start_idx:end_idx]
                import json
                data = json.loads(json_str)
                if "intent" in data and "target" in data:
                    return {
                        "intent": data["intent"].upper(),
                        "target": data["target"].lower()
                    }
        except Exception as e:
            logger.error(f"Error parsing JSON from LLM response: {e}")

        # Rule-based Fallback Parser (Robust and fast)
        logger.info("Using rule-based fallback for intent parsing.")

        # Check Applications
        for app_key, aliases in self.whitelisted_apps.items():
            if any(alias in cleaned_cmd for alias in aliases):
                return {"intent": "OPEN_APPLICATION", "target": app_key}

        # Check Folders
        for folder_key, aliases in self.whitelisted_folders.items():
            if any(alias in cleaned_cmd for alias in aliases):
                return {"intent": "OPEN_FOLDER", "target": folder_key}

        # Check Files
        for file_key, aliases in self.whitelisted_files.items():
            if any(alias in cleaned_cmd for alias in aliases):
                return {"intent": "OPEN_FILE", "target": file_key}

        # Catch-all
        if "open" in cleaned_cmd:
            parts = cleaned_cmd.split("open", 1)
            target = parts[1].strip() if len(parts) > 1 else ""
            if target:
                return {"intent": "OPEN_APPLICATION", "target": target}

        return {"intent": "UNKNOWN", "target": ""}

    def create_execution_plan(self, intent: str, target: str) -> list[str]:
        """
        Creates a list of sequential steps to accomplish the goal.
        """
        if not intent or intent == "UNKNOWN" or not target:
            return ["Analyze request", "No valid execution target found."]

        if intent == "OPEN_APPLICATION":
            return [
                f"Verify application '{target}' matches whitelist",
                f"Locate environment binary for '{target}'",
                f"Initialize process for '{target}' via subprocess",
                f"Confirm active UI window for '{target}'"
            ]
        elif intent == "OPEN_FOLDER":
            return [
                f"Resolve system path for folder '{target}'",
                "Check read/write permissions on folder directory",
                f"Trigger system File Explorer to launch folder '{target}'",
                "Confirm Explorer frame registration"
            ]
        elif intent == "OPEN_FILE":
            return [
                f"Search directory tree for file '{target}'",
                "Verify safe file MIME type and handler",
                f"Invoke default shell viewer for '{target}'",
                "Confirm file viewer launched successfully"
            ]
        else:
            return ["Identify operation", "Operation not supported."]

    def execute_action(self, intent: str, target: str, mock: bool = False) -> tuple[bool, str]:  # noqa: PLR0911
        """
        Executes the planned action on the operating system.
        """
        if not intent or intent == "UNKNOWN" or not target:
            return False, "Could not determine valid system action."

        if mock:
            return True, f"Mock execution of {intent} for '{target}' completed successfully."

        # Whitelist filtering
        if intent == "OPEN_APPLICATION":
            if target not in self.whitelisted_apps:
                return False, f"Application '{target}' is not in the safety whitelist."

            try:
                if target == "notepad":
                    subprocess.Popen("notepad.exe")
                    return True, "Notepad has been opened successfully."
                elif target == "chrome":
                    # Use cmd start to trigger default browser launch path
                    subprocess.Popen("cmd.exe /c start chrome", shell=True)  # nosec B602
                    return True, "Google Chrome has been opened successfully."
            except Exception as e:
                logger.error(f"Failed to open application '{target}': {e}")
                return False, f"Failed to open '{target}': {str(e)}"

        elif intent == "OPEN_FOLDER":
            if target not in self.whitelisted_folders:
                return False, f"Folder '{target}' is not in the safety whitelist."

            try:
                if target == "downloads":
                    path = os.path.expanduser("~/Downloads")
                else:
                    path = os.path.expanduser("~/Documents")

                if os.path.exists(path):
                    os.startfile(path)  # nosec B606
                    return True, f"{target.capitalize()} folder opened successfully."
                else:
                    return False, f"Folder directory '{path}' does not exist on this machine."
            except Exception as e:
                logger.error(f"Failed to open folder '{target}': {e}")
                return False, f"Failed to open folder: {str(e)}"

        elif intent == "OPEN_FILE":
            if target not in self.whitelisted_files:
                return False, f"File '{target}' is not in the safety whitelist."

            try:
                # Look for file in Documents directory
                docs_path = os.path.expanduser(f"~/Documents/{target}")
                if os.path.exists(docs_path):
                    os.startfile(docs_path)  # nosec B606
                    return True, f"File '{target}' opened successfully."
                else:
                    # Look in local project root workspace
                    local_path = os.path.join(os.getcwd(), target)
                    if os.path.exists(local_path):
                        os.startfile(local_path)  # nosec B606
                        return True, f"File '{target}' opened successfully from workspace."
                    else:
                        # Create a mock dummy file to demonstrate functionality if missing
                        with open(local_path, "w") as f:
                            f.write("%PDF-1.4 Mock resume file generated by SignBridge AI Agent.")
                        os.startfile(local_path)  # nosec B606
                        return True, f"Created and opened dummy '{target}' in project workspace."
            except Exception as e:
                logger.error(f"Failed to open file '{target}': {e}")
                return False, f"Failed to open file: {str(e)}"

        return False, f"Unsupported command: intent={intent}, target={target}."


# Singleton service instance
computer_control_service = ComputerControlService()
