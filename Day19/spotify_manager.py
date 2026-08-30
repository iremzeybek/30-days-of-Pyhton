import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import time

# =========================================================
# SPOTIFY CONFIGURATION
# =========================================================
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = (
    "playlist-read-private "
    "playlist-modify-public "
    "playlist-modify-private"
)

# =========================================================
# AUTHENTICATION
# =========================================================
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        open_browser=True
    )
)

# =========================================================
# USER INFORMATION
# =========================================================
user = sp.current_user()
user_id = user["id"]

print("=" * 60)
print(f"Logged in as: {user['display_name']} ({user_id})")
print("=" * 60)

# =========================================================
# FETCH USER PLAYLISTS
# =========================================================
print("\nFetching your playlists...")

playlists_data = []
results = sp.current_user_playlists(limit=50)

while results:
    for item in results["items"]:
        playlists_data.append({
            "playlist_name": item["name"],
            "tracks": item["tracks"]["total"],
            "public": item["public"],
            "owner": item["owner"]["display_name"]
        })

    if results["next"]:
        results = sp.next(results)
    else:
        results = None

df = pd.DataFrame(playlists_data)

print(df)

# Save report
report_name = f"spotify_playlists_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(report_name, index=False)

print(f"\nPlaylist report saved as: {report_name}")

# =========================================================
# SEARCH FOR TRACKS
# =========================================================
print("\nSearch for songs to add to a new playlist.")
print("Type 'done' when finished.\n")

track_uris = []

while True:
    query = input("Song search: ").strip()

    if query.lower() == "done":
        break

    try:
        results = sp.search(q=query, type="track", limit=5)
        tracks = results["tracks"]["items"]

        if not tracks:
            print("No results found.\n")
            continue

        print("\nResults:")
        for idx, track in enumerate(tracks, start=1):
            artists = ", ".join(a["name"] for a in track["artists"])
            print(f"{idx}. {track['name']} - {artists}")

        choice = int(input("Select a track number (1-5): "))

        if 1 <= choice <= len(tracks):
            selected = tracks[choice - 1]
            track_uris.append(selected["uri"])
            print(f"Added: {selected['name']}\n")
        else:
            print("Invalid selection.\n")

    except Exception as e:
        print(f"Error: {e}\n")

# =========================================================
# CREATE PLAYLIST
# =========================================================
if track_uris:
    playlist_name = f"Python API Playlist {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description="Created automatically with Spotipy and Python"
    )

    playlist_id = playlist["id"]

    print(f"\nCreated playlist: {playlist_name}")

    # Spotify allows max 100 tracks per request
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        sp.playlist_add_items(playlist_id, batch)
        time.sleep(0.2)

    print(f"Added {len(track_uris)} track(s) to the playlist.")
    print(f"Playlist URL: {playlist['external_urls']['spotify']}")

else:
    print("\nNo tracks selected. Playlist was not created.")

# =========================================================
# DISPLAY PLAYLIST CONTENTS
# =========================================================
print("\nFetching tracks from the new playlist...")

if track_uris:
    items = sp.playlist_items(playlist_id)["items"]

    print("\nPlaylist contents:")
    for idx, item in enumerate(items, start=1):
        track = item["track"]
        artists = ", ".join(a["name"] for a in track["artists"])
        print(f"{idx}. {track['name']} - {artists}")

print("\nDone. Spotify API app finished successfully.")
