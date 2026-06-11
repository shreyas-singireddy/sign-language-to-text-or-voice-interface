import json
import os
import subprocess
import sys


def check_file_exists(filepath, search_str=None):
    if not os.path.exists(filepath):
        return False, "File not found"
    if search_str:
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                if search_str not in content:
                    return False, f"Missing expected pattern: {search_str}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    return True, "OK"


def main():
    print("====================================================")
    print("      SIGNBRIDGE AI COMPLIANCE STATUS VALIDATOR     ")
    print("====================================================\n")

    results = []

    # 1. License Check
    lic_ok, lic_msg = check_file_exists("LICENSE", "GNU Affero General Public License")
    results.append(
        {
            "Requirement": "GNU AGPLv3 License",
            "File": "LICENSE",
            "Evidence": lic_msg,
            "Status": "PASS" if lic_ok else "FAIL",
            "Expected Compliance Impact": "100% License compliance",
        }
    )

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
        "SECURITY_AUDIT.md": "Security Audit & Threat Modeling",
        "VERSIONING.md": "SignBridge AI Versioning Policy",
        "CONVENTIONAL_COMMITS.md": "Conventional Commits Guidelines",
    }
    for doc_file, search_str in docs.items():
        doc_ok, doc_msg = check_file_exists(doc_file, search_str)
        results.append(
            {
                "Requirement": f"Documentation: {doc_file}",
                "File": doc_file,
                "Evidence": doc_msg,
                "Status": "PASS" if doc_ok else "FAIL",
                "Expected Compliance Impact": "100% Documentation coverage",
            }
        )

    # 3. Repository Health Configurations
    health_configs = [
        ".editorconfig",
        ".env.example",
        ".dockerignore",
        "Dockerfile",
        "backend/.dockerignore",
        "frontend/.dockerignore",
        "backend/Dockerfile",
        "frontend/Dockerfile",
    ]
    for cfg in health_configs:
        cfg_ok, cfg_msg = check_file_exists(cfg)
        results.append(
            {
                "Requirement": f"Repository Health: {cfg}",
                "File": cfg,
                "Evidence": cfg_msg,
                "Status": "PASS" if cfg_ok else "FAIL",
                "Expected Compliance Impact": "100% Repository health config",
            }
        )

    # 4. Quality Tooling Configurations
    tool_configs = {
        "pyproject.toml": "[tool.ruff]",
        "requirements-dev.txt": "pylint",
        "cliff.toml": "[changelog]",
    }
    for cfg, search_str in tool_configs.items():
        cfg_ok, cfg_msg = check_file_exists(cfg, search_str)
        results.append(
            {
                "Requirement": f"Quality Tooling Config: {cfg}",
                "File": cfg,
                "Evidence": cfg_msg,
                "Status": "PASS" if cfg_ok else "FAIL",
                "Expected Compliance Impact": "100% Tooling config coverage",
            }
        )

    # 5. Git Pre-Commit and CI/CD Configs
    ci_configs = {".pre-commit-config.yaml": "repos:", ".gitlab-ci.yml": "stages:"}
    for cfg, search_str in ci_configs.items():
        cfg_ok, cfg_msg = check_file_exists(cfg, search_str)
        results.append(
            {
                "Requirement": f"CI/CD and Git Hook: {cfg}",
                "File": cfg,
                "Evidence": cfg_msg,
                "Status": "PASS" if cfg_ok else "FAIL",
                "Expected Compliance Impact": "100% Pre-commit/CI automation",
            }
        )

    # 6. Spec-Kit Files
    specs = [
        ".specify/constitution.md",
        ".specify/templates/spec_template.md",
        ".specify/specs/hand_tracking.md",
        ".specify/specs/face_tracking.md",
        ".specify/specs/body_tracking.md",
        ".specify/specs/gesture_recognition.md",
        ".specify/specs/live_translation.md",
        ".specify/specs/speech_engine.md",
        ".specify/specs/telemetry_dashboard.md",
    ]
    for spec in specs:
        spec_ok, spec_msg = check_file_exists(spec)
        results.append(
            {
                "Requirement": f"Spec-Kit: {spec}",
                "File": spec,
                "Evidence": spec_msg,
                "Status": "PASS" if spec_ok else "FAIL",
                "Expected Compliance Impact": "100% Spec-Kit coverage",
            }
        )

    # 7. Git tag check
    try:
        tag_proc = subprocess.run(
            ["git", "tag"], capture_output=True, text=True, check=True
        )
        tags = tag_proc.stdout.strip().split("\n")
        if "v1.0.0" in tags:
            tag_ok, tag_msg = True, "v1.0.0 exists"
        else:
            tag_ok, tag_msg = False, "v1.0.0 tag not found in git tag"
    except Exception as e:
        tag_ok, tag_msg = False, f"Failed to query git: {str(e)}"

    results.append(
        {
            "Requirement": "Git Release Tag Check (v1.0.0)",
            "File": ".git",
            "Evidence": tag_msg,
            "Status": "PASS" if tag_ok else "FAIL",
            "Expected Compliance Impact": "100% Git tagging compliance",
        }
    )

    # Write status to json
    status_file = "COMPLIANCE_STATUS.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Generated {status_file}")

    # Generate Markdown Report
    report_file = "FINAL_COMPLIANCE_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# SignBridge AI — Final Compliance Audit Report\n\n")
        f.write(
            "| Requirement | File | Evidence | Status | Pass/Fail | Expected Compliance Impact |\n"
        )
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for res in results:
            pf = "🟢 PASS" if res["Status"] == "PASS" else "🔴 FAIL"
            f.write(
                f"| {res['Requirement']} | `{res['File']}` | {res['Evidence']} | {res['Status']} | {pf} | {res['Expected Compliance Impact']} |\n"
            )
    print(f"Generated {report_file}")

    # Print summary console output
    all_passed = all(res["Status"] == "PASS" for res in results)
    print("\n====================================================")
    if all_passed:
        print("          COMPLIANCE SCORE = 100% (ALL PASSED)      ")
    else:
        print("          COMPLIANCE SCORE < 100% (SOME FAILED)     ")
    print("====================================================")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
