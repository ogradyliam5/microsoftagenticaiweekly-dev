import json
import os
import pathlib
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "pipeline" / "buttondown_draft.py"


class _MockButtondownHandler(BaseHTTPRequestHandler):
    drafts = {}
    next_id = 1

    def log_message(self, *_args):
        return

    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/v1/emails":
            self._json(404, {"detail": "not found"})
            return

        query = parse_qs(parsed.query)
        subject = (query.get("subject") or [""])[0]
        rows = list(self.drafts.values())
        if subject:
            rows = [row for row in rows if row.get("subject", "") == subject]
        self._json(200, {"results": rows})

    def do_POST(self):
        if self.path != "/v1/emails":
            self._json(404, {"detail": "not found"})
            return

        payload = self._read_json()
        draft_id = str(self.next_id)
        type(self).next_id += 1
        row = {"id": draft_id, "absolute_url": f"https://buttondown.test/{draft_id}", **payload}
        type(self).drafts[draft_id] = row
        self._json(201, row)

    def do_PATCH(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/v1/emails/"):
            self._json(404, {"detail": "not found"})
            return
        draft_id = parsed.path.split("/")[-1]
        if draft_id not in self.drafts:
            self._json(404, {"detail": "missing"})
            return

        payload = self._read_json()
        row = {**self.drafts[draft_id], **payload}
        type(self).drafts[draft_id] = row
        self._json(200, row)


class ButtondownDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _MockButtondownHandler.drafts = {}
        _MockButtondownHandler.next_id = 1
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _MockButtondownHandler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        _MockButtondownHandler.drafts = {}
        _MockButtondownHandler.next_id = 1

    def _run(self, issue_id, subject, body_file, state_file):
        env = os.environ.copy()
        env["BUTTONDOWN_API_KEY"] = "test-token"
        env["BUTTONDOWN_API_BASE_URL"] = f"http://127.0.0.1:{self.port}/v1"
        env["BUTTONDOWN_DRAFT_STATE_PATH"] = str(state_file)
        return subprocess.run(
            [
                os.sys.executable,
                str(SCRIPT),
                "--issue-id",
                issue_id,
                "--subject",
                subject,
                "--body-file",
                str(body_file),
            ],
            cwd=str(ROOT),
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_create_then_update_is_idempotent(self):
        issue_id = "2099-01"
        subject = "Microsoft Agentic AI Weekly - Issue 2099-01"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            state_file = tmp_path / "buttondown_drafts.json"
            body_file = tmp_path / "draft.md"

            body_file.write_text("first body", encoding="utf-8")
            first = self._run(issue_id, subject, body_file, state_file)
            self.assertEqual(first.returncode, 0, first.stderr)

            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertIn(issue_id, state)
            self.assertEqual(state[issue_id]["draft_id"], "1")
            self.assertEqual(state[issue_id]["action"], "created")

            body_file.write_text("second body", encoding="utf-8")
            second = self._run(issue_id, subject, body_file, state_file)
            self.assertEqual(second.returncode, 0, second.stderr)

            state_after = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(state_after[issue_id]["draft_id"], "1")
            self.assertEqual(state_after[issue_id]["action"], "updated")
            self.assertEqual(_MockButtondownHandler.drafts["1"]["body"], "second body")
            self.assertEqual(len(_MockButtondownHandler.drafts), 1)

    def test_recovers_when_stored_draft_id_is_stale(self):
        issue_id = "2099-02"
        subject = "Microsoft Agentic AI Weekly - Issue 2099-02"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            state_file = tmp_path / "buttondown_drafts.json"
            body_file = tmp_path / "draft.md"

            body_file.write_text("initial", encoding="utf-8")
            created = self._run(issue_id, subject, body_file, state_file)
            self.assertEqual(created.returncode, 0, created.stderr)

            state = json.loads(state_file.read_text(encoding="utf-8"))
            state[issue_id]["draft_id"] = "999"
            state_file.write_text(json.dumps(state), encoding="utf-8")

            body_file.write_text("updated after stale id", encoding="utf-8")
            recovered = self._run(issue_id, subject, body_file, state_file)
            self.assertEqual(recovered.returncode, 0, recovered.stderr)

            state_after = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(state_after[issue_id]["draft_id"], "1")
            self.assertEqual(state_after[issue_id]["action"], "recovered_by_subject")
            self.assertEqual(_MockButtondownHandler.drafts["1"]["body"], "updated after stale id")


if __name__ == "__main__":
    unittest.main()
