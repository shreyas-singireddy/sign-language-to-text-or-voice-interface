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
    """Create venv and install all project requirements.

    Three-state logic:
    1. Python binary exists → reuse venv, skip creation.
    2. Dir exists but Python binary missing (stale/broken cache) →
       use UV_VENV_CLEAR=1 to overwrite pyvenv.cfg in-place.
       This avoids deleting the directory (which fails on Windows with
       long-path files inside sklearn/jax site-packages).
    3. Dir absent → create fresh.
    """
    use_uv = _uv_available()
    venv_python, venv_pip = _find_venv_python(venv_dir)

    if os.path.exists(venv_python):
        # Happy path: valid venv already present — skip creation entirely.
        print(f"[bootstrap] Reusing existing venv at {venv_dir!r}.", flush=True)
    else:
        env = os.environ.copy()
        if os.path.exists(venv_dir):
            # Stale/partial directory (e.g. cache without Python binary).
            # UV_VENV_CLEAR=1 rewrites pyvenv.cfg in-place — no deletion needed.
            # This avoids Windows MAX_PATH failures when long-path files exist.
            print(
                f"[bootstrap] Stale venv at {venv_dir!r} — recreating in-place ...",
                flush=True,
            )
            env["UV_VENV_CLEAR"] = "1"
        else:
            print(f"[bootstrap] Creating venv at {venv_dir!r} ...", flush=True)

        if use_uv:
            subprocess.run(
                ["uv", "venv", venv_dir, "--python", "3.12"],
                env=env,
                check=True,
            )
        else:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

        # Recompute paths after creation.
        venv_python, venv_pip = _find_venv_python(venv_dir)

    req_files: list[str] = []
    if os.path.exists("requirements.txt"):
        req_files += ["-r", "requirements.txt"]
    if os.path.exists("backend/requirements.txt"):
        req_files += ["-r", "backend/requirements.txt"]
    if os.path.exists("requirements-dev.txt"):
        req_files += ["-r", "requirements-dev.txt"]

    print("[bootstrap] Installing requirements ...", flush=True)

    if use_uv:
        # Pass the Python *binary* path — uv --python expects an interpreter,
        # not a venv directory path.
        subprocess.run(
            ["uv", "pip", "install", "--python", venv_python] + req_files,
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
    if os.name == "nt" and os.environ.get("CI") == "true":
        user_profile = os.environ.get("USERPROFILE", "C:\\Users\\shrey")
        venv_dir = os.path.join(user_profile, "sb_venv")
    else:
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
