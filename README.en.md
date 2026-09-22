# Agent Skills

[简体中文](README.md)

A focused collection of agent skills for project collaboration, knowledge management, and research workflows.

## Skills

| Skill | Description |
| --- | --- |
| [`handoff-project`](skills/handoff-project/) | Preserve, transfer, and resume project state through relays, checkpoints, closeouts, and recovery. |
| [`visual-explain`](skills/visual-explain/) | Choose the smallest sufficient visual representation for relationships, processes, comparisons, and state changes. |
| [`markdown-metadata`](skills/markdown-metadata/) | Define lean, routable, traceable, and maintainable metadata contracts for Markdown documents. |
| [`zotero-library-manager`](skills/zotero-library-manager/) | Manage local attachments and collection membership in Zotero Desktop with preview and post-write verification. |
| [`obsidian-lark-sync`](skills/obsidian-lark-sync/) | Synchronize local Markdown or Obsidian notes with Lark documents while handling versions, media, comments, and format differences. |

## Skill Details

### `handoff-project`

Treats a project handoff as a recoverable worksite rather than a chat summary. It routes work through four modes—relay, checkpoint, closeout, and resume—and records the actual stopping point, verification boundary, remaining work, and next action.

Use it when you need to:

- incorporate another agent's output into the current task;
- pause unfinished work and preserve enough context for a later session;
- close out a completed stage and reconcile project knowledge and status;
- resume from an existing handoff and verify it against the current project state.

### `visual-explain`

Determines whether a topic benefits from visual explanation and selects the least complex format that still communicates the key idea. It can route between prose, tables, flows, structural diagrams, charts, deterministic rendering, and explanatory imagery while preserving exact data and source evidence.

Use it when you need to:

- explain a process, hierarchy, dependency, or state transition;
- compare several objects or reveal an important difference in data;
- annotate visual evidence or turn an abstract concept into a clearer view;
- decide whether interaction is genuinely useful instead of defaulting to a complex graphic.

### `markdown-metadata`

Treats Markdown frontmatter as a minimal contract. It keeps only the metadata that cannot be reliably inferred from the path, filename, or body and that changes routing, maintenance, resource discovery, or provenance. It also separates document roles, external resources, source history, and Lark sync bindings.

Use it when you need to:

- create or revise directory guides, asset guides, and knowledge notes;
- design or update a Markdown frontmatter schema;
- establish stable references to external files, folders, or cloud resources;
- migrate metadata in bulk and validate YAML, dates, links, and field constraints.

### `zotero-library-manager`

Uses the Zotero Desktop local API to manage attachments and collection membership for existing items. Every mutation starts with a deterministic preview, runs only with explicit authorization, and is verified by reading the library again after the write.

Use it when you need to:

- attach a local PDF or another file to an existing Zotero item;
- move an item between collections without removing unrelated memberships;
- resolve and confirm the exact item, collection, and file before writing;
- verify library changes and avoid silent failures or accidental mutations.

### `obsidian-lark-sync`

Maintains a one-to-one synchronization relationship between local Markdown or Obsidian notes and Lark documents. It distinguishes repository and Obsidian Vault workflows and uses the official `lark-cli`, or a functionally equivalent Lark document API client, to handle revision conflicts, images, attachments, Mermaid diagrams, comments, and format differences.

Use it when you need to:

- publish local Markdown or an Obsidian note to Lark;
- import a Lark document locally while preserving its structure and images;
- detect version changes, resolve conflicts, and merge edits safely;
- maintain local source documents for recurring reports, meeting summaries, or collaborative Lark documents.

See each skill's `SKILL.md` for its full trigger conditions and workflow.

## License

This project is licensed under the [MIT License](LICENSE).
