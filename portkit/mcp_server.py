"""Optional stdio MCP integration for coding agents; not a REA dependency.

Install `mcp` separately. Tools inspect local user-supplied projects only;
returned reports intentionally omit actual game strings and asset bytes.
"""
from pathlib import Path
from .analyze import analyze_rpgmaker, inspect_assets
from .profile import analyze_frames
from .evidence import evidence_report, json_schema


def main():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError('Install optional MCP SDK: python -m pip install mcp') from exc

    server = FastMCP('3DS PortKit')

    @server.tool()
    def inspect_rpg_maker(project_path: str) -> dict:
        """Report map/event and plugin counts from a locally owned MV/MZ installation."""
        report = analyze_rpgmaker(Path(project_path))
        return evidence_report('rpgmv-structure', project_path, report,
                               f'python -m portkit inspect-rpgmv "{project_path}"')

    @server.tool()
    def inspect_asset_folder(folder_path: str) -> dict:
        """Report asset formats and dimensions without copying pixel data."""
        report = inspect_assets(Path(folder_path))
        return evidence_report('asset-inventory', folder_path, report,
                               f'python -m portkit inspect-assets "{folder_path}"')

    @server.tool()
    def inspect_frame_log(csv_path: str, target_fps: float = 30) -> dict:
        """Measure p50/p95/max of work and total frame times from CSV."""
        if target_fps <= 0:
            raise ValueError('target_fps must be positive')
        report = analyze_frames(Path(csv_path), 1000 / target_fps)
        return evidence_report('frame-profile', csv_path, report,
                               f'python -m portkit profile "{csv_path}" --fps {target_fps}')

    @server.tool()
    def portkit_capabilities() -> dict:
        """Describe evidence fields and safety limits, without inspecting any files."""
        return {"schema": json_schema(), "supports": ["structure counts", "asset inventory", "frame statistics"],
                "does_not_support": ["automatic game reverse engineering", "script execution", "game conversion"]}

    server.run(transport='stdio')


if __name__ == '__main__':
    main()
