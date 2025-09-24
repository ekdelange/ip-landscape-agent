# How to Run the Agentic System (VS Code)

## Option A — Copilot Chat
1) Open `prompts/orchestrator.md` and paste to Copilot Chat.
2) Feed the per-agent prompts in sequence; ensure paths match.
3) After each checkpoint, ask Copilot to append a summary to `runbooks/execution_log.md`.

## Option B — ChatGPT in browser
- Paste prompt content; when a tool can’t write files, ask it to emit file contents. Copy-paste into VS Code accordingly.

**Tips**: One agent per chat thread. Ask for assumptions & gaps at the end of each step.
