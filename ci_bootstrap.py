import os
import subprocess
import sys


def main() -> None:
    # 1. Create/Ensure virtual environment
    venv_dir = os.path.join("backend", ".venv")
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

    # 2. Compute virtual env paths
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    venv_python = os.path.abspath(os.path.join(venv_dir, bin_dir, "python" + (".exe" if os.name == "nt" else "")))
    venv_pip = os.path.abspath(os.path.join(venv_dir, bin_dir, "pip" + (".exe" if os.name == "nt" else "")))

    # 3. Bootstrap mode
    if len(sys.argv) > 1 and sys.argv[1] == "--bootstrap":
        # Upgrade pip
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        # Install requirements
        subprocess.run([venv_pip, "install", "-r", "backend/requirements.txt"], check=True)
        subprocess.run([venv_pip, "install", "-r", "requirements-dev.txt"], check=True)
        sys.exit(0)

    # 4. Command execution mode
    if len(sys.argv) > 1:
        cmd = sys.argv[1:]
        # If the command starts with a known tool, run it via the virtual environment python -m
        tool_mappings = [
            "black",
            "ruff",
            "mypy",
            "bandit",
            "pytest",
            "vulture",
            "flake8",
            "pylint",
            "detect-secrets",
        ]

        # Map detect-secrets command name to package import name
        if cmd[0] == "detect-secrets":
            run_cmd = [venv_python, "-m", "detect_secrets"] + cmd[1:]
        elif cmd[0] in tool_mappings:
            run_cmd = [venv_python, "-m", cmd[0]] + cmd[1:]
        else:
            # Add virtual env bin path to PATH and run directly
            venv_bin_path = os.path.abspath(os.path.join(venv_dir, bin_dir))
            os.environ["PATH"] = venv_bin_path + os.pathsep + os.environ["PATH"]
            run_cmd = cmd

        result = subprocess.run(run_cmd, check=False)
        sys.exit(result.returncode)
    else:
        print("Usage: python ci_bootstrap.py [--bootstrap | <command> [args...]]")
        sys.exit(1)


if __name__ == "__main__":
    main()
