import json
import os
import subprocess
import re
import hashlib
from typing import Dict, List, Optional

BASELINE_FILE = ".secrets.baseline"

# Custom regex for common sensitive keywords
SENSITIVE_PATTERNS = [
    re.compile(r'(?i)(api_key|password|secret|token|credential|auth_key|private_key)\s*[=:]\s*["\']?([a-zA-Z0-9_\-\.\/]{4,})["\']?'),
]

class SentinelEngine:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.baseline_path = os.path.join(self.root_dir, BASELINE_FILE)

    def scan(self, path: Optional[str] = None, staged: bool = False) -> Dict:
        """Runs both detect-secrets and custom regex scans."""
        # 1. Run detect-secrets
        ds_cmd = ["python3", "-m", "detect_secrets", "scan", "--all-files", "--exclude-files", r".*secrets\.baseline", "--exclude-files", r"^tests/.*"]
        if path:
            ds_cmd.append(path)
        else:
            ds_cmd.append(".")

        try:
            result = subprocess.run(ds_cmd, capture_output=True, text=True, check=True, cwd=self.root_dir)
            ds_raw = json.loads(result.stdout)
            
            # Use paths exactly as provided by detect-secrets, but ensure they are relative 
            # to root_dir if they are absolute. Usually detect-secrets returns relative paths.
            normalized_results = {}
            for fp, secrets in ds_raw.get("results", {}).items():
                if os.path.isabs(fp) and fp.startswith(self.root_dir):
                    rel_fp = os.path.relpath(fp, self.root_dir)
                    normalized_results[rel_fp] = secrets
                else:
                    normalized_results[fp] = secrets
                    
            findings = {"results": normalized_results}
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: detect-secrets failed with {e.returncode}: {e.stderr}")
            findings = {"results": {}}
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse failed: {e}")
            findings = {"results": {}}

        # 2. Run Custom Regex Scan
        custom_findings = self._custom_regex_scan(path)
        
        # 3. Merge Results
        merged_results = self._merge_findings(findings.get("results", {}), custom_findings)
        
        return self._process_findings({"results": merged_results})

    def _custom_regex_scan(self, target_path: Optional[str] = None) -> Dict:
        """Scans files for custom sensitive patterns."""
        results = {}
        files_to_scan = []

        if target_path:
            # Handle absolute path if provided
            abs_target = os.path.abspath(target_path)
            if os.path.isfile(abs_target):
                files_to_scan = [abs_target]
            else:
                for root, _, files in os.walk(abs_target):
                    for f in files:
                        files_to_scan.append(os.path.join(root, f))
        else:
            for root, dirs, files in os.walk(self.root_dir):
                if ".git" in root or "__pycache__" in root or "sentinel" in root or "tests" in root:
                    continue
                for f in files:
                    files_to_scan.append(os.path.join(root, f))

        for file_path in files_to_scan:
            # Skip binary files, baseline, and git files
            if any(ext in file_path for ext in [".png", ".jpg", ".exe", ".pyc", "secrets.baseline", ".git/"]):
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in SENSITIVE_PATTERNS:
                            match = pattern.search(line)
                            if match:
                                keyword = match.group(1)
                                value = match.group(2)
                                
                                # Ignore if value is a placeholder or very short
                                if "example" in value.lower() or len(value) < 6:
                                    continue

                                rel_path = os.path.relpath(file_path, self.root_dir)
                                if rel_path not in results:
                                    results[rel_path] = []
                                
                                # Create a hashed secret for baseline compatibility
                                hashed_val = hashlib.sha1(value.encode()).hexdigest()
                                results[rel_path].append({
                                    "type": f"Custom Pattern ({keyword})",
                                    "filename": rel_path,
                                    "hashed_secret": hashed_val,
                                    "line_number": line_num,
                                    "is_custom": True
                                })
            except Exception:
                continue
        
        return results

    def _merge_findings(self, ds_results: Dict, custom_results: Dict) -> Dict:
        """Merges results, avoiding exact line duplicates."""
        merged = ds_results.copy()
        for file_path, findings in custom_results.items():
            if file_path not in merged:
                merged[file_path] = findings
            else:
                existing_lines = {f.get("line_number") for f in merged[file_path]}
                for f in findings:
                    if f.get("line_number") not in existing_lines:
                        merged[file_path].append(f)
        return merged

    def _process_findings(self, raw_findings: Dict) -> Dict:
        """Filters against baseline and adds severity."""
        baseline = self.get_baseline()
        approved_hashes = set()
        if baseline and "results" in baseline:
            for secrets in baseline["results"].values():
                for secret in secrets:
                    approved_hashes.add(secret.get("hashed_secret"))

        new_results = {}
        for file_path, secrets in raw_findings.get("results", {}).items():
            new_secrets = []
            for secret in secrets:
                if secret.get("hashed_secret") not in approved_hashes:
                    secret["severity"] = self._calculate_severity(secret)
                    new_secrets.append(secret)
            
            if new_secrets:
                new_results[file_path] = new_secrets

        return {
            "results": new_results,
            "summary": {
                "new_secrets_count": sum(len(s) for s in new_results.values()),
                "total_files_scanned": len(raw_findings.get("results", {}))
            }
        }

    def _calculate_severity(self, secret: Dict) -> str:
        plugin = secret.get("type", "").lower()
        if "privatekey" in plugin or "password" in plugin:
            return "CRITICAL"
        if "aws" in plugin or "github" in plugin or "token" in plugin:
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
        """Adds a specific finding to the baseline."""
        raw_scan = self.scan(path=file_path)
        findings = raw_scan.get("results", {}).get(file_path, [])
        
        target_secret = None
        for secret in findings:
            if secret.get("line_number") == line_number:
                target_secret = secret
                break
        
        if not target_secret:
            return False

        baseline = self.get_baseline() or {"results": {}, "version": "1.0.0"}
        
        if file_path not in baseline["results"]:
            baseline["results"][file_path] = []
        
        if not any(s["hashed_secret"] == target_secret["hashed_secret"] for s in baseline["results"][file_path]):
            secret_to_add = target_secret.copy()
            if "severity" in secret_to_add:
                del secret_to_add["severity"]
            baseline["results"][file_path].append(secret_to_add)
            
            with open(self.baseline_path, "w") as f:
                json.dump(baseline, f, indent=2)
            return True
        
        return False
