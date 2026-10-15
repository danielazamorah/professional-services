# AGENTS.md: agent-eval workshop

Context for coding agents (Antigravity, Claude Code, Codex, Cursor, and others) that work in this folder. Humans: start
with [README.md](README.md).

## What this folder is

A hands-on workshop for [agent-eval](../../README.md). `app/` is a small ADK customer support agent for an electronics
store. Its instruction (`app/prompt.py`) has a deliberate bug: it tells the model to issue refunds right away, so the
agent gives refunds that the store policy does not allow. `tests/eval/` is the evaluation suite that catches the bug.

The workshop goal: run the evaluation, find the root cause, fix the agent, and prove the fix with data.

## Layout

| Path | Purpose |
|---|---|
| `app/agent.py` | Order data, three tools (`lookup_order`, `get_return_policy`, `issue_refund`), and `root_agent` (model `gemini-3.8-flash`) |
| `app/prompt.py` | The agent instruction. The baseline version has the bug. |
| `solution/prompt.py` | The reference fix (instruction only) |
| `tests/eval/dataset.jsonl` | 5 multi-turn test conversations that ADK's user simulator plays |
| `tests/eval/metrics/metric_definitions.json` | `general_quality` (managed rubric, threshold 0.7) and `refund_policy_compliance` (custom LLM judge, threshold 1.0) |
| `tests/eval/eval_config.json` | Created by `agent-eval init`. Do not edit. |
| `tests/eval/results/<run-id>/` | Created by each run (ignored by git) |
| `README.md`, `README.es.md`, `docs/INSTRUCTOR.md` | Guides for attendees and instructors |

## Store policy (ground truth)

A refund is allowed only for a delivered order, delivered 30 days ago or less. Before a refund, the agent must look up
the order and check the return policy.

| Order | Status | Refund allowed |
|---|---|---|
| `ORD-101` | Delivered 5 days ago, $149 | Yes |
| `ORD-202` | Delivered 45 days ago, $199 | No |
| `ORD-303` | In transit, $89 | No |
| `ORD-999` | Does not exist | No |

## Environment

- Python 3.12 virtual environment in `.venv`. Activate it with `source .venv/bin/activate`. To create it:
  `uv venv --python 3.12 && uv pip install -r requirements.txt -e .`
- agent-eval v0.2.0 and ADK are pinned in `requirements.txt`.
- `.env` holds `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global`, and `GOOGLE_GENAI_USE_ENTERPRISE=True`. Never
  print its values and never commit it.
- Credentials come from Application Default Credentials. If a command fails with `RefreshError` or
  `DefaultCredentialsError`, ask the user to run `gcloud auth application-default login`.

## Commands

| Task | Command |
|---|---|
| Run an evaluation (no prompts, 3 to 6 minutes, calls Vertex AI) | `AGENT_EVAL_NO_PAUSES=1 agent-eval run --agent-dir app --run-id <run-id> --no-interact --no-dashboard < /dev/null` |
| Compare two runs (new first) | `agent-eval compare tests/eval/results/<new-run-id> tests/eval/results/<baseline-run-id>` |
| Serve the HTML report of the latest run | `agent-eval report --serve --port 8080`, then open `/report.html` |
| Chat with the agent | `adk run app` |

## Rules

1. Ask the user before you start an evaluation run. Each run calls Vertex AI and costs money.
2. Commit before every run (`git commit -am "<what and why>"`). agent-eval ties each run to the git commit.
3. Use a new, descriptive `--run-id` for every run. Never reuse a run ID.
4. Change one thing per iteration, and write the hypothesis before you change the code.
5. Do not change `tests/eval/` (test conversations, judge, thresholds) to make scores pass, unless the user asks. Do
   not hard-code behavior for specific order IDs in the agent.
6. Do not run `agent-eval init` or `agent-eval setup` without asking. They change files or the Google Cloud project.
7. With five conversations, treat moves of about 0.1 in `general_quality`, and any move in tokens, cost, or latency, as
   noise until you read the conversations. In multi-turn conversations, `general_quality` sees only the customer's
   last message.
8. Workshop mode: when an attendee asks for help, show the evidence first (scores, judge explanations, tool calls).
   Apply `solution/prompt.py` only if they ask for the answer.

## Where the results are

| File (in `tests/eval/results/<run-id>/`) | What it holds |
|---|---|
| `eval_summary.json` | `overall_summary` (judge averages and deterministic metrics), `per_question_summary`, and `git_info` (commit) |
| `question_answer_log.md` | Each conversation: messages, tool calls, deterministic metrics, and each judge's score with its explanation |
| `gemini_analysis.md` | The AI root cause analysis |
| `report.html` | The HTML report (Overview, Per-Question, Iteration History, AI Analysis) |
| `../OPTIMIZATION_LOG.md` | One entry per run, with metric changes |

## Expected results

| Run | `general_quality` | `refund_policy_compliance` |
|---|---|---|
| Baseline | 0.8 to 0.9 (passes) | 0.4 (fails: `ORD-202`, `ORD-303` in transit, and `ORD-101` without a policy check) |
| After the fix in `solution/prompt.py` | about 0.8 (passes) | 1.0 (passes, 5 of 5) |

For a full improvement iteration, follow the `eval-loop` skill in `.agents/skills/eval-loop/SKILL.md`.
