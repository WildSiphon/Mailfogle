from lib.seleniumWrapper import Selenium
from bs4 import BeautifulSoup
from time import sleep
import requests

DELAY = 2 # Global variable of the seconds to wait to be sure that content is loaded

def scrapMinInfos(html):

	# Creating object to return scrapped datas from maps
	mapsDataMin = {}

	# Find <meta>
	for prop in html.find_all('meta'):
		# If they have attribute 'property'
		if prop.get('property'):
			# Where the name would be
			if prop['property'] == 'og:title':
				name = prop['content'].split('by ')
				# Public account
				if len(name) != 1: mapsDataMin['name'] = name[1]
				# Anonymous account
				else: return {}
			# 'Contributions' (May not be accurate) or 'LocalGuide'
			if prop['property'] == 'og:description':
				mapsDataMin['contributions'] = prop['content'].lower()

	# Return datas
	if mapsDataMin:	return mapsDataMin
	else:	return None

def requestMaps(url):

	# Set "User Agent" and cookie for Google consent 
	USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
	CONSENT = 'YES+cb.20210622-13-p0.fr+F+528'
	
	# Setting up the request
	session = requests.Session()
	session.headers.update({'User-Agent':USER_AGENT})
	consentCookie = requests.cookies.create_cookie(domain='.google.com',name='CONSENT',value=CONSENT)
	session.cookies.set_cookie(consentCookie)

	# Making the request
	mp = session.get(url)	
	if mp.status_code == 404: return None	# Not found
	elif mp.status_code == 200:				# Found
		mpDataRaw = BeautifulSoup(mp.text, 'html.parser')
		mpDatas = scrapMinInfos(mpDataRaw)
		return mpDatas
	else:									# Unknown error
		print('\n\t\tUnknown error occurred during Maps data processing')
		return -1

def seleniumLayoutScroll(here):
	# Define end of scrolling
	element = here.find_elements_by_xpath("./div[@data-review-id] | ./div[@data-photo-bucket-id]")[-1]
	while True:
		# Scroll
		element.location_once_scrolled_into_view
		# Be sure to load the page
		sleep(3)
		# Find last <div> of the section
		nextElement = here.find_elements_by_xpath("./div[@data-review-id] | ./div[@data-photo-bucket-id]")[-1]
		# Do it again if not at the end, else break the loop
		if nextElement == element: break
		else: element = nextElement
	return

def seleniumMaps(url,browser):

	# Open URL with Selenium
	browser.get(url)

	# Automate accepting cookies
	cookies_button = browser.find_elements_by_xpath("//form[@action='https://consent.google.com/s']//button")[0]
	cookies_button.click()

	# Be sure to load the page
	sleep(DELAY)

	# Open contributions panel
	contributions = browser.find_elements_by_xpath("//span[@jsaction='pane.profile-stats.showStats;keydown:pane.profile-stats.showStats']")[0]
	contributions.click()

	# Be sure to load the page
	sleep(DELAY)

	# Creating object to return scrapped datas from maps
	mpDatas = {}

	# Scrap 'Level' and 'Points' if target is a 'Local Guide'
	if 'section-profile-stats-progressbar' in browser.find_elements_by_xpath("//div[@class='modal-dialog']/div/div")[1].get_attribute('class'):
		mpDatas['localGuide'] = {}
		mpDatas['localGuide']['level'] =  int(browser.find_elements_by_xpath("//div[@class='modal-dialog']/div/div/div/h1")[0].text.split()[-1])
		mpDatas['localGuide']['points'] =  int(browser.find_elements_by_xpath("//div[@class='modal-dialog']/div/div/div")[1].text.replace('\u202f',''))
		contributions = browser.find_elements_by_xpath("//div[@class='modal-dialog']/div/div[3]//span")
	else:
		contributions = browser.find_elements_by_xpath("//div[@class='modal-dialog']//span")

	# Add all the differents contributions to an array
	mpDatas['contributions'] = {}
	mpDatas['contributions']['reviews'] = int(contributions[2].text)
	mpDatas['contributions']['ratings'] = int(contributions[5].text)
	mpDatas['contributions']['photos'] = int(contributions[8].text)
	mpDatas['contributions']['videos'] = int(contributions[11].text)
	mpDatas['contributions']['answers'] = int(contributions[14].text)
	mpDatas['contributions']['edits'] = int(contributions[17].text)
	mpDatas['contributions']['placesAdded'] = int(contributions[20].text)
	mpDatas['contributions']['roadsAdded'] = int(contributions[23].text)
	mpDatas['contributions']['factsChecked'] = int(contributions[26].text)
	mpDatas['contributions']['q&a'] = int(contributions[29].text)
	mpDatas['contributions']['publishedLists'] = int(contributions[32].text)

	# Close contributions panel
	contributions[0].find_elements_by_xpath("//div[@class='modal-close-row']//button[@jsaction='modal.close']")[0].click()

	# Be sure to load the page
	sleep(DELAY)

	# Checking if there are some ratings or reviews to scrap
	if mpDatas['contributions']['reviews'] or mpDatas['contributions']['ratings']:

		# Click on the review's panel
		section_review = browser.find_elements_by_xpath("//div[@role='tablist']/button[1]")[0]
		section_review.click()

		# Be sure to load the page
		sleep(DELAY)

		# Scroll in the layout section to load all the reviews to scrap
		layout_section = browser.find_elements_by_xpath("//div[@class='section-layout']")[0]
		seleniumLayoutScroll(layout_section)

		# Scrap each review
		mpDatas['reviews'] = []
		for mpReview in browser.find_elements_by_xpath("//div[@class='section-layout']/div[@role='button']/div/div[@class]"):
			review = {}

			# Separate title from content
			title = mpReview.find_elements_by_xpath("./div[@class]")[0].text.split('\n')
			content = mpReview.find_elements_by_xpath("./div[@class]")[1]

			# If the comment is a big one, click on the 'Plus' button to load all the text
			plus_button = content.find_elements_by_xpath(".//jsl/button")
			if plus_button: plus_button[0].click()
			
			# From title
			review['place'] = title[0]
			review['address'] = title[1]
			
			# From content
			firstLine = content.find_elements_by_xpath("./div")[0]
			
			# Elements always in content
			review['stars'] = int(firstLine.find_elements_by_xpath("./span[@class]")[0].get_attribute('aria-label').split('\xa0')[0].replace(' ',''))
			review['when'] = firstLine.find_elements_by_xpath("./span[@class]")[1].text
			
			# Elements not there every time
			try:	# Comment of the target
				nextLine = firstLine.find_elements_by_xpath("../div[@class]")[1]
				if nextLine.text != '':
					review['comment'] = nextLine.text
			except:
				pass
			try:	# "Visited in..." or "Owner's Response"
				nextLine = nextLine.find_elements_by_xpath("../div[@class]")[3]
				# Case where there is no line "Visited in..." but "Like" & "Share" instead (we don't want that)
				if not nextLine.find_elements_by_xpath("./button"):
					# Case where there is no line "Visited in..." but "Owner's response" instead
					if 'title' not in nextLine.find_elements_by_xpath("./span")[0].get_attribute('class'):
						review['visited'] = nextLine.text
					else:
						review['ownersResponse'] = nextline.text
			except:
				pass

			mpDatas['reviews'].append(review)

	# Check if there are some media to scrap to
	if mpDatas['contributions']['photos'] or mpDatas['contributions']['videos']:
		mpDatas['medias'] = {}
		
		# Going back to photos panel
		selection_photos = browser.find_elements_by_xpath("//div[@role='tablist']/button[2]")[0]
		selection_photos.click()

		# Be sure to load the page
		sleep(DELAY)

		# Scroll in the layout section to load all the medias to scrap
		scrollbox_section = browser.find_elements_by_xpath("//div[@class='section-layout']")[0]
		seleniumLayoutScroll(scrollbox_section)

		# Scrap the number of times the medias has been seen by people
		mpDatas['medias']['views'] = int(scrollbox_section.find_elements_by_xpath("../div/div/span[2]/span")[1].text.replace('\u202f',''))

		# Scrap each post with media
		mpDatas['medias']['content'] = []
		for div in scrollbox_section.find_elements_by_xpath("./div"):
			media = {}
			media['medias'] = []

			# Get the content
			content = div.find_elements_by_xpath(".//div[@aria-label]")[0]

			# Get the place and the address of the post
			place_and_address = content.text.split('\n')
			
			# Add the place and the address
			media['place'] = place_and_address[0]
			try: # This case append only one time during tests when place was "Unknown place" but had medias posted on it
				media['address'] = place_and_address[1]
			except: pass
				
			# For each media in the post
			for med in content.find_elements_by_xpath('.//jsl'):

				# If the media is a picture the "play button" at the bottom is not displayed
				if med.find_elements_by_xpath('./div/div')[-1].get_attribute('style') == 'display: none;':

					img = None
					while not img: # Waiting the picture to be loaded
						try: img = med.find_elements_by_xpath('.//img')[0].get_attribute('src')
						except: pass

					# Add its source to the array
					media['medias'].append(img)

				else: # The media is a video

					# Click on the thumbnail to load the video in a new iFrame
					med.find_elements_by_xpath('.//img/..')[0].click()

					# Be sure to load the iFrame
					sleep(DELAY)

					# Find the iFrame and switch to it
					iframe = browser.find_elements_by_xpath("//iframe[@class='widget-scene-imagery-iframe']")[0]
					browser.switch_to.frame(iframe)

					vid = None
					while not vid: # Waiting the video to be loaded
						try: vid = browser.find_elements_by_xpath("//video")[0].get_attribute('src')
						except: pass
					
					# Switch back to the default DOM
					browser.switch_to.default_content()
					
					# Add its source to the array
					media['medias'].append(vid)
	
			mpDatas['medias']['content'].append(media)

	# Return datas
	return mpDatas

def mapsData(url,browser):

	mpDatas = requestMaps(url)
	
	if mpDatas:
		
		try:
			mpDatas['url'] = url
			selenium = Selenium(browser)
			mpDatas.update(seleniumMaps(url,selenium.driver))
			selenium.driver.quit()
		except Exception as e:
			print(e)

	return mpDatas