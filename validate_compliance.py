import os
import sys
import subprocess

def print_result(check_name, status, details=""):
    color = "\033[92m" if status == "PASS" else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{status}{reset}] {check_name} {f'({details})' if details else ''}")

def check_file_exists(filepath, search_str=None):
    if not os.path.exists(filepath):
        return False, "File not found"
    if search_str:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if search_str not in content:
                    return False, f"Could not find expected string '{search_str}'"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    return True, "OK"

def main():
    print("====================================================")
    print("         SIGNBRIDGE AI COMPLIANCE VALIDATOR         ")
    print("====================================================\n")
    
    all_passed = True
    
    # 1. License Check
    lic_ok, lic_msg = check_file_exists("LICENSE", "GNU Affero General Public License")
    print_result("GNU AGPLv3 LICENSE File Check", "PASS" if lic_ok else "FAIL", lic_msg)
    if not lic_ok:
        all_passed = False

    # 2. Documentation Compliance
    docs = {
        "README.md": "SignBridge AI",
        "CONTRIBUTING.md": "Contributing to SignBridge AI",
        "USER_MANUAL.md": "End-User & Operator Manual",
        "AGENTS.md": "Agent Instructions",
        "CHANGELOG.md": "Changelog",
        "SECURITY.md": "Security Policy",
        "CODE_OF_CONDUCT.md": "Contributor Covenant Code of Conduct",
        "SECURITY_POLICY.md": "Security Policy for SignBridge AI",
        "SECURITY_AUDIT.md": "Security Audit & Threat Modeling"
    }
    for doc_file, search_str in docs.items():
        doc_ok, doc_msg = check_file_exists(doc_file, search_str)
        print_result(f"Documentation: {doc_file}", "PASS" if doc_ok else "FAIL", doc_msg)
        if not doc_ok:
            all_passed = False

    # 3. Repository Health Configurations
    health_configs = [
        ".editorconfig",
        ".env.example",
        ".dockerignore",
        "backend/.dockerignore",
        "frontend/.dockerignore",
        "backend/Dockerfile",
        "frontend/Dockerfile"
    ]
    for cfg in health_configs:
        cfg_ok, cfg_msg = check_file_exists(cfg)
        print_result(f"Repository Health: {cfg}", "PASS" if cfg_ok else "FAIL", cfg_msg)
        if not cfg_ok:
            all_passed = False

    # 4. Quality Tooling Configurations
    tool_configs = {
        "pyproject.toml": "[tool.ruff]",
        "requirements-dev.txt": "ruff"
    }
    for cfg, search_str in tool_configs.items():
        cfg_ok, cfg_msg = check_file_exists(cfg, search_str)
        print_result(f"Quality Tooling Config: {cfg}", "PASS" if cfg_ok else "FAIL", cfg_msg)
        if not cfg_ok:
            all_passed = False

    # 5. Git Pre-Commit and CI/CD Configs
    ci_configs = {
        ".pre-commit-config.yaml": "repos:",
        ".gitlab-ci.yml": "stages:"
    }
    for cfg, search_str in ci_configs.items():
        cfg_ok, cfg_msg = check_file_exists(cfg, search_str)
        print_result(f"CI/CD and Git Hook: {cfg}", "PASS" if cfg_ok else "FAIL", cfg_msg)
        if not cfg_ok:
            all_passed = False

    # 6. Spec-Kit Files
    specs = [
        ".specify/constitution.md",
        ".specify/templates/spec_template.md",
        ".specify/specs/hand_tracking.md",
        ".specify/specs/face_tracking.md",
        ".specify/specs/body_tracking.md",
        ".specify/specs/gesture_recognition.md",
        ".specify/specs/translation_engine.md",
        ".specify/specs/speech_engine.md",
        ".specify/specs/telemetry_dashboard.md"
    ]
    for spec in specs:
        spec_ok, spec_msg = check_file_exists(spec)
        print_result(f"Spec-Kit Specification: {spec}", "PASS" if spec_ok else "FAIL", spec_msg)
        if not spec_ok:
            all_passed = False

    # 7. Git tag check
    try:
        tag_proc = subprocess.run(["git", "tag"], capture_output=True, text=True, check=True)
        tags = tag_proc.stdout.strip().split("\n")
        if "v1.0.0" in tags:
            print_result("Git Release Tag Check (v1.0.0)", "PASS", "v1.0.0 exists")
        else:
            print_result("Git Release Tag Check (v1.0.0)", "FAIL", "v1.0.0 tag not found in git")
            all_passed = False
    except Exception as e:
        print_result("Git Release Tag Check (v1.0.0)", "FAIL", f"Failed to query git: {str(e)}")
        all_passed = False

    print("\n====================================================")
    if all_passed:
        print("          COMPLIANCE SCORE = 100% (ALL PASSED)      ")
    else:
        print("          COMPLIANCE SCORE < 100% (SOME FAILED)     ")
    print("====================================================")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
