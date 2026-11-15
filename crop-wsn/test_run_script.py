"""Static checks for the reproducible local/CI simulation runner."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"inet-radio"/"run.sh"

class RunnerScriptTests(unittest.TestCase):
    def test_shell_script_has_valid_continuations(self):
        self.assertTrue(SCRIPT.is_file())
        text=SCRIPT.read_text(encoding="utf-8")
        for number,line in enumerate(text.splitlines(),1):
            self.assertFalse(line.endswith("\\\\"), f"line {number}: double backslash breaks shell continuation")

    def test_range_boundary_experiments_are_wired(self):
        text=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('for distance in 49 50 51; do',text)
        self.assertIn('python3 verify_range.py',text)
        self.assertIn('python3 verify_telemetry.py',text)
        self.assertIn('--sim-time-limit=930s',text)

if __name__=="__main__": unittest.main()
