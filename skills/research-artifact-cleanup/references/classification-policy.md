# Classification Policy

Every item uses exactly one classification:

| Classification | Meaning | Allowed action |
|---|---|---|
| `keep_formal_evidence` | Supports a frozen evaluation, accepted result, review, or paper claim | keep or relocate |
| `keep_negative_evidence` | Material failure or null result that constrains decisions or claims | keep or relocate |
| `keep_active` | Used by the current direction, open Gate, or reproducibility path | keep or relocate |
| `delete_reproducible` | Duplicate/generated output reproducible from retained code, config, manifest, and data IDs | delete |
| `delete_technical_failure` | Output from a setup, crash, corrupt, or otherwise scientifically uninterpretable run | delete |
| `unknown` | Evidence role or reproducibility is unresolved | keep only |

Classification uses repository evidence and explicit user decisions. File age, size, ignored status, folder naming, or apparent duplication is never sufficient by itself. Preserve enough reports, metrics, manifests, negative results, and code/config identity for Browser Work to review the result and choose the next direction.

Inventory starts at the exact project/Git root and includes ignored local
artifacts, not only tracked files or the experiment directory. It records paths,
counts, byte sizes, modification metadata, tracked/ignored status, and tracked
references. It does not load large run contents into model context or read raw
datasets to infer a classification.

Tracked `.gitignore` declarations are ignore metadata, not artifact references;
all other live tracked references remain deletion blockers.

`delete_reproducible` requires retained reproducibility inputs. `delete_technical_failure` requires evidence that the output cannot support a scientific conclusion; a scientifically meaningful negative result belongs in `keep_negative_evidence`.
