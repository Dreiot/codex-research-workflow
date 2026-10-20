# Initialization and Migration

The Codex-opened project root and authority root are one directory. `--repo`
always names it. If Git exists, its exact root must be the same directory;
nested Git repositories remain an invalid project layout.

## New projects

Run `workflow.py init --repo <project>` without `--apply` first. By default it
plans only local authority files, preserving existing files and scientific
constraints. A plain directory needs neither Git nor a GitHub account; no
repository, commit, remote, upload or `.gitignore` is created for it.

Only after an explicit user request to create repositories:

- `--create-git` enables local Git creation at the project root.
- `--github-repo OWNER/NAME --visibility ...` explicitly enables GitHub creation
  and implies local Git creation. Do not infer this request from “initialize”.

For Git-enabled initialization, the plan additionally reports Git status,
branch/history, nested repositories, remote state, `.gitignore` additions,
exact commit/upload scope, exclusions, suspected credentials, large files and
blockers. The existing protections continue to apply:

- Use `main` for a new repository without creating another branch.
- If GitHub creation is requested, require owner, repository name and visibility;
  otherwise a local-only repository needs no remote.
- If a remote contains history, stop; never overwrite, force-push, or infer a
  merge.
- For a nonempty directory, stage the exact reviewed safe scope, never
  `git add .` blindly.
- Exclude raw/external data, persistent runs, temporary files, large generated
  outputs, caches, credentials, and sensitive material unless explicitly
  reviewed and authorized.

After the user approves the displayed plan, pass its `plan_id` to `--apply`.
Recompute the plan immediately before writing. Any changed target, scope,
history, remote, or safety finding invalidates approval.

## Existing governed projects

Use `workflow.py migrate --repo <project>` rather than `init`. The migration plan
may add current stable experiment-root and ignore rules while preserving
existing authorities, internal schema markers, Git history, reports, and
project-specific supporting documents.

Without Git, migration updates only local files and does not commit, push or
create a repository. Git-dependent history checks and commit/push behavior
apply only to an existing Git repository and its configured remote.

Migration does not compact authorities, relocate experiments, or delete
artifacts. Those are independent user-authorized transactions. Existing remote
or multi-branch layouts are inspected but never renamed, merged, deleted, or
rewritten automatically.

If the selected project root contains a nested Git repository, stop before
`migrate`. Prepare a separate user-approved root-relocation transaction, preserve
Git history and protected artifacts, and rerun `audit` at the unified root.
