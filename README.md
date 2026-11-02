# 3DS PortKit — OSS starter v0.1

**Experimental, game-agnostic tools for research, prototyping and profiling native Nintendo 3DS homebrew ports.**

This project was informed by engineering lessons from a private RPG Maker-to-3DS experiment, but **contains no Fear & Hunger game files, game logic, scripts, sprite sheets, ROMs or proprietary SDK**. All included code is independently authored for this starter. It is **not** a universal one-click game porter, decompiler or emulator.

## Features that actually work in v0.1

- **RPG Maker MV/MZ structure audit**: counts maps, events, pages, command IDs, JS plugin file count and resource formats locally, without embedding data from the game in the report.
- **Asset inventory**: files, extensions, PNG resolution risks and a simple source-byte inventory; estimates are **not measured RAM/VRAM consumption**.
- **FPS/latency report**: reads frame CSVs, computes median, p95, maximum and over-budget counts for both render work and complete frame time.
- **Optional offline PNG preparation**: nearest-neighbor scaling and transparent power-of-two padding, requiring Pillow; output is PNG, not a finished `tex3ds` GPU texture.
- **Optional coding-agent MCP interface**: three local analysis tools over stdio using the external MCP Python SDK (integration not end-to-end tested).
- **Original libctru `.3dsx` sample**: `init` scaffolds a new, unbranded C/Make homebrew app without game content.
- Python standard library for the core CLI; optional Pillow and MCP SDK for extra commands.

## Quick start

Python 3.10+ required. From repository root:

```bash
python -m portkit inspect-rpgmv "C:/YourOwnedRPGMakerGame" --output report.json
python -m portkit inspect-assets "C:/YourOwnedRPGMakerGame/img" --output assets.json
python -m portkit profile examples/synthetic-frames.csv --fps 30
# Optional: pip install Pillow; python -m portkit prepare-texture input.png output.png
# Optional: pip install mcp; python -m portkit.mcp_server
python -m portkit init ./my-3ds-demo --name "My Homebrew"
python -m unittest discover -s tests -v
```

For native builds, install the official **devkitPro `3ds-dev` toolchain** and run `make` in the new demo directory. Build success and device FPS are **not** verified for this starter; review on both original 3DS and New 3DS devices before shipping.

## Relationship to REA

Inspired by the evidence-first research workflow of [REA — Reverse Engineer Anything](https://github.com/morluto/rea), but not a fork, copy, adapter or an REA integration. A minimal optional MCP stdio adapter exposes audits and frame profiles to coding agents; advanced provenance and source tracing are still planned. REA itself is not included.

## What this is not

It cannot convert arbitrary game engines or Windows executables to 3DS. It does not decrypt or distribute copyrighted works or bypass DRM. Users must have rights to their inputs, and compatible original open-source games are the intended development targets. A 30 FPS frame budget is a **goal**, not a promise.

## Next steps

See [ROADMAP](docs/ROADMAP.md). We welcome PRs for synthetic fixtures, generic adapters and better developer documentation. Do not upload third-party game assets in issues or pull requests.

## Credits and licensing

Original starter code is MIT licensed. devkitPro's libctru and related tools are **external dependencies**, not redistributed. [devkitPro/3ds-examples](https://github.com/devkitPro/3ds-examples) provides official teaching material. The private research project is not included here.
