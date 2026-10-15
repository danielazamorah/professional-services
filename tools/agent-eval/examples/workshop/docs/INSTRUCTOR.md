# Instructor notes

Notes for running this repository as a live, hands-on workshop (about 60 minutes).

## Before the workshop

- [ ] **Decide how attendees get a Google Cloud project.** Each attendee needs a project with billing enabled (or
      credits) and the Owner or Editor role, because `agent-eval setup` enables APIs and adds one IAM binding.
- [ ] **If you provision the projects yourself**, do the setup ahead of time so attendees only need the Vertex AI User
      role (`roles/aiplatform.user`):
      ```bash
      PROJECT_ID=your-project-id
      PN=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
      gcloud services enable serviceusage.googleapis.com cloudresourcemanager.googleapis.com \
          aiplatform.googleapis.com iam.googleapis.com --project "$PROJECT_ID"
      gcloud projects add-iam-policy-binding "$PROJECT_ID" \
          --member="serviceAccount:service-$PN@gcp-sa-aiplatform.iam.gserviceaccount.com" \
          --role="roles/aiplatform.serviceAgent"
      ```
      If the binding fails because the service agent does not exist yet, make one Vertex AI call in the project first
      (or run `gcloud beta services identity create --service=aiplatform.googleapis.com --project "$PROJECT_ID"`).
- [ ] **Shared project?** Many attendees in one project share one Vertex AI quota. Ask them to add
      `--sim-parallelism 2` to `agent-eval run`, or give each attendee a separate project.
- [ ] **Run the whole guide once in Cloud Shell, with a fresh project,** the day before. It takes about 25 minutes.
- [ ] Put the folder URL (and a QR code) on a slide. Attendees only need the clone commands in Step 1 of the README.

## Suggested agenda (60 minutes)

| Time | What | README steps |
|---|---|---|
| 0:00 to 0:10 | Why evaluate agents. What agent-eval is. The bug: "friendly, fast, and gives away refunds". | (slides) |
| 0:10 to 0:25 | Setup. This is where most problems happen: walk the room. | Steps 1 to 3 |
| 0:25 to 0:30 | The agent, the five conversations, and the two metrics | Steps 4 and 5 |
| 0:30 to 0:38 | Baseline run. While it runs (3 to 6 minutes), explain the custom judge. | Step 6 |
| 0:38 to 0:45 | The report: "everything is green, except what matters". Root cause. | Steps 7 and 8 |
| 0:45 to 0:55 | The fix (one prompt change), second run, comparison, run history | Steps 9 and 10 |
| 0:55 to 1:00 | Lessons and challenges | Challenges |

## What good results look like

| Run | `general_quality` | `refund_policy_compliance` |
|---|---|---|
| Baseline | 0.8 to 0.9, passes (threshold 0.7) | 0.4, fails (threshold 1.0): only `order_status` and `unknown_order` pass |
| After the fix | about 0.8, passes | 1.0, passes: 5 of 5 |

- One run takes 3 to 6 minutes (on 2026-10-15: 3.6 minutes for the baseline, 6 minutes for the second run). The whole
  workshop costs well under US$1 per attendee.
- `compare` can mark `general_quality` as **Regressed** even when the agent is better. With five conversations, one
  misjudged reply moves the average by 0.1. This is a good teaching moment: read the conversation before you act.
- Tokens, cost, and latency move in both directions between identical runs. Do not present them as wins.

## Key messages

1. **Evaluate what matters.** The generic metric passed an agent that gave away $199 outside the return window.
2. **Judges must see what the agent did.** The refund judge reads every tool call, not only the final reply.
3. **Data, not vibes.** Each change is a hypothesis. Commit it, run, compare, and read the evidence.
4. **The tools were there; the agent did not use them correctly.** The fix is one prompt change here, but the same
   loop works for callbacks, new tools, other models, or a new architecture.

## Fast fixes for the room

| Problem | Fix |
|---|---|
| Credentials missing or expired | `gcloud auth application-default login` |
| `403` or "API not enabled" | Owner or Editor role, then `agent-eval setup --no-asp` again |
| `agent-eval run` hangs at the start | `adk telemetry disable`, then run again |
| `429 RESOURCE_EXHAUSTED` | Add `--sim-parallelism 2`, wait a minute, run again |
| `git commit` fails | `git config user.name "..."` and `git config user.email "..."` |

The full table is in the [README troubleshooting section](../README.md#troubleshooting).

## Live demo with a coding agent

The folder has `AGENTS.md` and an `eval-loop` skill, so a coding agent can run the loop on stage. See
[Use a coding agent](../README.md#use-a-coding-agent-optional) in the README.

- Use the Antigravity CLI (`agy`), the public product, so attendees can repeat what they see.
- Use a clean environment, such as Cloud Shell, the same place where attendees work. On your own machine, `agy` also
  loads global rules from `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`,
  `~/.gemini/config/GEMINI.md`, and `~/.gemini/config/rules/*.md`. Personal notes in those files can show up on
  screen.
- Start `agy` inside the workshop folder, and type `/skills` to show that `eval-loop` is loaded.
- One agent-driven iteration takes about 10 minutes (two runs of 3 to 6 minutes). Start the baseline before you
  explain the judge.

## Recovery shortcuts

- **An attendee is behind:** `cp solution/prompt.py app/prompt.py && git commit -am "Fix"` applies the fix.
- **Run without prompts:** `AGENT_EVAL_NO_PAUSES=1 agent-eval run --agent-dir app --run-id baseline --no-interact --no-dashboard`
- **Nothing runs in the room (for example, no billing):** walk through the screenshots in `docs/img/` and the expected
  results above, and let attendees run the guide at home.
