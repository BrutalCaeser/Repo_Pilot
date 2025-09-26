# server.py
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
from typing import List

from mcp.server.fastmcp import FastMCP

print("Starting RepoPilot server...")

# Name the server (shows up for clients)
mcp = FastMCP("repo-pilot")

REPO_ROOT = pathlib.Path(__file__).parent / "sample_repo"
print(f"Repository root: {REPO_ROOT}")

def _safe_path(base: pathlib.Path, rel: str) -> pathlib.Path:
    p = (base / rel).resolve()
    base_res = base.resolve()
    if p == base_res or base_res in p.parents:
        return p
    raise ValueError("path outside allowed repo")

# TOOL: list files
@mcp.tool()
def list_files(path: str = ".") -> List[str]:
    print(f"Listing files in: {path}")
    p = _safe_path(REPO_ROOT, path)
    files = []
    for root, _dirs, filenames in os.walk(p):
        for f in filenames:
            rel = os.path.relpath(os.path.join(root, f), REPO_ROOT)
            files.append(rel)
            if len(files) >= 2000:
                return files
    print(f"Found {len(files)} files")
    return files

# TOOL: read file (size-limited)
@mcp.tool()
def read_file(path: str) -> str:
    print(f"Reading file: {path}")
    p = _safe_path(REPO_ROOT, path)
    size = p.stat().st_size
    if size > 200 * 1024:
        return f"[file too large: {size} bytes]"
    return p.read_text(errors="replace")

# TOOL: run tests in a temp copy (timeout)
@mcp.tool()
def run_tests(timeout_seconds: int = 8) -> dict:
    print("Running tests...")
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copytree(REPO_ROOT, os.path.join(tmpdir, "repo"), dirs_exist_ok=True)
        cwd = os.path.join(tmpdir, "repo")
        start = time.time()
        proc = subprocess.run(
            ["pytest", "-q"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        elapsed = time.time() - start
        result = {
            "success": proc.returncode == 0,
            "rc": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "elapsed": elapsed
        }
        print(f"Tests finished: success={result['success']}")
        return result
    except subprocess.TimeoutExpired:
        print("Tests timed out")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# TOOL: create a patch file (write-only; no git push)
@mcp.tool()
def create_patch(patch_text: str, patch_name: str = "fix.patch") -> str:
    print(f"Creating patch: {patch_name}")
    out = pathlib.Path(tempfile.gettempdir()) / patch_name
    out.write_text(patch_text, encoding="utf-8")
    return str(out)

if __name__ == "__main__":
    try:
        print("Starting MCP server on http://127.0.0.1:8000/mcp")
        # Run with a streamable-HTTP transport (simplest demo)
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Server error: {str(e)}")
        raise
