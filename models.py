"""
models.py - Data constructors for geospatial run artifacts
==========================================================
"""

from datetime import datetime


def create_run_config(
    cluster_count: int = 3,
    max_cluster_iterations: int = 20,
    choropleth_metric: str = "point_count",
    zoom_start: int = 4,
) -> dict:
    """
    Create the exploration run configuration.

    Parameters:
        cluster_count (int): Number of K-means clusters.
        max_cluster_iterations (int): Maximum K-means refinement rounds.
        choropleth_metric (str): Region metric to color by.
        zoom_start (int): Default map zoom level.

    Returns:
        dict: Configuration payload.
    """
    return {
        "cluster_count": int(cluster_count),
        "max_cluster_iterations": int(max_cluster_iterations),
        "choropleth_metric": choropleth_metric,
        "zoom_start": int(zoom_start),
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def create_geo_point(
    name: str,
    latitude: float,
    longitude: float,
    region: str,
    category: str,
    population: int,
) -> dict:
    """
    Create one geospatial point record.

    Returns:
        dict: Point payload.
    """
    return {
        "name": name,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "region": region,
        "category": category,
        "population": int(population),
    }


def create_cluster_summary(cluster_id: int, centroid: tuple[float, float], point_names: list[str]) -> dict:
    """
    Create a summary object for one cluster.

    Returns:
        dict: Cluster summary payload.
    """
    return {
        "cluster_id": int(cluster_id),
        "centroid": {
            "latitude": float(centroid[0]),
            "longitude": float(centroid[1]),
        },
        "point_names": list(point_names),
        "size": len(point_names),
    }


def create_region_stat(
    region: str,
    point_count: int,
    total_population: int,
    category_mix: dict,
    intensity_score: float,
) -> dict:
    """
    Create a region-level metric object for choropleth rendering.

    Returns:
        dict: Region metric payload.
    """
    return {
        "region": region,
        "point_count": int(point_count),
        "total_population": int(total_population),
        "category_mix": dict(category_mix),
        "intensity_score": float(intensity_score),
    }


def create_run_summary(
    config: dict,
    points: list[dict],
    clusters: list[dict],
    region_stats: list[dict],
    output_files: dict,
) -> dict:
    """
    Create the complete persistable run artifact.

    Returns:
        dict: Full run payload.
    """
    return {
        "config": config,
        "point_count": len(points),
        "points": points,
        "clusters": clusters,
        "region_stats": region_stats,
        "output_files": output_files,
        "saved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
