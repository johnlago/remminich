"""
Neediness algorithm for album prioritization.

Albums are scored by how much metadata is missing. Higher score = more needy.
Score = (no_dates + no_captions + no_locations) / (total_images * 3) * 100
"""

import time
import logging
from immich.ImmichClient import ImmichClient

logger = logging.getLogger(__name__)

# Simple in-memory cache: {album_id: (score, summary_data, timestamp)}
_cache = {}
_CACHE_TTL = 300  # 5 minutes


def compute_neediness(album_detail: dict) -> tuple[float, dict]:
    """
    Compute the neediness score for an album and return (score, summary_data).

    summary_data includes counts useful for the swipe view info box.
    """
    assets = album_detail.get('assets', [])
    total = len(assets)
    if total == 0:
        return 0.0, {'total': 0, 'no_dates': 0, 'no_captions': 0, 'no_locations': 0}

    no_dates = 0
    no_captions = 0
    no_locations = 0

    for asset in assets:
        exif = asset.get('exifInfo', {})
        if not exif:
            no_dates += 1
            no_captions += 1
            no_locations += 1
            continue

        # Date: missing if dateTimeOriginal is None or empty
        dt = exif.get('dateTimeOriginal')
        if not dt:
            no_dates += 1

        # Caption: missing if description is None or empty string
        desc = exif.get('description')
        if not desc or desc.strip() == '':
            no_captions += 1

        # Location: missing if no city, state, country, lat, or long
        has_location = any([
            exif.get('city'),
            exif.get('state'),
            exif.get('country'),
            exif.get('latitude'),
            exif.get('longitude'),
        ])
        if not has_location:
            no_locations += 1

    score = (no_dates + no_captions + no_locations) / (total * 3) * 100

    summary_data = {
        'total': total,
        'no_dates': no_dates,
        'no_captions': no_captions,
        'no_locations': no_locations,
    }

    return score, summary_data


def get_album_queue(exclude_ids=None):
    """
    Return all albums sorted by neediness (most needy first).

    exclude_ids: set of album UUIDs to skip (e.g. already passed by user).
    Returns list of dicts with album info + neediness score.
    """
    if exclude_ids is None:
        exclude_ids = set()

    all_albums = ImmichClient.list_albums()
    scored_albums = []

    for album_summary in all_albums:
        album_id = album_summary['id']
        if album_id in exclude_ids:
            continue

        # Check cache
        now = time.time()
        if album_id in _cache and (now - _cache[album_id][2]) < _CACHE_TTL:
            score, neediness_data = _cache[album_id][0], _cache[album_id][1]
        else:
            album_detail = ImmichClient.get_album(album_id)
            if isinstance(album_detail, dict) and 'error' in album_detail:
                logger.warning(f"Failed to fetch album {album_id}: {album_detail['error']}")
                continue
            score, neediness_data = compute_neediness(album_detail)
            _cache[album_id] = (score, neediness_data, now)

        scored_albums.append({
            'id': album_id,
            'albumName': album_summary.get('albumName', ''),
            'albumThumbnailAssetId': album_summary.get('albumThumbnailAssetId'),
            'assetCount': album_summary.get('assetCount', 0),
            'neediness': score,
            'neediness_data': neediness_data,
        })

    # Sort by neediness descending (most needy first)
    scored_albums.sort(key=lambda a: a['neediness'], reverse=True)
    return scored_albums


def invalidate_cache(album_id=None):
    """Clear cache for a specific album or all albums."""
    if album_id:
        _cache.pop(album_id, None)
    else:
        _cache.clear()
