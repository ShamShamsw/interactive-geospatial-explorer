"""
operations.py - Core geospatial exploration workflow
====================================================

Implements:
    - sample point loading
    - simple K-means style clustering
    - region metrics for choropleth rendering
    - map export (points, clusters, region intensity)
    - run artifact persistence
"""

from collections import Counter
from math import sqrt

from models import (
    create_cluster_summary,
    create_geo_point,
    create_region_stat,
    create_run_config,
    create_run_summary,
)
from storage import get_output_dir, save_latest_run


def _load_folium():
    """
    Lazily import folium to keep import errors readable.
    """
    try:
        import folium
        from folium.features import GeoJsonTooltip

        return folium, GeoJsonTooltip
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: folium. Install requirements.txt for this project first."
        ) from exc


def load_sample_points() -> list[dict]:
    """
    Return built-in sample city points for a first geospatial workflow.

    Returns:
        list[dict]: Point records.
    """
    return [
        create_geo_point("Seattle", 47.6062, -122.3321, "west", "tech", 733_919),
        create_geo_point("San Francisco", 37.7749, -122.4194, "west", "tech", 808_437),
        create_geo_point("Los Angeles", 34.0522, -118.2437, "west", "media", 3_849_297),
        create_geo_point("Denver", 39.7392, -104.9903, "central", "logistics", 713_252),
        create_geo_point("Chicago", 41.8781, -87.6298, "central", "finance", 2_664_452),
        create_geo_point("Dallas", 32.7767, -96.7970, "south", "energy", 1_302_868),
        create_geo_point("Austin", 30.2672, -97.7431, "south", "tech", 979_882),
        create_geo_point("Atlanta", 33.7490, -84.3880, "south", "logistics", 510_823),
        create_geo_point("New York City", 40.7128, -74.0060, "east", "finance", 8_258_035),
        create_geo_point("Boston", 42.3601, -71.0589, "east", "education", 653_833),
        create_geo_point("Miami", 25.7617, -80.1918, "east", "tourism", 455_924),
        create_geo_point("Washington DC", 38.9072, -77.0369, "east", "government", 678_972),
    ]


def load_region_geojson() -> dict:
    """
    Return simple region polygons used for choropleth rendering.

    Returns:
        dict: GeoJSON FeatureCollection.
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"region": "west"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-125, 32], [-104, 32], [-104, 49], [-125, 49], [-125, 32]]],
                },
            },
            {
                "type": "Feature",
                "properties": {"region": "central"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-104, 32], [-92, 32], [-92, 49], [-104, 49], [-104, 32]]],
                },
            },
            {
                "type": "Feature",
                "properties": {"region": "south"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-92, 25], [-75, 25], [-75, 37], [-92, 37], [-92, 25]]],
                },
            },
            {
                "type": "Feature",
                "properties": {"region": "east"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-92, 37], [-66, 37], [-66, 48], [-92, 48], [-92, 37]]],
                },
            },
        ],
    }


def compute_map_center(points: list[dict]) -> tuple[float, float]:
    """
    Compute average latitude and longitude of all points.

    Returns:
        tuple[float, float]: Map center coordinate.
    """
    if not points:
        return 39.5, -98.35
    mean_lat = sum(point["latitude"] for point in points) / len(points)
    mean_lon = sum(point["longitude"] for point in points) / len(points)
    return mean_lat, mean_lon


def _distance(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """
    Return Euclidean distance between two lat/lon coordinates.
    """
    return sqrt((a_lat - b_lat) ** 2 + (a_lon - b_lon) ** 2)


def cluster_points(
    points: list[dict],
    cluster_count: int,
    max_iterations: int,
) -> tuple[list[dict], list[tuple[float, float]]]:
    """
    Cluster points with a beginner-friendly K-means implementation.

    Parameters:
        points (list[dict]): Input geospatial points.
        cluster_count (int): Number of clusters.
        max_iterations (int): Max centroid update cycles.

    Returns:
        tuple[list[dict], list[tuple[float, float]]]:
            - points including assigned cluster IDs
            - centroid coordinates
    """
    if not points:
        return [], []

    safe_cluster_count = max(1, min(cluster_count, len(points)))
    working_points = [dict(point) for point in points]
    centroids = [
        (point["latitude"], point["longitude"])
        for point in working_points[:safe_cluster_count]
    ]

    for _ in range(max_iterations):
        changed = False

        for point in working_points:
            best_cluster_id = min(
                range(safe_cluster_count),
                key=lambda idx: _distance(
                    point["latitude"],
                    point["longitude"],
                    centroids[idx][0],
                    centroids[idx][1],
                ),
            )
            if point.get("cluster_id") != best_cluster_id:
                changed = True
            point["cluster_id"] = best_cluster_id

        updated_centroids = []
        for cluster_id in range(safe_cluster_count):
            members = [p for p in working_points if p["cluster_id"] == cluster_id]
            if not members:
                updated_centroids.append(centroids[cluster_id])
                continue

            avg_lat = sum(point["latitude"] for point in members) / len(members)
            avg_lon = sum(point["longitude"] for point in members) / len(members)
            updated_centroids.append((avg_lat, avg_lon))

        if not changed:
            centroids = updated_centroids
            break
        centroids = updated_centroids

    return working_points, centroids


def summarize_clusters(points_with_clusters: list[dict], centroids: list[tuple[float, float]]) -> list[dict]:
    """
    Build cluster-level summaries.

    Returns:
        list[dict]: Cluster summary payloads.
    """
    summaries = []
    for cluster_id, centroid in enumerate(centroids):
        members = [point["name"] for point in points_with_clusters if point["cluster_id"] == cluster_id]
        summaries.append(create_cluster_summary(cluster_id, centroid, members))
    return summaries


def build_region_stats(points: list[dict]) -> list[dict]:
    """
    Aggregate points into region-level metrics for choropleth rendering.

    Returns:
        list[dict]: Region metric payloads.
    """
    grouped: dict[str, dict] = {}

    for point in points:
        region = point["region"]
        if region not in grouped:
            grouped[region] = {
                "point_count": 0,
                "total_population": 0,
                "categories": [],
            }

        grouped[region]["point_count"] += 1
        grouped[region]["total_population"] += point["population"]
        grouped[region]["categories"].append(point["category"])

    region_stats = []
    for region, payload in grouped.items():
        category_mix = dict(Counter(payload["categories"]))

        # Intensity balances absolute population with point density.
        intensity = payload["total_population"] / max(1, payload["point_count"])

        region_stats.append(
            create_region_stat(
                region=region,
                point_count=payload["point_count"],
                total_population=payload["total_population"],
                category_mix=category_mix,
                intensity_score=intensity,
            )
        )

    return sorted(region_stats, key=lambda row: row["region"])


def _metric_to_color(value: float, min_value: float, max_value: float) -> str:
    """
    Map a metric value to a choropleth fill color.
    """
    palette = ["#deebf7", "#9ecae1", "#6baed6", "#3182bd", "#08519c"]
    if max_value <= min_value:
        return palette[0]

    normalized = (value - min_value) / (max_value - min_value)
    index = min(int(normalized * (len(palette) - 1)), len(palette) - 1)
    return palette[index]


def generate_points_map(points: list[dict], zoom_start: int) -> str:
    """
    Generate and save the map with plain point markers.

    Returns:
        str: Saved HTML path.
    """
    folium, _ = _load_folium()

    center = compute_map_center(points)
    point_map = folium.Map(location=center, zoom_start=zoom_start, tiles="CartoDB positron")

    for point in points:
        popup = (
            f"{point['name']}<br>"
            f"Region: {point['region']}<br>"
            f"Category: {point['category']}<br>"
            f"Population: {point['population']:,}"
        )
        folium.Marker(location=[point["latitude"], point["longitude"]], popup=popup).add_to(point_map)

    output_path = get_output_dir() / "points_map.html"
    point_map.save(str(output_path))
    return str(output_path)


def generate_clusters_map(points_with_clusters: list[dict], centroids: list[tuple[float, float]], zoom_start: int) -> str:
    """
    Generate and save the cluster map.

    Returns:
        str: Saved HTML path.
    """
    folium, _ = _load_folium()

    center = compute_map_center(points_with_clusters)
    cluster_map = folium.Map(location=center, zoom_start=zoom_start, tiles="CartoDB positron")

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    for point in points_with_clusters:
        color = colors[point["cluster_id"] % len(colors)]
        folium.CircleMarker(
            location=[point["latitude"], point["longitude"]],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f"{point['name']} (Cluster {point['cluster_id']})",
        ).add_to(cluster_map)

    for cluster_id, centroid in enumerate(centroids):
        folium.Marker(
            location=[centroid[0], centroid[1]],
            popup=f"Centroid {cluster_id}",
            icon=folium.Icon(color="black", icon="info-sign"),
        ).add_to(cluster_map)

    output_path = get_output_dir() / "clusters_map.html"
    cluster_map.save(str(output_path))
    return str(output_path)


def generate_choropleth_map(
    region_geojson: dict,
    region_stats: list[dict],
    choropleth_metric: str,
    zoom_start: int,
) -> str:
    """
    Generate and save a region-intensity choropleth map.

    Returns:
        str: Saved HTML path.
    """
    folium, GeoJsonTooltip = _load_folium()

    metric_values = {item["region"]: item.get(choropleth_metric, 0.0) for item in region_stats}
    all_values = list(metric_values.values())
    min_value = min(all_values) if all_values else 0.0
    max_value = max(all_values) if all_values else 1.0

    choro_map = folium.Map(location=[38.5, -96.0], zoom_start=zoom_start, tiles="CartoDB positron")

    def style_function(feature: dict) -> dict:
        region = feature["properties"]["region"]
        value = float(metric_values.get(region, 0.0))
        return {
            "fillColor": _metric_to_color(value, min_value, max_value),
            "weight": 1,
            "opacity": 1,
            "color": "#1f2937",
            "fillOpacity": 0.65,
        }

    folium.GeoJson(
        data=region_geojson,
        style_function=style_function,
        tooltip=GeoJsonTooltip(fields=["region"], aliases=["Region:"]),
        name="Region intensity",
    ).add_to(choro_map)

    for stat in region_stats:
        popup = (
            f"Region: {stat['region']}<br>"
            f"Point count: {stat['point_count']}<br>"
            f"Total population: {stat['total_population']:,}<br>"
            f"Intensity score: {stat['intensity_score']:.2f}"
        )
        if stat["region"] == "west":
            location = [41.0, -114.5]
        elif stat["region"] == "central":
            location = [41.0, -98.0]
        elif stat["region"] == "south":
            location = [31.5, -83.5]
        else:
            location = [42.0, -78.0]

        folium.Marker(location=location, popup=popup).add_to(choro_map)

    folium.LayerControl().add_to(choro_map)
    output_path = get_output_dir() / "choropleth_map.html"
    choro_map.save(str(output_path))
    return str(output_path)


def run_core_flow() -> dict:
    """
    Execute one full geospatial exploration run.

    Returns:
        dict: Run artifact payload.
    """
    config = create_run_config()
    points = load_sample_points()
    region_geojson = load_region_geojson()

    points_with_clusters, centroids = cluster_points(
        points=points,
        cluster_count=config["cluster_count"],
        max_iterations=config["max_cluster_iterations"],
    )

    clusters = summarize_clusters(points_with_clusters, centroids)
    region_stats = build_region_stats(points)

    points_map = generate_points_map(points, config["zoom_start"])
    clusters_map = generate_clusters_map(points_with_clusters, centroids, config["zoom_start"])
    choropleth_map = generate_choropleth_map(
        region_geojson=region_geojson,
        region_stats=region_stats,
        choropleth_metric=config["choropleth_metric"],
        zoom_start=config["zoom_start"],
    )

    output_files = {
        "points_map": points_map,
        "clusters_map": clusters_map,
        "choropleth_map": choropleth_map,
    }

    run_summary = create_run_summary(
        config=config,
        points=points_with_clusters,
        clusters=clusters,
        region_stats=region_stats,
        output_files=output_files,
    )
    save_latest_run(run_summary)
    return run_summary
