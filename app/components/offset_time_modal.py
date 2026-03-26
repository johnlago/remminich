import time

from django_unicorn.components import UnicornView
from immich.ImmichClient import ImmichClient
from immich.models import BulkUpdateAssetsModel
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from app.update_rel import adjust_iso8601_time

class OffsetTimeModalView(UnicornView):
    showing:bool = False
    year_offset:int=0
    month_offset:int=0
    day_offset:int=0
    assets:list = []
    album_id=""

    def save_chosen(self):

        for asset in self.assets:
            exif_data = asset.get("exifInfo")
            if exif_data:
                og_time = exif_data.get("dateTimeOriginal")
                if og_time:
                    new_time = adjust_iso8601_time(
                        og_time, years=self.year_offset, months=self.month_offset, days=self.day_offset,
                        hours=0, minutes=0, seconds=0
                    )
                    print(f"Old time: {og_time}, Adjusted: {new_time}")
                    if new_time:
                        ImmichClient.update_assets(BulkUpdateAssetsModel(
                            ids=[asset['id']],
                            dateTimeOriginal=new_time
                        ))

        return redirect('album_detail', album_uuid=self.album_id)

    def mount(self):
        self.year_offset = 0
        self.month_offset = 0
        self.day_offset = 0

