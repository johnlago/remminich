# under CC0/Public Domain. Do as you like. NO WARRANTY

# make venv, pip install requests python-dateutil
# This script updates the original date of all photos in an Immich album by a given offset.

# Use: python3 immich-date-shift.py <ALBUM_ID> --years=-10 --days=5 --hours=2

import requests
import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

def adjust_iso8601_time(iso_string: str, years=0, months=0, days=0, hours=0, minutes=0, seconds=0, timezone='UTC') -> str | None:
	try:
		# Parse the ISO 8601 string, handling time zones manually
		if 'Z' in iso_string:
			iso_string = iso_string.replace('Z', '+00:00')  # Convert 'Z' to UTC offset
		dt = datetime.fromisoformat(iso_string)

		# Convert to the specified time zone if necessary
		if timezone != 'UTC':
			dt = dt.astimezone(ZoneInfo(timezone))

		# Adjust year and month together (months can overflow into years)
		new_year = dt.year + years
		new_month = dt.month + months
		# Normalize month to 1-12 range
		new_year += (new_month - 1) // 12
		new_month = ((new_month - 1) % 12) + 1
		# Clamp day to valid range for the new month
		import calendar
		max_day = calendar.monthrange(new_year, new_month)[1]
		new_day = min(dt.day, max_day)

		adjusted_dt = dt.replace(year=new_year, month=new_month, day=new_day) + timedelta(days=days, hours=hours, minutes=minutes,
																   seconds=seconds)

		# Convert back to ISO 8601 format in UTC
		new_iso_string = adjusted_dt.astimezone(ZoneInfo('UTC')).isoformat(timespec='milliseconds').replace('+00:00',
																											'Z')
		return new_iso_string

	except ValueError as e:
		print(f"Error parsing date: {e}")
		return None


def change_date_immich(photo_uuid: str, new_date: str) -> requests.Response:
	url = f"{API_URL}assets"
	payload = json.dumps({
		"dateTimeOriginal": new_date,
		"ids": [photo_uuid]
	})
	headers = {
		'Content-Type': 'application/json',
		'x-api-key': API_KEY
	}
	return requests.put(url, headers=headers, data=payload)


def main():
	parser = argparse.ArgumentParser(description="Offset dates of all photos in an Immich album.")
	parser.add_argument("album_id", nargs="?", help="The UUID of the album")
	parser.add_argument("--years", type=int, default=0, help="Number of years to offset")
	parser.add_argument("--days", type=int, default=0, help="Number of days to offset")
	parser.add_argument("--hours", type=int, default=0, help="Number of hours to offset")
	parser.add_argument("--minutes", type=int, default=0, help="Number of minutes to offset")
	parser.add_argument("--seconds", type=int, default=0, help="Number of seconds to offset")

	args = parser.parse_args()

	album_id = args.album_id
	if not album_id:
		album_id = input("Enter the album ID: ").strip()

	album_url = f"{API_URL}albums/{album_id}"
	headers = {
		'Accept': 'application/json',
		'x-api-key': API_KEY
	}

	response = requests.get(album_url, headers=headers)

	if response.status_code != 200:
		print(f"Error: Failed to fetch album data ({response.status_code})")
		return

	for asset in response.json().get("assets", []):
		exif_data = asset.get("exifInfo")
		if exif_data:
			og_time = exif_data.get("dateTimeOriginal")
			if og_time:
				new_time = adjust_iso8601_time(
					og_time, years=args.years, days=args.days, hours=args.hours, minutes=args.minutes,
					seconds=args.seconds
				)
				print(f"Old time: {og_time}, Adjusted: {new_time}")
				if new_time:
					print(change_date_immich(asset["id"], new_time).text)


if __name__ == "__main__":
	main()