---
name: review-test-gaps
description: Review a provided pytest test file for missed edge cases, untested functionality, and security risks by launching the project code-reviewer subagent. Use when the user provides or names a test file and asks to check missing edge cases, coverage gaps, untested behavior, or security risks in tests.
---

# Review Test Gaps

Launch the project `code-reviewer` subagent on the test file the user provided. The subagent compares that file to the implementation it exercises and reports missing edge cases, missing functionality, and security risks.

Read `.cursor/agents/code-reviewer.mdc` before launching. Follow its Execution Workflow and Output Formatting Requirements. If that file and this skill disagree, follow the agent file.

## When to run

Run when the user points at a test file (path, `@` mention, or the open test file) and asks for missed edge cases, missing functionality, coverage gaps, or security risks in the tests.

Do not run for a general code review, a diff review, or a request to add tests. Those stay with the user unless they also name a test file to audit.

## Before launch

1. Resolve every test file to an absolute path. If none was given, ask for the path and stop. Do not guess a file.
2. Confirm each path exists and is a test module (`test_*.py`, `*_test.py`, or a file under `tests/`).
3. Read the test file only far enough to list what the subagent must open:
   - the test file
   - `tests/conftest.py` when the test imports it
   - route modules, schemas, services, and security modules the tests call or import
4. Do not write the gap analysis yourself. Locating files is the only pre-work.

This repo’s tests live in `quickdesk-backend/tests/`. Route tests call `/api/v1/...` and the handlers live under `quickdesk-backend/app/api/endpoints/`.

## Launch

Launch exactly one `code-reviewer` subagent with the Task tool:

- `subagent_type`: `code-reviewer`
- `run_in_background`: `false` unless the user asked to run it in the background
- `description`: `Review test gaps`
- omit `model` so the agent file’s `inherit` setting is kept

`code-reviewer` must be an available subagent type. If it is not, stop and say so. Do not substitute `bugbot` or `security-review`.

The subagent does not see the chat. Put every path and the review scope in the prompt:

```text
Review only these test files for missed edge cases, untested functionality, and security risks. Read the implementation they exercise and compare behavior to the tests. Do not edit files.

Repository: <absolute workspace path>
Test files:
- <absolute path>

Related implementation and fixtures:
- <absolute path>

Run these three steps, in order:
1. Test Gap Analysis: edge cases, boundary values, and critical paths present in the implementation but absent from the tests.
2. Docs Verification: pytest, FastAPI, SQLAlchemy, Pydantic, and PyJWT usage against current official docs. Flag deprecated or insecure patterns.
3. OWASP Security Audit: authentication bypass, injection, insecure data handling, and broken object level authorization, including cases the tests fail to lock down.

Return findings only in the code-reviewer output format, ordered Critical, High, Medium, Low. Every finding must cite file path and line number. If nothing is missing, say so in one sentence.
```

One subagent covers every test file in the request. Launch a second only when the user asks for separate reviews.

## After the subagent returns

Relay its findings in the agent file’s structure. Do not collapse them into a table and do not drop fields.

### ⚠️ [Priority Level] - [Short Risk/Gap Title]

- **Target File & Location:** `path/to/file.py:line_number`
- **Test Case Category:** [e.g., Security / Missing Edge Case / Integration]
- **The Gap/Risk:** A precise description of the missing test or the OWASP/documentation compliance risk.
- **Official Reference Checklist:** Explicit citation of the standard or official docs rule being breached (e.g., "OWASP A01:2021-Broken Access Control" or "FastAPI Depend Injection Docs").
- **Recommended Action:** Exact code block or test step needed to resolve this risk.

Order is Critical, then High, Medium, Low. If the subagent reports no gaps, say that in one sentence.

If the subagent fails before producing findings, retry once with the same prompt. If the second attempt fails, stop and report the short error. Do not keep retrying.

Do not add tests or edit code unless the user asks for that next step.
