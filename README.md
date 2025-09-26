# RepoPilot

RepoPilot is a local agentic AI system demo for hackathons, built with the MCP Python SDK.

## Structure
- `server.py`: MCP server exposing safe tools for file listing, reading, running tests, and patch creation.
- `agent_client.py`: Agent client that interacts with the server, runs tests, inspects failures, and suggests/apply patches.
- `sample_repo/`: Contains a buggy `calc.py` and a failing pytest test.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the MCP server:
   ```bash
   python server.py
   ```
3. In another terminal, run the agent client:
   ```bash
   python agent_client.py
   ```

## Demo Flow
- The agent lists repo files, runs tests, and if tests fail, inspects the failing test file.
- It then suggests and creates a patch to fix the bug in `calc.py`.
- All actions are sandboxed and safe.

## Notes
- Python 3.10+
- All code is in a single folder for easy demo.
- Ready for LLM integration in the agent client.
mcp[cli]
uvicorn
pytest
gitpython
python-dotenv

