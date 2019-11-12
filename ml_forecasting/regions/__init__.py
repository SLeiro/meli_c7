from . import mlb


def get_region(site, location):
    return REGIONS[site].get_region(location)


# Registry regions by site
REGIONS = {
    'MLB': mlb
}
