import pytest
from ml_forecasting.regions.mlb import Region as RegionMLB


mlb_test_data = [
    ('BR-RS', RegionMLB.SOUTH),
    ('BR-SC', RegionMLB.SOUTH),
    ('BR-SP', RegionMLB.NORTH),
    ('BR-X', RegionMLB.NORTH),
]


@pytest.mark.parametrize("state,region", mlb_test_data)
def test_mlb_region_from_state(state, region):
    r = RegionMLB.from_state(state)

    assert r == region
