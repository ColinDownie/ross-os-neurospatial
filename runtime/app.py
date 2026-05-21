"""Ross-OS NeuroSpatial Runtime Application

FastAPI runtime shell exposing the NeuroSpatial Engine + Stability Mapper as HTTP APIs.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List

# Import core modules (adjust paths if core structure differs)
try:
    from core.neurospatial_engine import NeuroSpatialEngine
    from core.stability_mapper import CivilizationalStabilityMapGenerator
except ImportError:
    # Fallback for development; core modules may not exist yet
    NeuroSpatialEngine = None
    CivilizationalStabilityMapGenerator = None

app = FastAPI(
    title="Ross-OS NeuroSpatial Runtime",
    version="1.0.0",
    description="Computational civilizational cybernetics engine runtime",
)

# Initialize core engines
try:
    engine = NeuroSpatialEngine()
    mapper = CivilizationalStabilityMapGenerator()
except Exception as e:
    print(f"Warning: Core modules not fully initialized: {e}")
    engine = None
    mapper = None


# ============================================================================
# Data Models
# ============================================================================

class TelemetryPayload(BaseModel):
    """Single environment telemetry input"""
    system_inputs: Dict[str, Any]


class TilePayload(BaseModel):
    """Geospatial tile specification"""
    tile_id: str
    bounding_box_coordinates: List[List[float]]
    telemetry_payload: TelemetryPayload


class RegionPayload(BaseModel):
    """Regional assessment payload"""
    region_id: str
    geospatial_tiles: List[TilePayload]


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", summary="Health check")
def health():
    """Service health and status"""
    return {
        "service": "Ross-OS NeuroSpatial Runtime",
        "status": "operational",
        "engine_ready": engine is not None,
        "mapper_ready": mapper is not None,
    }


@app.post("/evaluate", summary="Evaluate a single environment")
def evaluate_environment(payload: TelemetryPayload):
    """
    Evaluate architectural entropy, spatial coherence, and stability indices
    for a single environment.

    **Input:**
    - `system_inputs`: Dict of environmental parameters

    **Output:**
    - indices: Array of computed metrics
    - toxins: Environmental degradation factors
    - stability_score: 0-1 normalized stability
    - outcome_state: Categorical assessment (stable/transitional/critical)
    """
    if engine is None:
        return {
            "error": "NeuroSpatialEngine not initialized",
            "status": "engine_unavailable",
        }

    try:
        result = engine.evaluate_environment(payload.dict())
        return result
    except Exception as e:
        return {
            "error": str(e),
            "status": "evaluation_failed",
            "payload_received": payload.dict(),
        }


@app.post("/map", summary="Generate a regional stability map")
def generate_map(payload: RegionPayload):
    """
    Compile geospatial stability assessment across multiple tiles.

    **Input:**
    - `region_id`: Unique region identifier
    - `geospatial_tiles`: List of tile specifications with telemetry

    **Output:**
    - matrix_layers: 3D geospatial assessment matrix
    - regional_integrity_coefficient: 0-1 normalized regional stability
    - tile_results: Per-tile outcome breakdown
    """
    if mapper is None:
        return {
            "error": "CivilizationalStabilityMapGenerator not initialized",
            "status": "mapper_unavailable",
        }

    try:
        tiles = [t.dict() for t in payload.geospatial_tiles]
        result = mapper.compile_regional_stability_map(payload.region_id, tiles)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "status": "mapping_failed",
            "region_id": payload.region_id,
            "tile_count": len(payload.geospatial_tiles),
        }


# ============================================================================
# Metadata
# ============================================================================

@app.get("/spec", summary="API specification")
def api_specification():
    """Return API contract specification for external integrations"""
    return {
        "version": "1.0.0",
        "endpoints": {
            "POST /evaluate": {
                "description": "Evaluate a single environment",
                "input_schema": "TelemetryPayload",
                "output_fields": ["indices", "toxins", "stability_score", "outcome_state"],
            },
            "POST /map": {
                "description": "Generate a regional stability map",
                "input_schema": "RegionPayload",
                "output_fields": ["matrix_layers", "regional_integrity_coefficient", "tile_results"],
            },
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
