# Workflow Patterns

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. It is often helpful to give Manus an overview of the process towards the beginning of SKILL.md:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

## Stage Gates for Multi-Phase Work

For workflows where doing the right thing in the wrong order causes errors, define each phase with explicit gates rather than relying on narrative wording alone.

A useful pattern is:

```markdown
| Stage | Entry Condition | Completion Condition | Forbidden Actions |
| --- | --- | --- | --- |
| Initial pass | Input files A and B exist | All batch review files exist | Do not create audit files |
| Audit | Entire batch initial pass complete | Audit file for current unit exists | Do not modify final output data |
| Revision | Audit + issue inventory for current unit exist | Validation passes | Do not skip issue inventory |
```

This makes it much harder for another Manus instance to "reason its way" into an invalid stage transition.

## Priority Resolution Rules

When a workflow can be influenced by multiple sources of truth, encode a precedence rule in the skill.

Example:

```markdown
If instructions conflict, resolve them in this order:
1. User's latest explicit instruction
2. Current SKILL.md rules
3. Verified current-state artifacts for the active work unit
4. Inherited summaries, older plans, or stale notes
```

Without an explicit rule, inherited summaries and partial history can silently override the intended workflow.

## Resume Protocols

Interrupted tasks often fail not because the workflow is unknown, but because the current state is reconstructed loosely. For long or multi-stage tasks, require a resume checkpoint before taking action.

Example:

```markdown
Before resuming after interruption, restate:
- current batch
- current stage
- current work unit
- required prerequisite files
- forbidden next actions

If any item is unclear, stop and rebuild the plan before proceeding.
```

## Conditional Workflows

For tasks with branching logic, guide Manus through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```