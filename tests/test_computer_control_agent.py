from unittest import mock

from ai_engine.ai_agent.computer_control_service import ComputerControlService, computer_control_service


def test_parse_intent_empty():
    service = ComputerControlService()
    res = service.parse_intent("")
    assert res["intent"] == "UNKNOWN"
    assert res["target"] == ""
    assert "Empty command" in res.get("error", "")

    res = service.parse_intent("   ")
    assert res["intent"] == "UNKNOWN"


def test_parse_intent_llm_success():
    service = ComputerControlService()
    with mock.patch("ai_engine.ai_agent.computer_control_service.llm_engine.generate_completion") as mock_completion:
        mock_completion.return_value = '{"intent": "OPEN_APPLICATION", "target": "chrome"}'
        res = service.parse_intent("open chrome browser")
        assert res["intent"] == "OPEN_APPLICATION"
        assert res["target"] == "chrome"


def test_parse_intent_llm_json_block():
    service = ComputerControlService()
    with mock.patch("ai_engine.ai_agent.computer_control_service.llm_engine.generate_completion") as mock_completion:
        mock_completion.return_value = (
            'Here is the result: ```json\n{"intent": "OPEN_FOLDER", "target": "downloads"}\n```'
        )
        res = service.parse_intent("open downloads please")
        assert res["intent"] == "OPEN_FOLDER"
        assert res["target"] == "downloads"


def test_parse_intent_llm_invalid_json_fallback():
    service = ComputerControlService()
    with mock.patch("ai_engine.ai_agent.computer_control_service.llm_engine.generate_completion") as mock_completion:
        # LLM returns garbage, it should fall back to rule-based parser
        mock_completion.return_value = "invalid response"
        res = service.parse_intent("open notepad")
        assert res["intent"] == "OPEN_APPLICATION"
        assert res["target"] == "notepad"


def test_parse_intent_rule_based_fallback():
    service = ComputerControlService()

    # App
    res = service.parse_intent("launch google chrome now")
    assert res["intent"] == "OPEN_APPLICATION"
    assert res["target"] == "chrome"

    # Folder
    res = service.parse_intent("show documents folder")
    assert res["intent"] == "OPEN_FOLDER"
    assert res["target"] == "documents"

    # File
    res = service.parse_intent("read my resume please")
    assert res["intent"] == "OPEN_FILE"
    assert res["target"] == "resume.pdf"

    # Catch-all
    res = service.parse_intent("open test_command_here")
    assert res["intent"] == "OPEN_APPLICATION"
    assert res["target"] == "test_command_here"

    # Unknown
    res = service.parse_intent("arbitrary gibberish text")
    assert res["intent"] == "UNKNOWN"
    assert res["target"] == ""


def test_create_execution_plan():
    service = ComputerControlService()

    # Unknown
    plan = service.create_execution_plan("UNKNOWN", "")
    assert len(plan) == 2
    assert "No valid execution target found" in plan[1]

    # Apps
    plan = service.create_execution_plan("OPEN_APPLICATION", "chrome")
    assert len(plan) == 4
    assert any("chrome" in step for step in plan)

    # Folders
    plan = service.create_execution_plan("OPEN_FOLDER", "downloads")
    assert len(plan) == 4
    assert any("downloads" in step for step in plan)

    # Files
    plan = service.create_execution_plan("OPEN_FILE", "resume.pdf")
    assert len(plan) == 4
    assert any("resume.pdf" in step for step in plan)

    # Other unsupported
    plan = service.create_execution_plan("OTHER_INTENT", "target")
    assert len(plan) == 2
    assert "Operation not supported" in plan[1]


def test_execute_action_invalid():
    service = ComputerControlService()
    ok, msg = service.execute_action("UNKNOWN", "")
    assert not ok
    assert "Could not determine valid system action" in msg

    ok, msg = service.execute_action("OTHER_INTENT", "target")
    assert not ok
    assert "Unsupported command" in msg


def test_execute_action_mock():
    service = ComputerControlService()
    ok, msg = service.execute_action("OPEN_APPLICATION", "notepad", mock=True)
    assert ok
    assert "Mock execution" in msg


def test_execute_action_app_whitelist_violation():
    service = ComputerControlService()
    ok, msg = service.execute_action("OPEN_APPLICATION", "malicious_app")
    assert not ok
    assert "safety whitelist" in msg


def test_execute_action_folder_whitelist_violation():
    service = ComputerControlService()
    ok, msg = service.execute_action("OPEN_FOLDER", "malicious_folder")
    assert not ok
    assert "safety whitelist" in msg


def test_execute_action_file_whitelist_violation():
    service = ComputerControlService()
    ok, msg = service.execute_action("OPEN_FILE", "malicious_file")
    assert not ok
    assert "safety whitelist" in msg


def test_execute_action_notepad_success():
    service = ComputerControlService()
    with mock.patch("subprocess.Popen") as mock_popen:
        ok, msg = service.execute_action("OPEN_APPLICATION", "notepad")
        assert ok
        assert "Notepad has been opened successfully" in msg
        mock_popen.assert_called_once_with("notepad.exe")


def test_execute_action_chrome_success():
    service = ComputerControlService()
    with mock.patch("subprocess.Popen") as mock_popen:
        ok, msg = service.execute_action("OPEN_APPLICATION", "chrome")
        assert ok
        assert "Google Chrome has been opened successfully" in msg
        mock_popen.assert_called_once_with("cmd.exe /c start chrome", shell=True)  # nosec B604


def test_execute_action_app_failure():
    service = ComputerControlService()
    with mock.patch("subprocess.Popen", side_effect=OSError("Access denied")):
        ok, msg = service.execute_action("OPEN_APPLICATION", "notepad")
        assert not ok
        assert "Failed to open 'notepad': Access denied" in msg


def test_execute_action_folder_downloads_success():
    service = ComputerControlService()
    with mock.patch("os.path.exists", return_value=True), mock.patch("os.startfile") as mock_startfile:
        ok, msg = service.execute_action("OPEN_FOLDER", "downloads")
        assert ok
        assert "Downloads folder opened successfully" in msg
        mock_startfile.assert_called_once()


def test_execute_action_folder_not_exist():
    service = ComputerControlService()
    with mock.patch("os.path.exists", return_value=False):
        ok, msg = service.execute_action("OPEN_FOLDER", "downloads")
        assert not ok
        assert "does not exist on this machine" in msg


def test_execute_action_folder_failure():
    service = ComputerControlService()
    with (
        mock.patch("os.path.exists", return_value=True),
        mock.patch("os.startfile", side_effect=OSError("Explorer error")),
    ):
        ok, msg = service.execute_action("OPEN_FOLDER", "downloads")
        assert not ok
        assert "Failed to open folder: Explorer error" in msg


def test_execute_action_file_docs_success():
    service = ComputerControlService()
    with mock.patch("os.path.exists", return_value=True), mock.patch("os.startfile") as mock_startfile:
        ok, msg = service.execute_action("OPEN_FILE", "resume.pdf")
        assert ok
        assert "File 'resume.pdf' opened successfully." in msg
        mock_startfile.assert_called_once()


def test_execute_action_file_workspace_success():
    service = ComputerControlService()
    # first exists call is for Documents (False), second exists call is for project root (True)
    with mock.patch("os.path.exists", side_effect=[False, True]), mock.patch("os.startfile") as mock_startfile:
        ok, msg = service.execute_action("OPEN_FILE", "resume.pdf")
        assert ok
        assert "File 'resume.pdf' opened successfully from workspace." in msg
        mock_startfile.assert_called_once()


def test_execute_action_file_dummy_creation():
    service = ComputerControlService()
    # documents exists (False), workspace exists (False)
    with (
        mock.patch("os.path.exists", side_effect=[False, False]),
        mock.patch("builtins.open", mock.mock_open()) as mock_file,
        mock.patch("os.startfile") as mock_startfile,
    ):
        ok, msg = service.execute_action("OPEN_FILE", "resume.pdf")
        assert ok
        assert "Created and opened dummy 'resume.pdf'" in msg
        mock_file.assert_called_once()
        mock_startfile.assert_called_once()


def test_execute_action_file_failure():
    service = ComputerControlService()
    with mock.patch("os.path.exists", side_effect=OSError("disk error")):
        ok, msg = service.execute_action("OPEN_FILE", "resume.pdf")
        assert not ok
        assert "Failed to open file: disk error" in msg


def test_singleton_service():
    assert computer_control_service is not None
    assert isinstance(computer_control_service, ComputerControlService)
