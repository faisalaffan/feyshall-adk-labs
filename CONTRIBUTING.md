# Contributing to feyshall-adk-labs

Thanks for your interest in contributing! This cookbook thrives on practical, production-tested recipes.

## What Makes a Good Recipe

A strong recipe follows this structure:

1. **Concept** — one paragraph explaining the problem and approach
2. **Prerequisites** — what the reader needs installed or configured
3. **Code** — runnable, minimal, well-commented
4. **Pitfalls** — edge cases, gotchas, and when NOT to use this pattern
5. **References** — links to official docs or related recipes

## How to Contribute

1. **Check existing work.** Search issues and the cookbook to avoid duplicates.
2. **Open an issue first** describing your recipe idea before writing code.
3. **Fork and branch.** Use a descriptive branch name: `recipe/streaming-sse-python`.
4. **Follow the chapter structure.** Place your recipe in the right chapter folder (`00-foundations/`, `01-tools/`, etc.).
5. **Write in English.** Reach is wider.
6. **Keep it opinionated.** Official docs cover the basics — we want production patterns.

## Pull Request Checklist

- [ ] Recipe follows the structure above
- [ ] Code is runnable and tested
- [ ] Language-specific code goes in `_languages/<lang>/`
- [ ] No secrets, tokens, or credentials in code
- [ ] Frontmatter includes ADK version tag (`adk_version: 1.28`)

## Code Style

- Python: follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Go: standard `gofmt` + `go vet`
- Dart: follow [Effective Dart](https://dart.dev/guides/language/effective-dart)

## Need Help?

Open a [discussion](https://github.com/feyshall/feyshall-adk-labs/discussions) or ask in an issue.
