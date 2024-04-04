import requests


def get_user_info(access_token):
    url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        user_name = user_data['display_name']
        user_email = user_data['email']
        user_id = user_data['id']
        return user_name, user_email ,user_id
    else:
        print("Failed to get user info:", response.status_code)
        return None, None, None
    
def get_user_playlists(access_token,user_id):
    if user_id:
        url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            playlists_data = response.json()['items']
            playL_data = [playlist for playlist in playlists_data if playlist['owner']['id'] == user_id]
            user_playlists = [playlist['name'] for playlist in playlists_data if playlist['owner']['id'] == user_id]
            return user_playlists, playL_data
        else:
            print("Failed to get user playlists:", response.status_code)
            return None
        
def get_playlist_albums_count(access_token,uri):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api.spotify.com/v1/playlists/{uri.split(':')[-1]}/tracks"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        playlist_data = response.json()
        albums = set()
        for track in playlist_data["items"]:
            album_name = track["track"]["album"]["name"]
            albums.add(album_name)
        num_albums = len(albums)
        return num_albums
    else:
        print("Error:", response.status_code)
        return None
    
def make_image_url_list(access_token,uri):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    playlist_tracks_response = requests.get(f"https://api.spotify.com/v1/playlists/{uri.split(':')[-1]}/tracks", headers=headers)
    album_art_urls = set()
    if playlist_tracks_response.status_code == 200:
        for item in playlist_tracks_response.json()['items']:
            track = item['track']
            if track is not None and 'album' in track and 'images' in track['album'] and len(track['album']['images']) > 0:
                album_art_urls.add(track['album']['images'][0]['url'])
    else:
        print("Error:", playlist_tracks_response.status_code)
        return None

    return list(album_art_urls)