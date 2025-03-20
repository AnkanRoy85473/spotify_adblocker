import subprocess
import time
import os
import sys
import psutil

class SpotifyAdBlocker:
    def __init__(self):
        self.spotify_bundle = "com.spotify.client" if sys.platform == "darwin" else "Spotify.exe"
        self.hosts_path = "/etc/hosts" if sys.platform != "win32" else r"C:\Windows\System32\drivers\etc\hosts"
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
        self.audio2 = "audio2.spotify.com"
        self.audio4 = "audio4-fa.spotify.com"
        self.crashdump = "crashdump.spotify.com"
        self.desktop = "desktop.spotify.com"
        self.log = "log.spotify.com"
        self.metrics = "metrics.spotify.com"
        self.weighted = "weighted-ads-creatives.spotify.com"
        
    def is_spotify_running(self):
        try:
            processes = [p.name() for p in psutil.process_iter(['name'])]
            return 'Spotify' in processes or 'Spotify.exe' in processes
        except:
            return False

    def block_ads(self):
        try:
            # Check admin privileges
            if sys.platform == "win32":
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    print("Please run as administrator")
                    return False
            else:
                if os.geteuid() != 0:
                    print("Please run with sudo privileges")
                    return False

            # Backup hosts file
            backup_path = self.hosts_path + ".backup"
            if not os.path.exists(backup_path):
                if sys.platform == "win32":
                    subprocess.run(["copy", self.hosts_path, backup_path], shell=True)
                else:
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

            # Flush DNS cache based on OS
            if sys.platform == "win32":
                subprocess.run(["ipconfig", "/flushdns"], shell=True)
            else:
                subprocess.run(["dscacheutil", "-flushcache"])
                subprocess.run(["killall", "-HUP", "mDNSResponder"])

            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def restart_spotify(self):
        if self.is_spotify_running():
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", "Spotify.exe"], shell=True)
                time.sleep(2)
                subprocess.Popen([os.environ["APPDATA"] + "\\Spotify\\Spotify.exe"])
            else:
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