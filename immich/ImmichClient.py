from immich.models import SearchModel, BulkUpdateAssetsModel, UpdateAlbumModel, SingleAssetUpdateModel
import requests
import json
import os

class _ImmichClient:
	def __init__(self, base_url: str, api_key: str):
		"""
		Initializes the ImmichClient wrapper.

		:param base_url: The base URL of the Immich server.
		:param api_key: The API key for authentication.
		"""
		self.base_url = base_url.rstrip('/')
		self.headers = {
			"x-api-key": f"{api_key}",
			# "Authorization": f"Bearer {api_key}",
			"Content-Type": "application/json",
			'Accept': 'application/json'
		}

	def list_albums(self):
		url = f"{self.base_url}/api/albums"
		response = requests.get(url, headers=self.headers)
		return self._handle_response(response)

	def update_album(self, album_Id:str, update: UpdateAlbumModel):
		# PATCH /albums/:id
		url = f"{self.base_url}/api/albums/{album_Id}"
		response = requests.patch(url, headers=self.headers, data=update.model_dump_json(exclude_unset=True))
		return self._handle_response(response)

	def get_album(self, album_uuid:str):
		url = f"{self.base_url}/api/albums/{album_uuid}"
		response = requests.get(url, headers=self.headers)
		return self._handle_response(response)

	def search_assets(self, search_payload:SearchModel):
		url = f"{self.base_url}/api/search/metadata"
		response = requests.post(url, headers=self.headers, data=search_payload.model_dump_json(exclude_unset=True))
		return self._handle_response(response)

	def make_thumb_url(self, asset_id:str):
		return f"{self.base_url}/api/assets/{asset_id}/thumbnail"
	def get_thumbnail(self, asset_id:str):
		url = self.make_thumb_url(asset_id)
		response = requests.get(url, headers=self.headers)
		return response

	def update_asset(self, asset_id: str, update: SingleAssetUpdateModel):
		"""Update a single asset's metadata. PUT /api/assets/:id"""
		url = f"{self.base_url}/api/assets/{asset_id}"
		response = requests.put(url, headers=self.headers, data=update.model_dump_json(exclude_unset=True))
		return self._handle_response(response)

	def update_assets(self, asset_update:BulkUpdateAssetsModel):
		url = f"{self.base_url}/api/assets"
		pl = asset_update.model_dump_json(exclude_unset=True)
		response = requests.put(url, headers=self.headers, data=pl)
		return response

	def get_place(self, search_str):
		# http://localhost:2283/api/search/places?name=belgrade
		import urllib.parse
		safe_string = urllib.parse.quote_plus(search_str)
		url = f"{self.base_url}/api/search/places?name={safe_string}"
		response = requests.get(url, headers=self.headers)
		print(response)
		return self._handle_response(response)

	def _handle_response(self, response, resp_type=None):
		"""Handles HTTP responses and raises exceptions for errors."""
		try:
			response.raise_for_status()
			return response.json()
		except requests.exceptions.HTTPError as err:
			return {"error": str(err), "status_code": response.status_code}
		except ValueError:
			return {"error": "Invalid JSON response", "status_code": response.status_code}

ImmichClient = _ImmichClient(os.environ['IMMICH_URL'], os.environ['IMMICH_API_KEY'] )


if __name__ == "__main__":
	c = ImmichClient('http://localhost:2283/', "xnFmvnF4E2ijDXZPbCL8LjJm8kbdSwe85EvzD5VZA")
	r = c.get_place("bozeman")
	print(r.json())