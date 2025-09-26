# agent_client.py
import asyncio
import json
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

MCP_URL = "http://127.0.0.1:8000/mcp"

async def run_agent():
    async with streamablehttp_client(MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            # 1) list files
            lf_res = await session.call_tool("list_files", arguments={"path": "."})

            # Handle different response formats
            files = None
            if hasattr(lf_res, 'structuredContent'):
                files = lf_res.structuredContent
            else:
                content_text = "".join([c.text for c in lf_res.content if getattr(c, "text", None)])
                try:
                    files = json.loads(content_text)
                except:
                    files = content_text

            print("--- repo files (sample) ---")
            file_list = []
            if isinstance(files, list):
                file_list = files
            elif isinstance(files, str):
                file_list = [l.strip() for l in files.splitlines() if l.strip()]
            elif isinstance(files, dict) and 'files' in files:
                file_list = files['files']

            if file_list:
                print("\n".join(file_list[:30]))
            else:
                print("No files found")

            # 2) run tests
            tr = await session.call_tool("run_tests", arguments={"timeout_seconds": 8})
            try:
                result_text = "".join([c.text for c in tr.content if getattr(c, "text", None)])
                result_obj = json.loads(result_text)
            except:
                result_obj = tr.structuredContent if getattr(tr, "structuredContent", None) else tr
            print("run_tests ->", result_obj)

            # 3) if tests fail, inspect likely test file
            if not (result_obj.get("success") if isinstance(result_obj, dict) else False):
                test_file = next((f for f in file_list if f.startswith("tests") or f.startswith("test_") or "/tests/" in f), None)
                if test_file:
                    content_res = await session.call_tool("read_file", arguments={"path": test_file})
                    content = "".join([c.text for c in content_res.content if getattr(c, "text", None)])
                    print(f"--- {test_file} preview ---\n{content[:2000]}")

                    # 4) Suggest/apply a patch (hardcoded for demo)
                    patch_text = """--- sample_repo/calc.py\n+++ sample_repo/calc.py\n@@ -1,4 +1,4 @@\n-def add(a, b):\n-    # intentionally wrong: returns subtraction to create a failing test\n-    return a - b\n+def add(a, b):\n+    return a + b\n"""
                    patch_res = await session.call_tool("create_patch", arguments={"patch_text": patch_text, "patch_name": "fix.patch"})
                    patch_path = patch_res.structuredContent if getattr(patch_res, "structuredContent", None) else patch_res
                    print(f"Patch created at: {patch_path}")

if __name__ == "__main__":
    asyncio.run(run_agent())
