# Overview
Repo: zm2231/browser-skill
Ref: 3b8b9296996b7503b36f947622faa820428a9532
Base URL: http://codebase.md/zm2231/browser-skill

## README Summary
Source: README.md
The browser-skill project is a web browser automation tool for AI agents, allowing them to interact with web pages using commands such as open, click, and fill. It uses Chrome's CDP auto-detection to leverage existing logins and provides features like login persistence, stealth mode, and video recording. The project enables automated browsing for various use cases, including background automation, user interaction, and sites requiring saved Chrome passwords.

## Repository tree (depth=3)
File tree: /file_tree (supports depth, base_path, include, exclude)
```
├── commands
│   └── browser.md
├── examples
│   ├── 01-quickstart.sh
│   ├── 02-form-filling.sh
│   ├── 03-auth-persistence.sh
│   ├── 04-scraping.sh
│   ├── 05-testing.sh
│   ├── 06-multi-session.sh
│   ├── 07-cdp-mode.sh
│   ├── 08-streaming.sh
│   ├── 09-video-recording.sh
│   ├── 10-import-chrome-profile.sh
│   ├── 11-enhanced-features.sh
│   └── 12-gmail-hybrid-workflow.sh
├── install.sh
├── README.md
├── scripts
│   ├── start-chrome.sh
│   └── stop-chrome.sh
└── skills
    └── browser-automation
        ├── reference.md
        └── skill.md
```

## Key files
- README: README.md

## How to navigate this repo
Paths below are relative to Base URL.
### Paths
- /readme
- /slice?path=src/index.ts&lines=1:40
- /manifest
- /search?query=router
- /file_tree
- /blob/{ref}/{path}

### Query params
- ext: csv of extensions (example: ts,md)
- base_path: path prefix for tree
- include/exclude: glob patterns
- depth: integer or all
- lines: true to add line numbers
- format: md or html

### Tips
- Use ?depth=all for full tree depth.
- /search combines lexical and semantic results when available.

### Examples
- /readme
- /slice?path=src/index.ts&lines=1:40
- /manifest
- /search?query=router
- /file_tree?base_path=src&depth=2
- /blob/main/src/index.ts