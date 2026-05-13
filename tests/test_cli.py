import os
import pytest
from click.testing import CliRunner
from sentinel.sentinel.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_init_baseline(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ['init'])
        assert result.exit_code == 0
        assert "Baseline initialized" in result.output
        assert os.path.exists(".secrets.baseline")

def test_cli_scan_clean(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ['scan'])
        assert result.exit_code == 0
        assert "No new secrets detected" in result.output

def test_cli_scan_detects_secret(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create a file with a secret
        with open("test_secret.py", "w") as f:
            f.write("API_KEY = 'super_secret_key_12345'\n")

        result = runner.invoke(cli, ['scan'])
        assert result.exit_code == 1
        assert "Found 1 new secret" in result.output or "Found 2 new secret" in result.output
        assert "test_secret.py" in result.output

def test_cli_approve_finding(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create a file with a secret
        with open("test_secret.py", "w") as f:
            f.write("API_KEY = 'super_secret_key_12345'\n")

        # Approve it
        result_approve = runner.invoke(cli, ['approve', 'test_secret.py', '1'])
        assert result_approve.exit_code == 0
        assert "Approved finding" in result_approve.output
        
        # Scan should now pass
        result_scan = runner.invoke(cli, ['scan'])
        assert result_scan.exit_code == 0
        assert "No new secrets detected" in result_scan.output
