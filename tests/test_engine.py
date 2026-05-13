import os
import json
import pytest
from sentinel.sentinel.engine import SentinelEngine

@pytest.fixture
def temp_workspace(tmp_path):
    """Provides a temporary directory acting as a workspace."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    return str(workspace)

def test_engine_initialization(temp_workspace):
    engine = SentinelEngine(root_dir=temp_workspace)
    assert engine.root_dir == temp_workspace
    assert engine.baseline_path == os.path.join(temp_workspace, ".secrets.baseline")

def test_scan_detects_custom_pattern(temp_workspace):
    engine = SentinelEngine(root_dir=temp_workspace)
    
    # Create a file with a low-entropy custom pattern that detect-secrets misses
    test_file = os.path.join(temp_workspace, "config.py")
    with open(test_file, "w") as f:
        f.write("API_KEY = 'simple_key_123'\n")
        f.write("NORMAL_VAR = 'hello_world'\n")
        f.write("PASSWORD = 'my_super_secret_password'\n")

    findings = engine.scan()
    results = findings.get("results", {})
    
    # Assert custom patterns were found
    assert "config.py" in results
    assert len(results["config.py"]) == 2
    
    types_found = [s["type"] for s in results["config.py"]]
    assert any("Secret Keyword" in t for t in types_found)

def test_scan_detects_high_entropy(temp_workspace):
    engine = SentinelEngine(root_dir=temp_workspace)
    
    # Create a file with high entropy string (AWS Key format)
    test_file = os.path.join(temp_workspace, "aws_config.py")
    with open(test_file, "w") as f:
        f.write("aws_secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'\n")

    findings = engine.scan()
    results = findings.get("results", {})
    print(f"DEBUG FINDINGS: {findings}")
    
    assert "aws_config.py" in results
    assert len(results["aws_config.py"]) > 0

def test_approve_finding_workflow(temp_workspace):
    engine = SentinelEngine(root_dir=temp_workspace)
    
    test_file = os.path.join(temp_workspace, "config.py")
    with open(test_file, "w") as f:
        f.write("API_KEY = 'simple_key_123'\n")

    # Step 1: Scan should find it
    initial_findings = engine.scan()
    assert initial_findings["summary"]["new_secrets_count"] == 1

    # Step 2: Approve the finding on line 1
    # We pass the relative path for approval, as that's how it's keyed in the results
    assert engine.approve_finding("config.py", 1) == True

    # Step 3: Scan should no longer report it as a "new secret"
    post_approval_findings = engine.scan()
    assert post_approval_findings["summary"]["new_secrets_count"] == 0

    # Step 4: Baseline file should exist and contain the hash
    assert os.path.exists(engine.baseline_path)
    with open(engine.baseline_path, "r") as f:
        baseline_data = json.load(f)
        assert "config.py" in baseline_data["results"]
        assert len(baseline_data["results"]["config.py"]) == 1
