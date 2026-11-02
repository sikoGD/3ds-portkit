# Codex goal: complete 3DS PortKit OSS import and development

This is a fresh, public repository distinct from private FnH2o3DS. The private project's code, game content, assets, logs, credentials, vendor source and commit history must NEVER be copied indiscriminately.

1. Import the files from the provided `3ds-portkit-oss-starter.zip` archive into this repository root (without the enclosing starter folder), replacing the placeholder README. Reconcile existing MIT LICENSE and .gitignore without dropping exclusions.
2. Run `python -m unittest discover -s tests -v`. Record actual evidence; do not claim hardware tests.
3. Develop a game-agnostic RPG Maker MV/MZ structural inspector, safe texture helpers, frame-time profiling, and a minimal Nintendo 3DS native homebrew example.
4. Avoid game-specific bypasses, proprietary content, bundled ROMs or RPG Maker game data. Keep external dependencies separate, observe their licenses.
5. Test with synthetic fixtures; add CI, install docs, user examples, CONTRIBUTING and SECURITY.
6. Keep Old 3DS as the minimum performance target. Report real timings separately for host, emulator and hardware.
7. Work in reviewed milestones, commit and push each verified milestone. Never modify the private FnH2o3DS repo.

Success: the example and CLI run according to their documented requirements, CI is green, and a newcomer can reproduce a safe start.