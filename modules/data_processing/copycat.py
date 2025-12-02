from pathlib import Path
import yaml
from datetime import datetime, timezone

from copycatbmi import TRouteWarmer
from modules.data_processing.gpkg_utils import get_cat_to_nhd_feature_id

def get_copycat_cache_dir(
    config_dir: Path
) -> Path|None:
    cache_dir = None
    try:
        config_file = config_dir / 'copycat_config.yaml'
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            cache_dir = config.get('cache_dir', None)
    except Exception as e:
        return None
    return cache_dir
    

def copycat_make_channel_restart_file(
    config_dir: Path, 
    gpkg_dir: Path,
    forcings_dir: Path,
    start_date: datetime
) -> None:
    cache_dir = get_copycat_cache_dir(config_dir=config_dir)
    trw = TRouteWarmer(cache_dir=cache_dir)
    tm1 = start_date.replace(tzinfo=timezone.utc)
    mapping = get_cat_to_nhd_feature_id(gpkg_dir)
    trw.make_channel_restart_file(tm1, mapping, forcings_dir / 'channel_restart_20251201.pkl')
