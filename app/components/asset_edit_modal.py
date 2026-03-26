from django_unicorn.components import UnicornView
from immich.ImmichClient import ImmichClient
from immich.models import SingleAssetUpdateModel
from django.shortcuts import redirect
from app.neediness import invalidate_cache


class AssetEditModalView(UnicornView):
    asset_id: str = ""
    album_id: str = ""
    description: str = ""
    date_month: str = ""
    date_day: str = ""
    date_year: str = ""
    location_search: str = ""
    _last_search: str = ""
    location_suggestions: list = []
    chosen_location: dict = {}
    thumb_url: str = ""

    def mount(self):
        self.asset_id = self.component_kwargs.get("asset_id", "")
        self.album_id = self.component_kwargs.get("album_id", "")
        self.description = self.component_kwargs.get("description", "") or ""
        self.thumb_url = f"/asset/{self.asset_id}/thumb" if self.asset_id else ""

        # Parse existing date if provided
        date_str = self.component_kwargs.get("date", "")
        if date_str:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                self.date_month = str(dt.month)
                self.date_day = str(dt.day)
                self.date_year = str(dt.year)
            except (ValueError, AttributeError):
                pass

        # Parse existing location
        self.chosen_location = {}
        city = self.component_kwargs.get("city", "")
        state = self.component_kwargs.get("state", "")
        lat = self.component_kwargs.get("latitude")
        lng = self.component_kwargs.get("longitude")
        if city or state:
            parts = [p for p in [city, state] if p]
            self.chosen_location = {
                'pretty': ', '.join(parts),
                'latitude': lat,
                'longitude': lng,
            }

    def updating(self, name, value):
        """Called when reactive data changes -- used for location search."""
        if name == 'location_search' and value and value != self._last_search:
            r = ImmichClient.get_place(value)
            r = r[:10] if isinstance(r, list) else []
            for item in r:
                parts = [item.get('name', '')]
                if item.get('admin1name'):
                    parts.append(item['admin1name'])
                if item.get('admin2name'):
                    parts.append(item['admin2name'])
                item['pretty'] = ', '.join(parts)
            self.location_suggestions = r
            self._last_search = value

    def select_location(self, loc):
        self.chosen_location = loc
        self.location_suggestions = []
        self.location_search = ""

    def clear_location(self):
        self.chosen_location = {}

    def save(self):
        update = SingleAssetUpdateModel()

        # Description
        if self.description is not None:
            update.description = self.description

        # Date - build ISO string from parts
        if self.date_year:
            year = int(self.date_year)
            month = int(self.date_month) if self.date_month else 1
            day = int(self.date_day) if self.date_day else 1
            update.dateTimeOriginal = f"{year:04d}-{month:02d}-{day:02d}T00:00:00.000Z"

        # Location
        if self.chosen_location and self.chosen_location.get('latitude'):
            update.latitude = float(self.chosen_location['latitude'])
            update.longitude = float(self.chosen_location['longitude'])

        ImmichClient.update_asset(self.asset_id, update)
        invalidate_cache(self.album_id)
        return redirect('album_detail', album_uuid=self.album_id)
