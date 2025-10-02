import pandas as pd
import requests
import base64
import time
import os
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

print("🎵 Music Rights Analysis Tool - Final Version")
print("=" * 50)


def load_dataset_correctly():
    """Load the dataset with correct header handling"""
    print(" Step 1: Loading dataset with correct headers...")

    try:
        # First, let's read the actual header line that starts with #
        with open('unclaimedmusicalworkrightshares.tsv', 'r', encoding='utf-8') as f:
            header_line = f.readline().strip()
            if header_line.startswith('#'):
                header_line = header_line[1:]  # Remove the # character
            actual_headers = header_line.split('\t')
            print(f" Actual headers: {actual_headers}")

        # Now read the data with the correct headers
        df = pd.read_csv('unclaimedmusicalworkrightshares.tsv',
                         sep='\t',
                         encoding='utf-8',
                         comment='#',
                         nrows=50000,  # Limit rows for memory safety
                         header=0,
                         names=actual_headers)  # Use the actual headers

        print(" Successfully loaded dataset with proper headers")
        print(f" Dataset shape: {df.shape}")
        print(f" Dataset columns: {list(df.columns)}")

        # Create ISRC lookup
        isrc_lookup = defaultdict(list)
        isrc_column = 'ISRC'  # We know the column name from the header

        if isrc_column not in df.columns:
            print(" ISRC column not found!")
            return None, df

        print(f" Using ISRC column: '{isrc_column}'")

        # Build the lookup dictionary
        valid_isrcs = 0
        for idx, row in df.iterrows():
            isrc_code = str(row[isrc_column]).strip().upper()
            if isrc_code and isrc_code != 'NAN' and len(isrc_code) >= 10:
                isrc_lookup[isrc_code].append({
                    'work_title': str(row.get('ResourceTitle', 'Unknown')),
                    'writers': str(row.get('DisplayArtistName', 'Unknown')),
                    'publishers': 'Unknown',
                    'status': 'Unclaimed'
                })
                valid_isrcs += 1

        print(f"Built lookup with {valid_isrcs} valid ISRC codes")
        print(f" Sample ISRCs: {list(isrc_lookup.keys())[:5]}")

        return isrc_lookup, df

    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None, None


def test_spotify_auth():
    """Test Spotify authentication"""
    print("\n Step 2: Testing Spotify authentication...")

    CLIENT_ID = "797926ecf7c94ac7928b2a519ff34d42"
    CLIENT_SECRET = "54028d7053ca4bf693c37549406f6966"

    try:
        # Encode credentials
        client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

        headers = {
            'Authorization': f'Basic {client_creds_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {'grant_type': 'client_credentials'}

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers,
            data=data,
            timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            print(" Spotify authentication successful!")
            return token_data['access_token']
        else:
            print(f" Spotify auth failed: {response.status_code}")
            return None

    except Exception as e:
        print(f" Error during Spotify auth: {e}")
        return None


def get_artist_discography(token, artist_id, artist_name):
    """Get a few tracks from an artist"""
    print(f"\n🎵 Step 3: Getting {artist_name}'s popular tracks...")

    try:
        headers = {'Authorization': f'Bearer {token}'}

        # Get artist's top tracks
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            tracks_data = response.json().get('tracks', [])
            catalog = []

            for track in tracks_data[:10]:  # Get top 10 tracks
                external_ids = track.get('external_ids', {})
                isrc = external_ids.get('isrc', '')

                if isrc:
                    catalog.append({
                        'track_name': track.get('name', ''),
                        'album_name': track.get('album', {}).get('name', ''),
                        'release_date': track.get('album', {}).get('release_date', ''),
                        'isrc': isrc,
                        'popularity': track.get('popularity', 0),
                    })

            df = pd.DataFrame(catalog)
            print(f" Retrieved {len(df)} tracks with ISRC codes")
            print(f" Sample tracks:")
            for i, track in df.head(3).iterrows():
                print(f"   • {track['track_name']} (ISRC: {track['isrc']})")
            return df
        else:
            print(f" Error getting top tracks: {response.status_code}")
            return pd.DataFrame()

    except Exception as e:
        print(f" Error getting discography: {e}")
        return pd.DataFrame()


def search_artist(token, artist_name="The Weeknd"):
    """Search for artist"""
    print(f"\n🔍 Searching for artist '{artist_name}'...")

    try:
        headers = {'Authorization': f'Bearer {token}'}
        params = {
            'q': artist_name,
            'type': 'artist',
            'limit': 5
        }

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            artists = response.json().get('artists', {}).get('items', [])
            if artists:
                print(f" Found {len(artists)} artists:")
                for artist in artists:
                    print(f"   • {artist['name']} (Popularity: {artist['popularity']})")
                return artists[0]  # Return most popular
            else:
                print(" No artists found")
                return None
        else:
            print(f" Search failed: {response.status_code}")
            return None

    except Exception as e:
        print(f" Error searching artist: {e}")
        return None


def find_matches(artist_catalog, isrc_lookup):
    """Find matches between artist catalog and unclaimed works"""
    print(f"\nStep 4: Finding matches...")

    matches = []
    for _, track in artist_catalog.iterrows():
        isrc_code = str(track['isrc']).strip().upper()
        if isrc_code in isrc_lookup:
            for unclaimed_work in isrc_lookup[isrc_code]:
                match = track.to_dict()
                match.update(unclaimed_work)
                matches.append(match)

    result_df = pd.DataFrame(matches) if matches else pd.DataFrame()
    print(f"Found {len(result_df)} matches in unclaimed works")
    return result_df


def create_final_report(artist_catalog, matches, artist_name):
    """Create the final Excel report"""
    try:
        # Create a safe filename without special characters
        safe_name = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        output_file = f"{safe_name}_analysis.xlsx"

        # Use a simple path in current directory
        output_path = os.path.join(os.getcwd(), output_file)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Artist Catalog
            artist_catalog.to_excel(writer, sheet_name='Artist_Catalog', index=False)

            # Matches
            if not matches.empty:
                matches.to_excel(writer, sheet_name='Matches', index=False)
            else:
                pd.DataFrame({'Message': ['No matches found in unclaimed works dataset']}).to_excel(
                    writer, sheet_name='Matches', index=False)

            # Process Notes
            notes_data = {
                'Section': [
                    'Dataset Info',
                    'Spotify Analysis',
                    'Matching Results',
                    'Technical Details'
                ],
                'Details': [
                    f'Unclaimed works: {len(artist_catalog)} records analyzed\nISRC column used for matching',
                    f'Artist: {artist_name}\nTracks analyzed: {len(artist_catalog)}\nSource: Spotify Top Tracks',
                    f'Matches found: {len(matches)}\nMatch rate: {(len(matches) / len(artist_catalog)) * 100 if len(artist_catalog) > 0 else 0:.1f}%',
                    f'Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}\nDataset sample: 50,000 records'
                ]
            }
            pd.DataFrame(notes_data).to_excel(writer, sheet_name='Process_Notes', index=False)

        print(f" Report saved: {output_file}")
        return True

    except Exception as e:
        print(f" Error creating report: {e}")
        print(" Trying alternative save location...")

        # Try saving to user's desktop
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            output_path = os.path.join(desktop, f"{safe_name}_analysis.xlsx")

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                artist_catalog.to_excel(writer, sheet_name='Artist_Catalog', index=False)
                if not matches.empty:
                    matches.to_excel(writer, sheet_name='Matches', index=False)
                else:
                    pd.DataFrame({'Message': ['No matches found']}).to_excel(writer, sheet_name='Matches', index=False)

            print(f"💾 Report saved to Desktop: {os.path.basename(output_path)}")
            return True
        except Exception as e2:
            print(f" Could not save report: {e2}")
            return False


def try_multiple_artists(token, isrc_lookup):
    """Try multiple artists to find matches"""
    print(f"\n Step 5: Trying multiple artists to find matches...")

    artists_to_try = [
        "Taylor Swift",
        "Ed Sheeran",
        "Adele",
        "Drake",
        "Beyonce",
        "Coldplay",
        "Eminem",
        "Kanye West",
        "Rihanna",
        "Bruno Mars"
    ]

    all_matches = []

    for artist_name in artists_to_try[:3]:  # Try first 3 artists
        print(f"\n Testing: {artist_name}")

        artist = search_artist(token, artist_name)
        if not artist:
            continue

        catalog = get_artist_discography(token, artist['id'], artist['name'])
        if catalog.empty:
            continue

        matches = find_matches(catalog, isrc_lookup)
        if not matches.empty:
            print(f" FOUND MATCHES for {artist_name}!")
            all_matches.append({
                'artist': artist_name,
                'catalog': catalog,
                'matches': matches
            })
            # Create individual report for this artist
            create_final_report(catalog, matches, artist_name)

    return all_matches


def main():
    """Main analysis function"""
    try:
        # Step 1: Load dataset
        isrc_lookup, dataset = load_dataset_correctly()
        if isrc_lookup is None:
            print(" Cannot proceed without dataset")
            return

        # Step 2: Spotify authentication
        token = test_spotify_auth()
        if not token:
            print(" Cannot proceed without Spotify access")
            return

        # Step 3: Try The Weeknd first
        print(f"\n" + "=" * 50)
        print("🎵 ANALYZING THE WEEKND")
        print("=" * 50)

        artist = search_artist(token, "The Weeknd")
        if not artist:
            print(" Cannot find The Weeknd")
            return

        artist_catalog = get_artist_discography(token, artist['id'], artist['name'])
        if artist_catalog.empty:
            print(" No tracks found for The Weeknd")
            return

        matches = find_matches(artist_catalog, isrc_lookup)

        # Create report for The Weeknd
        create_final_report(artist_catalog, matches, artist['name'])

        # Step 4: If no matches found, try other artists
        if matches.empty:
            print(f"\n" + "=" * 50)
            print("NO MATCHES FOUND FOR THE WEEKND - TRYING OTHER ARTISTS")
            print("=" * 50)

            all_matches = try_multiple_artists(token, isrc_lookup)

            if all_matches:
                print(f"\n FOUND MATCHES WITH {len(all_matches)} ARTISTS!")
            else:
                print(f"\n No matches found with any popular artists")
                print("💡 The unclaimed works dataset might contain mostly obscure or older works")

        print(f"\n🎉 ANALYSIS COMPLETE!")
        print("=" * 50)

    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    main()