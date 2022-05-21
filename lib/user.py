from lib.maps_scraper import MapsScraper
from lib.youtube_scraper import YoutubeScraper


class User:
    def __init__(
        self, browser, mail=None, user_type=None, google_ID=None, profile_pic=None
    ):
        self.mail = mail
        self.user_type = user_type
        self.google_ID = google_ID
        self.profile_pic = profile_pic
        self.username = self.mail.split("@")[0]

        self.data_maps = MapsScraper(
            google_ID=google_ID,
            browser=browser,
        )
        # try:
        self.data_maps.scrap_data()
        # except Exception as e:
        #     print(e)            

        try:
            self.data_youtube = YoutubeScraper(self.username)
        except Exception as e:
            print(e)

        self.print_informations()

    def print_informations(self):
        self._print_global_info()
        self._print_maps_info()
        self._print_youtube_info()

    def _print_global_info(self):
        print(
            f"\n{self.mail} : "
            f"{self.user_type if self.user_type else 'NOT A GOOGLE USER'}\n"
        )
        if self.name:
            print(f"\tName : {self.name}")
        if self.google_ID:
            print(f"\tGoogle ID : {self.google_ID}")
        if self.profile_pic:
            print(f"\tProfile picture : {self.profile_pic}")

    def _print_maps_info(self):
        if not self.data_maps.exist:
            return

        print(f"\n\tMaps Contributions & Reviews ({self.data_maps.url})")

        if not self.data_maps.is_public:
            print("\tProfile is private, can't scrap informations from it")
            return

        if self.data_maps.local_guide:
            print(
                f"\t\tLocal Guide level {self.data_maps.local_guide['level']} with "
                f"{self.data_maps.local_guide['points']} points"
            )

        if self.data_maps.contributions:
            print(
                f"\t\t{self.data_maps.nb_contributions} contributions including "
                f"{self.data_maps.nb_displayed_reviews_ratings} reviews & ratings and "
                f"{self.data_maps.nb_displayed_medias} medias"
            )
            print(
                "\t\t\t"
                + " " * len(str(self.data_maps.nb_contributions))
                + f"scrapped in fact {self.data_maps.nb_reviews_ratings} "
                f"reviews & ratings and {self.data_maps.nb_medias} medias"
            )

    def _print_youtube_info(self):
        if not self.data_youtube.found:
            print(f'\n\tYouTube : User "{self.username}" not found')
            return

        print(f'\n\tYouTube : User "{self.data_youtube.username}" found !')
        creation = self.data_youtube.creation
        creation_date = creation[: len(creation) - 6].replace("T", " ")
        print(
            f'\t\tChannel named "{self.data_youtube.channel}" '
            f"created {creation_date}"
        )
        print(f"\t\t{self.data_youtube.url}")
        print(
            f"\t\t{sum(video['views'] for video in self.data_youtube.videos)} "
            f"cumulative views on {len(self.data_youtube.videos)} "
            "last posted video(s)"
        )

    def as_dict(self):
        data = {"mail": self.mail}
        if self.name:
            data["name"] = self.name
        if self.user_type:
            data["user_type"] = self.user_type
        if self.google_ID:
            data["google_ID"] = self.google_ID
        if self.profile_pic:
            data["profile_pic"] = self.profile_pic
        if self.data_maps:
            data["maps"] = self.data_maps.as_dict()
        if self.data_youtube:
            data["youtube"] = self.data_youtube.as_dict()
        return data

    @property
    def name(self):
        return self.data_maps.name
