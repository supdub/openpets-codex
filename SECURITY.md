# Security policy

## Supported versions

The latest `main` branch is supported during the project's alpha period.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature for path traversal, unsafe file
replacement, malicious archive, deep-link, or installer issues. Do not open a public issue with
working exploit details.

Ordinary validation bugs, malformed art, and Codex compatibility questions can use the public bug
template. The installer intentionally validates before copy, refuses unexpected overwrite, stages
atomically, and copies only the runtime manifest and spritesheet.
