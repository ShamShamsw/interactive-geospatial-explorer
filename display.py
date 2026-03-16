"""
display.py - Formatting helpers for geospatial explorer output
==============================================================
"""


def format_header() -> str:
    """Return CLI banner for this project."""
    return (
        "=" * 62
        + "\n"
        + "  INTERACTIVE GEOSPATIAL EXPLORER - POINTS, CLUSTERS, CHOROPLETH\n"
        + "=" * 62
    )


def _format_clusters(clusters: list[dict]) -> str:
    """
    Format cluster summary lines.
    """
    lines = ["Cluster summary:"]
    for cluster in clusters:
        centroid = cluster["centroid"]
        lines.append(
            "  Cluster "
            + str(cluster["cluster_id"])
            + f": size={cluster['size']}, "
            + f"centroid=({centroid['latitude']:.3f}, {centroid['longitude']:.3f})"
        )
    return "\n".join(lines)


def _format_regions(region_stats: list[dict]) -> str:
    """
    Format region metric lines.
    """
    lines = ["Region metrics:"]
    for region in region_stats:
        lines.append(
            f"  {region['region']}: points={region['point_count']}, "
            f"population={region['total_population']:,}, "
            f"intensity={region['intensity_score']:.2f}"
        )
    return "\n".join(lines)


def _format_outputs(output_files: dict) -> str:
    """
    Format generated output file paths.
    """
    return "\n".join(
        [
            "Generated map files:",
            f"  Points map: {output_files['points_map']}",
            f"  Clusters map: {output_files['clusters_map']}",
            f"  Choropleth map: {output_files['choropleth_map']}",
            "Saved run artifact: data/runs/latest_geospatial_run.json",
        ]
    )


def format_run_report(run: dict) -> str:
    """
    Format complete geospatial run report.

    Parameters:
        run (dict): Run artifact from operations.py.

    Returns:
        str: User-facing report.
    """
    config = run["config"]
    lines = [
        "",
        "Configuration:",
        f"  Cluster count: {config['cluster_count']}",
        f"  Max cluster iterations: {config['max_cluster_iterations']}",
        f"  Choropleth metric: {config['choropleth_metric']}",
        f"  Zoom start: {config['zoom_start']}",
        "",
        f"Loaded points: {run['point_count']}",
        "",
        _format_clusters(run["clusters"]),
        "",
        _format_regions(run["region_stats"]),
        "",
        _format_outputs(run["output_files"]),
    ]
    return "\n".join(lines)
