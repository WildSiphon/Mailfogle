import requests

from bs4 import BeautifulSoup


class YoutubeScraper:
    def __init__(self, username):
        self.username = username
        self.url = f"https://www.youtube.com/feeds/videos.xml?user={self.username}"

        self.found = None

        self.channel = None
        self.creation = None
        self.videos = None
        self._scrap_data()

    def _scrap_data(self):
        # Making the request
        youtube_request = requests.get(self.url)

        if youtube_request.status_code == 404:  # Not found
            self.found = False

        elif youtube_request.status_code == 200:  # Found

            html = BeautifulSoup(youtube_request.text, "html.parser")

            # Get informations of the account
            self.channel = html.title.string
            self.url = html.title.find_next_sibling("link").get("href")
            self.creation = html.published.string

            # Get informations of each video
            videos = []
            for vid in html.find_all("entry"):
                video = {}

                video["title"] = vid.find("title").string
                video["link"] = vid.find("link").get("href")
                video["thumbnail"] = (
                    vid.find("media:group").find("media:thumbnail").get("url")
                )
                video["description"] = (
                    vid.find("media:group").find("media:description").string
                )
                video["published"] = vid.find("published").string
                video["updated"] = vid.find("updated").string
                video["views"] = int(
                    vid.find("media:group")
                    .find("media:community")
                    .find("media:statistics")
                    .get("views")
                )
                video["thumbUp"] = int(
                    vid.find("media:group")
                    .find("media:community")
                    .find("media:starrating")
                    .get("count")
                )

                # YouTube give a note based on a ratio of thumbs up and down ('star')
                if video["thumbUp"] != "0":
                    video["stars"] = float(
                        vid.find("media:group")
                        .find("media:community")
                        .find("media:starrating")
                        .get("average")
                    )

                videos.append(video)

            self.videos = videos

    def as_dict(self):
        data = {"username": self.username}

        if self.found:
            data["url"] = self.url
        if self.channel:
            data["channel"] = self.channel
        if self.url:
            data["url"] = self.url
        if self.creation:
            data["creation"] = self.creation
        if self.videos:
            data["videos"] = self.videos
        return data
