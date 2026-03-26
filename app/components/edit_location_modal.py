import time

from django_unicorn.components import UnicornView
from immich.ImmichClient import ImmichClient
from immich.models import BulkUpdateAssetsModel
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
def _format(v):
    name = v['name']
    if v['admin1name']:
        name = f"{name}, {v['admin1name']}"
    if v['admin2name']:
        name = f"{name}, {v['admin2name']}"

    return name

class EditLocationModalView(UnicornView):
    showing:bool = False
    search_word: str = ""
    _last_search_word:str=""
    suggestions:list=[]
    chosen:dict = {}
    assets:list = []
    album_id=""

    def toggle_modal(self):
        print("toggle")
        self.showing = not self.showing

    def updateChosen(self,a):
        self.chosen = a
        self.suggestions = []
        self.search_word = ""

    def save_chosen(self):
        print(f"saving: {self.chosen}")
        ImmichClient.update_assets(BulkUpdateAssetsModel(
            ids=[asset['id'] for asset in self.assets],
            latitude=self.chosen['latitude'],
            longitude=self.chosen['longitude']
        ))
        time.sleep(3)
        return redirect('album_detail', album_uuid=self.album_id)

    def mount(self):
        self.search_word = ""  # initialize a new list every time a SentenceView is initialized and mounted
        self.suggestions:list[str] = []
        self.assets = self.component_kwargs["assets"]
        self.album_id = self.component_kwargs["album_id"]

    def updating(self, name, value):
        if value != self._last_search_word:
            r = ImmichClient.get_place(value)
            r = r[:10]
            for item in r:
                item['pretty'] = _format(item)
            self.suggestions = r
            self._last_search_word = value
