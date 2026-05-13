import json
import os
import subprocess
from typing import Dict, List, Optional

BASELINE_FILE = ".secrets.baseline"

class SentinelEngine:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.baseline_path = os.path.join(self.root_dir, BASELINE_FILE)

    def scan(self, path: Optional[str] = None, staged: bool = False) -> Dict:
        """Runs a scan and returns findings."""
        cmd = ["python3", "-m", "detect_secrets", "scan", "--all-files"]
        
        if staged:
            # For staged files, we use a slightly different approach or filter results
            # For now, let's focus on path-based scanning
            pass

        if path:
            cmd.append(path)
        else:
            cmd.append(self.root_dir)

        # We want to compare against the baseline if it exists
        if os.path.exists(self.baseline_path):
            # detect-secrets has a way to use baseline, but often it's easier to
            # run the scan and then filter ourselves for custom logic/severity
            pass

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            findings = json.loads(result.stdout)
            return self._process_findings(findings)
        except subprocess.CalledProcessError as e:
            return {"error": f"Scan failed: {e.stderr}"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse scanner output"}

    def _process_findings(self, raw_findings: Dict) -> Dict:
        """Filters and adds metadata to findings."""
        # Load baseline to filter out approved secrets
        baseline = self.get_baseline()
        approved_hashes = set()
        if baseline and "results" in baseline:
            for file_path, secrets in baseline["results"].items():
                for secret in secrets:
                    approved_hashes.add(secret.get("hashed_secret"))

        new_results = {}
        results = raw_findings.get("results", {})
        for file_path, secrets in results.items():
            new_secrets = []
            for secret in secrets:
                if secret.get("hashed_secret") not in approved_hashes:
                    # Add severity (placeholder logic)
                    secret["severity"] = self._calculate_severity(secret)
                    new_secrets.append(secret)
            
            if new_secrets:
                new_results[file_path] = new_secrets

        return {
            "results": new_results,
            "summary": {
                "new_secrets_count": sum(len(s) for s in new_results.values()),
                "total_files_scanned": len(results)
            }
        }

    def _calculate_severity(self, secret: Dict) -> str:
        """Simple severity scoring based on plugin type."""
        plugin = secret.get("type", "")
        if "PrivateKey" in plugin:
            return "CRITICAL"
        if "AWS" in plugin or "Github" in plugin:
            return "HIGH"
        return "MEDIUM"

    def get_baseline(self) -> Optional[Dict]:
        if os.path.exists(self.baseline_path):
            with open(self.baseline_path, "r") as f:
                return json.load(f)
        return None

    def initialize_baseline(self):
        """Creates the initial baseline file."""
        cmd = ["python3", "-m", "detect_secrets", "scan", self.root_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        with open(self.baseline_path, "w") as f:
            f.write(result.stdout)

    def approve_finding(self, file_path: str, line_number: int) -> bool:
        """Finds a secret in a file at a specific line and adds it to the baseline."""
        # Perform a fresh scan of the file to get the current secret object
        raw_scan = self.scan(path=file_path)
        findings = raw_scan.get("results", {}).get(file_path, [])
        
        target_secret = None
        for secret in findings:
            if secret.get("line_number") == line_number:
                target_secret = secret
                break
        
        if not target_secret:
            return False

        baseline = self.get_baseline()
        if not baseline:
            self.initialize_baseline()
            baseline = self.get_baseline()

        if file_path not in baseline["results"]:
            baseline["results"][file_path] = []
        
        # Check if already there
        if not any(s["hashed_secret"] == target_secret["hashed_secret"] for s in baseline["results"][file_path]):
            # Add the full secret object (excluding our custom severity)
            secret_to_add = target_secret.copy()
            if "severity" in secret_to_add:
                del secret_to_add["severity"]
            baseline["results"][file_path].append(secret_to_add)
            
            with open(self.baseline_path, "w") as f:
                json.dump(baseline, f, indent=2)
            return True
        
        return False
