import os
import subprocess
import time

class SpotifyAdBlockerAndroid:
    def __init__(self):
        self.hosts_path = "/system/etc/hosts"
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

    def check_root(self):
        return os.getuid() == 0

    def mount_system_rw(self):
        try:
            subprocess.run(["mount", "-o", "rw,remount", "/system"])
            return True
        except:
            return False

    def block_ads(self):
        if not self.check_root():
            print("This script requires root access (SuperSU/Magisk)")
            return False

        try:
            if not self.mount_system_rw():
                print("Failed to mount system as read-write")
                return False

            # Backup original hosts
            if not os.path.exists(self.hosts_path + ".backup"):
                subprocess.run(["cp", self.hosts_path, self.hosts_path + ".backup"])

            # Read existing hosts
            with open(self.hosts_path, 'r') as f:
                hosts_content = f.read()

            # Add ad domains
            new_entries = []
            for domain in self.ad_domains:
                if domain not in hosts_content:
                    new_entries.append(f"127.0.0.1 {domain}")

            if new_entries:
                with open(self.hosts_path, 'a') as f:
                    f.write("\n# Spotify Ad Blocker for Android\n")
                    f.write("\n".join(new_entries) + "\n")

            # Set proper permissions
            subprocess.run(["chmod", "644", self.hosts_path])

            # Clear DNS cache
            subprocess.run(["resetprop", "net.dns1", "8.8.8.8"])
            
            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def restart_spotify(self):
        try:
            subprocess.run(["am", "force-stop", "com.spotify.music"])
            time.sleep(2)
            subprocess.run(["am", "start", "-n", "com.spotify.music/.MainActivity"])
        except:
            print("Failed to restart Spotify. Please restart manually.")

    def run(self):
        print("Starting Spotify Ad Blocker for Android...")
        if self.block_ads():
            print("Ad blocking rules have been added successfully")
            self.restart_spotify()
            print("Spotify has been restarted with ad blocking enabled")
            print("\nNote: To disable, restore /system/etc/hosts.backup")
        else:
            print("Failed to set up ad blocking")

def main():
    blocker = SpotifyAdBlockerAndroid()
    blocker.run()

if __name__ == "__main__":
    main()