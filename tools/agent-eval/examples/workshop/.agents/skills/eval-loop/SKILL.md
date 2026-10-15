---
name: eval-loop
description: Runs one agent-eval improvement iteration on the workshop's order support agent. It runs the evaluation without prompts, reads the scores, judge explanations, and AI analysis, writes one hypothesis, makes and commits one change, runs again, and compares the two runs. Use when the user asks to evaluate the agent, explain why a metric fails, improve the agent, or compare runs.
---

# Evaluation loop for the workshop agent

Work in the folder that holds this repository's `AGENTS.md`. Follow the steps in order. Ask the user before steps 2
and 7, because they call Vertex AI and cost money.

## 1. Prepare

1. Activate the environment: `source .venv/bin/activate`.
2. Check the version: `agent-eval --version`. The last line must be `agent-eval v0.2.0`.
3. Check that `.env` exists. Do not print its values.
4. Check the git state: `git status --short`. If `app/` has changes, commit them first.
5. List the existing runs: `ls tests/eval/results/`. Choose a new run ID, for example `baseline` or `v2-<change>`.

## 2. Run the evaluation

```bash
AGENT_EVAL_NO_PAUSES=1 agent-eval run --agent-dir app --run-id <run-id> --no-interact --no-dashboard < /dev/null > /tmp/<run-id>.log 2>&1
```

- The run takes 3 to 6 minutes. It succeeded if the log contains `Pipeline complete!`.
- The **LLM-as-Judge Metrics** table in the log shows the average of each judge and its pass or fail result.
- If it fails, read the end of the log. `RefreshError` or `DefaultCredentialsError`: ask the user to run
  `gcloud auth application-default login`. `429 RESOURCE_EXHAUSTED`: wait a minute and run again with
  `--sim-parallelism 2`. More fixes are in the Troubleshooting section of `README.md`.

## 3. Read the results

Read these files in `tests/eval/results/<run-id>/`:

1. `eval_summary.json`: `overall_summary.llm_based_metrics` (judge averages) and
   `overall_summary.deterministic_metrics` (tokens, cost, latency, tool success).
2. `question_answer_log.md`: for each conversation, the messages, the tool calls with their results, and each judge's
   score and explanation.
3. `gemini_analysis.md`: the AI root cause analysis.

Give the user one table, with one row per conversation: the case, the `general_quality` score, the
`refund_policy_compliance` score, what the agent did (tool calls), and the judge's reason.

## 4. Find the root cause

1. Compare each tool call sequence with the store policy in `AGENTS.md`.
2. Read `app/prompt.py` and `app/agent.py`.
3. Check every claim of `gemini_analysis.md` against the evidence. Quote the judge explanations that support it.

## 5. Write a hypothesis

Use this form, and show it to the user before you change code:

> If <one change>, then <target metric> moves to <value>, and <guardrail metric> stays above <threshold>.

## 6. Make one change and commit it

Common options for this agent:

- Change the instruction in `app/prompt.py` so that the agent looks up the order and checks the policy before any
  refund, and declines orders that do not qualify. `solution/prompt.py` is the reference version.
- Enforce the rule in code (Offload): make `issue_refund` look up the order and return an error when it does not
  qualify.

Make only one change. Then commit it: `git commit -am "<what and why>"`.

## 7. Run again

Repeat step 2 with a new run ID.

## 8. Compare and report

```bash
agent-eval compare tests/eval/results/<new-run-id> tests/eval/results/<baseline-run-id> < /dev/null
```

- The judge rows come first, with a status (Improved, Regressed, Unchanged). The deterministic rows follow.
- `compare` marks any drop larger than 0.001 as Regressed. With five conversations, read the conversations before you
  call a drop a regression.
- Report to the user: the hypothesis, confirmed or not, with the numbers from both runs, and one suggested next step.
