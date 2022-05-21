import requests

from bs4 import BeautifulSoup
from lib.selenium_wrapper import SeleniumWrapper
from time import sleep


# Global variable of the seconds to wait to be sure that content is loaded
DELAY = 5
# Set cookie for Google consent and "User Agent"
CONSENT = "YES+cb.20210622-13-p0.fr+F+528"
USER_AGENT = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
)

class MapsScraper:

    def __init__(self, browser: str, google_ID: str = ""):
        self.browser = browser

        self.exist = None
        self.is_public = None

        self.name = None
        self.local_guide = None
        self.contributions = []
        self.reviews = []
        self.medias = {}

        self.url = None
        self.google_ID = google_ID

    def as_dict(self):
        if not self.exist:
            return None

        data = {"url": self.url}
        if self.local_guide:
            data["local_guide"] = self.local_guide
        if self.contributions:
            data["contributions"] = self.contributions
        if self.reviews:
            data["reviews"] = self.reviews
        if self.medias:
            data["medias"] = self.medias
        return data

    def scrap_data(self):
        if self.google_ID == "":
            return

        self.url = f"https://www.google.com/maps/contrib/{self.google_ID}"
        self._request()

        if self.is_public:
            self.driver = SeleniumWrapper(self.browser).driver
            # try:
            self._selenium_scrap()
            # except:
            #     msg = "Google Maps layout has changed. This tool may be outdated."
            #     # TODO custom exception
            #     raise Exception(msg)
            # finally:
            self.driver.quit()

    def _request(self):
        # Setting up the request
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
        consent_cookie = requests.cookies.create_cookie(
            domain=".google.com", name="CONSENT", value=CONSENT
        )
        session.cookies.set_cookie(consent_cookie)

        # Making the request
        maps_request = session.get(self.url)
        if maps_request.status_code == 404:
            self.exist = False
        elif maps_request.status_code == 200:
            self.exist = True
            self._minimal_scrap(BeautifulSoup(maps_request.text, "html.parser"))

    def _minimal_scrap(self, html):
        title = html.find("meta", attrs={"property": "og:title"})["content"].split(
            "by "
        )
        if len(title) != 1:
            self.is_public = True
            self.name = title[1]
        else:
            self.is_public = False
            return

        description = html.find("meta", attrs={"property": "og:description"})[
            "content"
        ].split(" Local Guide | ")
        if len(description) != 1:
            self.local_guide = {
                "level": int(description[0].replace("Level ", "")),
                "points": int(description[1].replace(" Points", "").replace(",", "")),
            }
        else:
            self.contributions = int(
                description[0]
                .replace(" Contributions", "")
                .replace(" Contribution", "")
            )

    def _selenium_scroll(self, here):
        # Define end of scrolling
        element = here.find_elements_by_xpath(
            "//div[@data-review-id] | //div[@data-photo-bucket-id]"
        )
        if not element:
            return

        element = element[-1]
        while True:
            # Scroll
            element.location_once_scrolled_into_view
            # Be sure to load the page
            sleep(3)
            # Find last <div> of the section
            nextElement = here.find_elements_by_xpath(
                "//div[@data-review-id] | //div[@data-photo-bucket-id]"
            )[-1]
            # Do it again if not at the end, else break the loop
            if nextElement == element:
                return
            element = nextElement

    def _selenium_scrap(self):

        # Open URL with Selenium
        self.driver.get(self.url)

        # Be sure to load the page
        sleep(DELAY)

        # Scrap contribution panel
        self._scrap_contributions()  

        # Be sure to load the page
        sleep(DELAY)

        # Checking if there are some ratings or reviews to scrap
        if self.contributions["reviews"] or self.contributions["ratings"]:
            # Scrap ratings and reviews
            self._scrap_ratings_reviews()

        # Check if there are some media to scrap to
        if self.contributions["photos"] or self.contributions["videos"]:
            # Going back to photos panel
            medias_panel = self.driver.find_elements_by_xpath(
                "//div[@role='tablist']/button[2]"
            )[0]
            medias_panel.click()

            # Be sure to load the page
            sleep(DELAY)

            # Scroll in the layout section to load all the medias to scrap
            divs = self.driver.find_elements_by_xpath("//div")
            layout_section = [
                scrollbox_section
                for scrollbox_section in divs
                if "section-scrollbox" in scrollbox_section.get_attribute("class")
            ][0]
            self._selenium_scroll(layout_section)

            try:
                # Scrap the number of times the medias has been seen by people
                self.medias["views"] = int(
                    layout_section.find_elements_by_xpath("div")[0]
                    .text.replace("\u202f", "")
                    .split("\n")[0]
                    .split(" ")[1]
                )
                self.medias = {}
            except IndexError:
                # Medias are mentioned in contributions panel but none are scrapable
                return

            # Scrap each post with media
            self.medias["content"] = []
            for content in layout_section.find_elements_by_xpath(
                ".//div[@role='button']"
            ):
                media = {}
                media["medias"] = []

                # Get the place and the address of the post
                place_and_address = content.text.split("\n")

                # Add the place and the address
                media["place"] = place_and_address[0]
                try:  # When place is "Unknown place" but had medias posted on it
                    media["address"] = place_and_address[1]
                except:
                    pass

                # For each media in the post
                for med in content.find_elements_by_xpath(".//jsl"):

                    # If the media is picture, "play button" is not displayed
                    if (
                        med.find_elements_by_xpath("./div/div")[-1].get_attribute(
                            "style"
                        )
                        == "display: none;"
                    ):

                        img = None
                        while not img:  # Waiting the picture to be loaded
                            try:
                                img = med.find_elements_by_xpath(".//img")[
                                    0
                                ].get_attribute("src")
                            except:
                                pass

                        # Add its source to the array
                        media["medias"].append(img)

                    else:  # The media is a video

                        # Click on the thumbnail to load the video in a new iFrame
                        med.find_elements_by_xpath(".//img/..")[0].click()

                        # Be sure to load the iFrame
                        sleep(DELAY)

                        # Find the iFrame and switch to it
                        iframe = self.driver.find_elements_by_xpath(
                            "//iframe[@class='widget-scene-imagery-iframe']"
                        )[0]
                        self.driver.switch_to.frame(iframe)

                        vid = None
                        while not vid:  # Waiting the video to be loaded
                            try:
                                vid = self.driver.find_elements_by_xpath("//video")[
                                    0
                                ].get_attribute("src")
                            except:
                                pass

                        # Switch back to the default DOM
                        self.driver.switch_to.default_content()

                        # Add its source to the array
                        media["medias"].append(vid)

                self.medias["content"].append(media)

    def _scrap_contributions(self):
        # Open contributions panel
        contributions = self.driver.find_elements_by_xpath(
            "//span[@jsaction='pane.profile-stats.showStats;keydown:pane.profile-stats.showStats']"
        )[0]
        contributions.click()

        # Be sure to load the page
        sleep(DELAY)

        # Get informations from the contribution panel
        contributions_content = self.driver.find_elements_by_xpath(
            "//div[@id='modal-dialog']//h1/../../div"
        )
        contributions_header = contributions_content[0]
        contributions_points = contributions_content[2]
        contributions_stats = contributions_content[3].text.split("\n")[1::2]

        # Scrap 'Level' and 'Points' if target is a 'Local Guide'
        if contributions_points.text:
            self.local_guide = {}
            self.local_guide["level"] = int(contributions_header.text.split()[-1])
            self.local_guide["points"] = int(
                contributions_points.text.replace("\u202f", "").split("\n")[0]
            )

        # Add all the differents contributions statistics to a list
        self.contributions = {}
        self.contributions["reviews"] = int(contributions_stats[0])
        self.contributions["ratings"] = int(contributions_stats[1])
        self.contributions["photos"] = int(contributions_stats[2])
        self.contributions["videos"] = int(contributions_stats[3])
        self.contributions["answers"] = int(contributions_stats[4])
        self.contributions["edits"] = int(contributions_stats[5])
        self.contributions["placesAdded"] = int(contributions_stats[6])
        self.contributions["roadsAdded"] = int(contributions_stats[7])
        self.contributions["factsChecked"] = int(contributions_stats[8])
        self.contributions["q&a"] = int(contributions_stats[9])
        self.contributions["publishedLists"] = int(contributions_stats[10])

        # Close contributions panel
        self.driver.find_elements_by_xpath(
            "//div[@id='modal-dialog']//button[@jsaction='modal.close']"
        )[0].click()

    def _scrap_ratings_reviews(self):
        # Click on the review's panel
        review_panel = self.driver.find_elements_by_xpath(
            "//div[@role='tablist']/button[1]"
        )[0]
        review_panel.click()

        # Be sure to load the page
        sleep(DELAY)


        # Scroll in the layout section to load all the reviews to scrap
        layout_section = self.driver.find_elements_by_xpath("//div[@role='main']/div[@tabindex]")[0]
        self._selenium_scroll(layout_section)

        # Scrap each review
        self.reviews = []
        for mpReview in layout_section.find_elements_by_xpath(
            "//div[@role='button']/div[@data-review-id]"
        ):
            review = {}
            # Separate title from content
            title = mpReview.find_elements_by_xpath("div[@class]/div[@class]")[
                0
            ].text.split("\n")
            content = mpReview.find_elements_by_xpath("div[@class]/div[@class]")[2]

            # Click on the 'Plus' button to load all the text
            plus_button = content.find_elements_by_xpath("//jsl/button")
            if plus_button:
                plus_button[0].click()

            # From title
            review["place"] = title[0]
            if len(title) > 1:
                review["address"] = title[1]

            # From content
            first_line = content.find_elements_by_xpath("./div")
            if isinstance(first_line, list):
                first_line = first_line[0]

            # Elements always in content
            review["stars"] = int(
                first_line.find_elements_by_xpath("./span[@class]")[0]
                .get_attribute("aria-label")
                .split("\xa0")[0]
                .replace(" ", "")
            )
            review["when"] = first_line.find_elements_by_xpath("./span[@class]")[
                1
            ].text

            # Elements not there every time
            try:  # Comment of the target
                next_line = first_line.find_elements_by_xpath("../div[@class]")[1]
                if next_line.text != "":
                    review["comment"] = next_line.text
            except:
                pass
            try:  # "Visited in..." or "Owner's Response"
                next_line = next_line.find_elements_by_xpath("../div[@class]")[3]
                # Case with "Like" & "Share" instead of "Visited in..."
                if not next_line.find_elements_by_xpath("./button"):
                    # Case with "Owner's response" instead of "Visited in..."
                    if "title" not in next_line.find_elements_by_xpath("./span")[
                        0
                    ].get_attribute("class"):
                        review["visited"] = next_line.text
                    else:
                        review["ownersResponse"] = next_line.text
            except:
                pass

            self.reviews.append(review)

    @property
    def nb_contributions(self):
        return sum(self.contributions[what] for what in self.contributions)

    @property
    def nb_medias(self):
        if "content" not in self.medias:
            return 0
        return sum(len(c["medias"]) for c in self.medias["content"])

    @property
    def nb_reviews_ratings(self):
        return len(self.reviews)

    @property
    def nb_displayed_reviews_ratings(self):
        return self.contributions["reviews"] + self.contributions["ratings"]

    @property
    def nb_displayed_medias(self):
        return self.contributions["photos"] + self.contributions["videos"]
