---
name: comment-file
description: Comment one named source file by launching the project code-commenter subagent. Use when the user provides or names a file and asks to add comments, docstrings, or documentation comments to that file. No change to code only comment.
---

# Comment one file

Launch the project `code-commenter` subagent on the one source file the user named. The subagent inserts comments. No change to code only comment.

Read `.cursor/agents/code-commenter.mdc` before launching. Follow that file. If it and this skill disagree, follow the agent file.

## When to run

Run when the user points at one file (path, `@` mention, or the open file) and asks to comment it.

Do not run for a review, a refactor, or a request to explain code without editing. Do not comment a file the user did not name.

## Before launch

1. Resolve the file to an absolute path. If none was given, ask for one path and stop. Do not guess a file.
2. If several paths were given, keep only the first. Tell the user the others were left untouched.
3. Confirm that path exists and is a source file. If it does not exist, stop and say so.
4. Do not comment the file yourself. Resolving the path is the only pre-work.

## Launch

Launch exactly one `code-commenter` subagent with the Task tool:

- `subagent_type`: `code-commenter`
- `run_in_background`: `false` unless the user asked to run it in the background
- `description`: `Comment one file`
- omit `model` so the agent file’s `inherit` setting is kept

`code-commenter` must be an available subagent type. If it is not, stop and say so. Do not substitute another subagent and do not comment the file yourself.

The subagent does not see the chat. Put the path and the limits in the prompt:

```text
Comment only this file. No change to code only comment.

Repository: <absolute workspace path>
File: <absolute path>

Read .cursor/agents/code-commenter.mdc and follow it.

Insert comments only:
- a short docstring on a function, method, or class when the name does not already say what it does
- one inline comment inside a function only at critical database work or a raised exception that is easy to misread

Do not change, reorder, rename, reformat, or delete code. Do not fix bugs. Do not open or comment any other file.

Reply with the file path, each comment added (one line per function or class), what you left uncommented (one line), and any defect you noticed and did not touch.
```

Launch a second subagent only when the user later names another file.

## After the subagent returns

Relay its reply:

- the file path
- each comment added, one line per function or class
- what was left uncommented
- any defect noticed and not touched

Check the diff for that file. A valid edit is an added comment or docstring only. If any other line changed, restore those lines and say what you restored.

If the subagent fails before commenting, retry once with the same prompt. If the second attempt fails, stop and report the short error. Do not keep retrying. Do not comment the file yourself.
