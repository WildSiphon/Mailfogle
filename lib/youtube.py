import requests
from bs4 import BeautifulSoup

def youtubeData(username):

	# Making the request
	yt = requests.get('https://www.youtube.com/feeds/videos.xml?user=' + username)

	if yt.status_code == 404:	# Not found
		return None

	elif yt.status_code == 200:	# Found

		# Prepare to parse informations
		ytDataRaw = BeautifulSoup(yt.text, 'html.parser')
		ytDatas = {}

		# Get informations of the account
		ytDatas['username'] = username
		ytDatas['channel'] = ytDataRaw.title.string
		ytDatas['url'] = ytDataRaw.title.find_next_sibling('link').get('href')
		ytDatas['creation'] = ytDataRaw.published.string
		
		# Get informations of each video
		videos = []
		for vid in ytDataRaw.find_all('entry'):
			video = {}

			# Add the information to a dict
			video['title'] = vid.find('title').string
			video['link'] = vid.find('link').get('href')
			video['thumbnail'] = vid.find('media:group').find('media:thumbnail').get('url')
			video['description'] = vid.find('media:group').find('media:description').string
			video['published'] = vid.find('published').string
			video['updated'] = vid.find('updated').string
			video['views'] = int(vid.find('media:group').find('media:community').find('media:statistics').get('views'))
			video['thumbUp'] = int(vid.find('media:group').find('media:community').find('media:starrating').get('count'))

			# If some people put a 'Thumb up' to the video, YouTube give a note based on a ratio of thumbs up and down ('star')
			if video['thumbUp'] != '0':
				video['stars'] = float(vid.find('media:group').find('media:community').find('media:starrating').get('average'))

			# Add the informations of the video to an array of dict
			videos.append(video)

		# Add the array to the datas
		ytDatas['videos'] = videos
		
		# Return the datas
		return ytDatas

	else:					# Unknown error
		print('\n\t\tUnknown error occurred during YouTube data processing')
		return -1