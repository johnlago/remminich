import time

from django_unicorn.components import UnicornView
from immich.ImmichClient import ImmichClient
from immich.models import UpdateAlbumModel
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from app.neediness import invalidate_cache

class CaptionModalView(UnicornView):
    showing:bool = False
    caption:str = ""
    album_id:str = ""

    def save_chosen(self):
        ImmichClient.update_album(self.album_id, UpdateAlbumModel(description=self.caption))
        invalidate_cache(self.album_id)
        return redirect('album_detail', album_uuid=self.album_id)

    def mount(self):
        self.caption = self.component_kwargs["caption"]
        self.album_id = self.component_kwargs["album_id"]

