# Beginner Project 10: Interactive Geospatial Explorer

**Time:** 3-5 hours  
**Difficulty:** Intermediate Beginner  
**Focus:** Geospatial points, clustering, region intensity mapping, and map output interpretation

---

## Why This Project?

A lot of analytics work is location-based: city operations, logistics, site analysis, and market exploration.
This project gives you a practical geospatial workflow where you can:

- visualize raw points,
- discover cluster patterns,
- compare region-level intensity through a choropleth,
- and save reproducible run artifacts.

---

## More Projects

You can access this project and more in this separate repository:

[student-interview-prep](https://github.com/ShamShamsw/student-interview-prep.git)

---

## What You Will Build

You will build a command-line geospatial explorer that:

1. Loads sample city-level point data.
2. Creates a map of all points.
3. Runs a beginner-friendly K-means clustering pass.
4. Creates a cluster map with centroid markers.
5. Aggregates region metrics and renders a choropleth map.
6. Saves run metadata and map file paths to JSON.

---

## Requirements

- Python 3.10+
- `folium`

Install with:

```bash
pip install -r requirements.txt
```

---

## Example Session

```text
==============================================================
   INTERACTIVE GEOSPATIAL EXPLORER - POINTS, CLUSTERS, CHOROPLETH
==============================================================

Configuration:
   Cluster count: 3
   Max cluster iterations: 20
   Choropleth metric: point_count
   Zoom start: 4

Loaded points: 12

Cluster summary:
   Cluster 0: size=3, centroid=(39.811, -121.000)
   Cluster 1: size=5, centroid=(33.492, -92.935)
   Cluster 2: size=4, centroid=(40.465, -77.823)

Region metrics:
   central: points=2, population=3,377,704, intensity=1688852.00
   east: points=4, population=10,046,764, intensity=2511691.00
   south: points=3, population=2,793,573, intensity=931191.00
   west: points=3, population=5,391,653, intensity=1797217.67

Generated map files:
   Points map: .../data/outputs/points_map.html
   Clusters map: .../data/outputs/clusters_map.html
   Choropleth map: .../data/outputs/choropleth_map.html
Saved run artifact: data/runs/latest_geospatial_run.json
```

---

## Build Order

Follow this order for clean architecture:

1. `storage.py`
2. `models.py`
3. `operations.py`
4. `display.py`
5. `main.py`

---

## File Responsibilities

- `storage.py`: handles run artifact and output directory persistence.
- `models.py`: creates consistent record payloads for points, clusters, and region stats.
- `operations.py`: geospatial logic, clustering, aggregation, and map generation.
- `display.py`: formats a readable CLI summary.
- `main.py`: thin orchestration entry point.

---

## Suggested Reflection Prompts

Add answers in your own notes after running the project:

- How did the cluster map reveal patterns that point markers alone did not?
- Which region looked strongest in the choropleth, and why?
- What are limitations of this simple K-means and rectangular region model?

---

## Stretch Goals

1. Allow loading custom CSV input instead of fixed sample points.
2. Add marker filtering by category and population threshold.
3. Add multiple clustering metrics and compare outputs.
4. Export a Markdown report summarizing each run.
