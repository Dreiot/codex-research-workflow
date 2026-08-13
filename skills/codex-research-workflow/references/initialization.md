# Initialization and Migration

The Codex-opened project root, authority root, and exact Git root are one
directory. `--repo` always names that directory. A nested Git repository is an
invalid project layout, not a supported multi-root mode.

## New projects

Run `workflow.py init --repo <repo>` without `--apply` first. The plan must
report the exact target, Git status, branch/history, nested repositories,
remote/GitHub state, proposed authority files, `.gitignore` additions, upload
scope, exclusions, suspected credentials, large files, and blockers.

- Use `main` for a new repository without creating another branch.
- If GitHub is absent, require the user to choose owner, repository name, and
  visibility before creation.
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

Use `workflow.py migrate --repo <repo>` rather than `init`. The migration plan
may add current stable experiment-root and ignore rules while preserving
existing authorities, internal schema markers, Git history, reports, and
project-specific supporting documents.

Migration does not compact authorities, relocate experiments, or delete
artifacts. Those are independent user-authorized transactions. Existing remote
or multi-branch layouts are inspected but never renamed, merged, deleted, or
rewritten automatically.

If the selected project root contains a nested Git repository, stop before
`migrate`. Prepare a separate user-approved root-relocation transaction, preserve
Git history and protected artifacts, and rerun `audit` at the unified root.
