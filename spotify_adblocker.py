import subprocess
import time
import os
import psutil

class SpotifyAdBlocker:
    def __init__(self):
        self.spotify_bundle = "com.spotify.client"
        self.hosts_path = "/etc/hosts"
        self.ad_domains = [
            "adclick.g.doubleclick.net",
            "googleads.g.doubleclick.net",
            "pagead2.googlesyndication.com",
            "tpc.googlesyndication.com",
            "pagead46.l.doubleclick.net",
            "ads-fa.spotify.com",
            "audio-fa.spotify.com",
            "adeventtracker.spotify.com",
            "analytics.spotify.com",
            "weblb-wg.gslb.spotify.com",
            "prod.spotify.map.fastlylb.net",
            "tracking.spotify.com",
            "mp3ad.scdn.co",
            "partner-service.spotify.com",
            "partner-service-testing.spotify.com",
            "video-fa.scdn.co",
            "audio-sp-*.spotifycdn.net"
        ]

    def is_spotify_running(self):
        try:
            # Use psutil to check if Spotify is running
            for proc in psutil.process_iter(['name']):
                if 'Spotify' in proc.info['name']:
                    return True
            return False
        except:
            return False

    def block_ads(self):
        try:
            # Check if running as root
            if os.geteuid() != 0:
                print("Please run this script with sudo privileges")
                return False

            # Backup hosts file
            backup_path = "/etc/hosts.backup"
            if not os.path.exists(backup_path):
                subprocess.run(["cp", self.hosts_path, backup_path])

            # Read existing hosts
            with open(self.hosts_path, 'r') as f:
                hosts_content = f.read()

            # Add ad domains if not already present
            new_entries = []
            for domain in self.ad_domains:
                if domain not in hosts_content:
                    new_entries.append(f"127.0.0.1 {domain}")

            if new_entries:
                with open(self.hosts_path, 'a') as f:
                    f.write("\n# Spotify Ad Blocker\n")
                    f.write("\n".join(new_entries) + "\n")

            # Flush DNS cache
            subprocess.run(["dscacheutil", "-flushcache"])
            subprocess.run(["killall", "-HUP", "mDNSResponder"])

            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def restart_spotify(self):
        if self.is_spotify_running():
            subprocess.run(["killall", "Spotify"])
            time.sleep(2)
            subprocess.run(["open", "-a", "Spotify"])

    def run(self):
        print("Starting Spotify Ad Blocker...")
        if self.block_ads():
            print("Ad blocking rules have been added successfully")
            self.restart_spotify()
            print("Spotify has been restarted with ad blocking enabled")
            print("\nNote: To disable ad blocking, restore /etc/hosts.backup")
        else:
            print("Failed to set up ad blocking")

def main():
    blocker = SpotifyAdBlocker()
    blocker.run()

if __name__ == "__main__":
    main()