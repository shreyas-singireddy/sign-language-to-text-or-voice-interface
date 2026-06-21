"""
ci_bootstrap.py — Cross-platform CI venv bootstrap helper.

Usage:
    python ci_bootstrap.py --bootstrap          # Create venv + install deps
    python ci_bootstrap.py <tool> [args...]     # Run tool inside venv

Supported tool aliases:
    black, ruff, mypy, bandit, pytest,
    vulture, flake8, pylint, detect-secrets
"""

import os
import subprocess
import sys


def _find_venv_python(venv_dir: str) -> tuple[str, str]:
    """Return (python_path, pip_path) for the given venv directory."""
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    python = os.path.abspath(os.path.join(venv_dir, bin_dir, f"python{suffix}"))
    pip = os.path.abspath(os.path.join(venv_dir, bin_dir, f"pip{suffix}"))
    return python, pip


def _uv_available() -> bool:
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def bootstrap(venv_dir: str) -> None:
    """Create venv (if missing) and install all project requirements."""
    use_uv = _uv_available()

    if not os.path.exists(venv_dir):
        print(f"[bootstrap] Creating venv at {venv_dir!r} ...", flush=True)
        if use_uv:
            subprocess.run(["uv", "venv", venv_dir, "--python", "3.12"], check=True)
        else:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    else:
        print(f"[bootstrap] Venv already exists at {venv_dir!r}.", flush=True)

    print("[bootstrap] Installing requirements ...", flush=True)
    venv_python, venv_pip = _find_venv_python(venv_dir)

    req_files = []
    if os.path.exists("backend/requirements.txt"):
        req_files += ["-r", "backend/requirements.txt"]
    if os.path.exists("requirements-dev.txt"):
        req_files += ["-r", "requirements-dev.txt"]

    if use_uv:
        subprocess.run(
            ["uv", "pip", "install", "--python", venv_dir] + req_files,
            check=True,
        )
    else:
        subprocess.run(
            [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
        )
        subprocess.run([venv_pip, "install"] + req_files, check=True)

    print("[bootstrap] Done.", flush=True)


def run_tool(venv_dir: str, cmd: list[str]) -> int:
    """Execute a tool from inside the venv. Returns exit code."""
    venv_python, _ = _find_venv_python(venv_dir)
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    venv_bin_path = os.path.abspath(os.path.join(venv_dir, bin_dir))

    TOOL_ALIASES: dict[str, list[str]] = {
        "detect-secrets": [venv_python, "-m", "detect_secrets"],
        "black": [venv_python, "-m", "black"],
        "ruff": [venv_python, "-m", "ruff"],
        "mypy": [venv_python, "-m", "mypy"],
        "bandit": [venv_python, "-m", "bandit"],
        "pytest": [venv_python, "-m", "pytest"],
        "vulture": [venv_python, "-m", "vulture"],
        "flake8": [venv_python, "-m", "flake8"],
        "pylint": [venv_python, "-m", "pylint"],
    }

    tool = cmd[0]
    args = cmd[1:]

    if tool in TOOL_ALIASES:
        run_cmd = TOOL_ALIASES[tool] + args
    else:
        # Unknown tool — prepend venv bin to PATH and run directly
        os.environ["PATH"] = venv_bin_path + os.pathsep + os.environ.get("PATH", "")
        run_cmd = cmd

    result = subprocess.run(run_cmd, check=False)
    return result.returncode


def main() -> None:
    venv_dir = os.path.join("backend", ".venv")

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--bootstrap":
        bootstrap(venv_dir)
        sys.exit(0)

    exit_code = run_tool(venv_dir, sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
