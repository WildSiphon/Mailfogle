from __future__ import print_function
import os.path,requests,json
from time import sleep
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/contacts']

def connect():
	creds = None

	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

	global service
	service = build('people', 'v1', credentials=creds)

def importContact(mail):
	service.people().createContact(body={'emailAddresses': [{'value': mail}]}).execute()

def importMails(apiFlag):
	mails = open('emails.txt', 'r').readlines()
	for i in range(len(mails)):
		mails[i] = mails[i].replace('\n','')
		if apiFlag:
			importContact(mails[i])
	return mails
		
def ytData(username):
	print('\tYouTube : User \'' + username + '\'',end=' ')
	yt = requests.get('https://www.youtube.com/feeds/videos.xml?user=' + username)
	if yt.status_code == 404:
		print('not found')
		return None
	elif yt.status_code == 200:
		print('found!')
		ytDataRaw = BeautifulSoup(yt.text, 'html.parser')
		ytDatas = {}
		ytDatas['channel'] = ytDataRaw.title.string
		ytDatas['url'] = ytDataRaw.title.find_next_sibling('link').get('href')
		ytDatas['creation'] = ytDataRaw.published.string
		videos = []
		for vid in ytDataRaw.find_all('entry'):
			video = {}
			video['title'] = vid.find('title').string
			video['link'] = vid.find('link').get('href')
			video['thumbnail'] = vid.find('media:group').find('media:thumbnail').get('url')
			video['description'] = vid.find('media:group').find('media:description').string
			video['published'] = vid.find('published').string
			video['updated'] = vid.find('updated').string
			video['views'] = int(vid.find('media:group').find('media:community').find('media:statistics').get('views'))
			video['thumbUp'] = int(vid.find('media:group').find('media:community').find('media:starrating').get('count'))
			if video['thumbUp'] != '0':
				video['stars'] = float(vid.find('media:group').find('media:community').find('media:starrating').get('average'))
			videos.append(video)
		ytDatas['videos'] = videos

		views = 0
		for video in ytDatas['videos']:
			views += video['views']
		print('\t\tChannel \'' + ytDatas['channel'] + '\' created ' + ytDatas['creation'][:len(ytDatas['creation'])-6].replace('T',' '))
		print('\t\t' + ytDatas['url'])
		print('\t\t' + str(views) + ' cumulative views on ' + str(len(ytDatas['videos'])) + ' posted video(s) found')
		return ytDatas
	else:
		print('\n\t\tUnknown error occurred during data processing')
		return -1		

def main():

	apiFlag = False
	try:
		connect()
		apiFlag = True
		print('Connected to Google people API')
	except:
		print('Cannot connect to Google people API')

	mails = importMails(apiFlag)

	datas = []
	if apiFlag:
		while True:
			results = service.people().connections().list(
				resourceName='people/me',
				personFields='names,photos,emailAddresses,metadata').execute()
			connections = results.get('connections', [])

			for person in connections:
				data = {}
				mail = person['emailAddresses'][0]['value']
				if mail in mails:
					print('\n' + mail + ' :',end=' ')
					data['mail'] = mail
					if len(person['metadata']['sources']) > 1:
						data['userTypes'] = person['metadata']['sources'][1]['profileMetadata']['userTypes']
						data['googleID'] = person['metadata']['sources'][1]['id']
						data['profilePic'] = person['photos'][0]['url']
						data['maps'] = 'https://www.google.com/maps/contrib/' + data['googleID']
						print(data['userTypes'][0])
						print('\tGoogle ID : ' + data['googleID'])
						print('\tProfile picture : ' + data['profilePic'])
						print('\tMaps Contributions & Reviews : ' + data['maps'])
					else:
						print('Not a Google user')

					ytDatas = ytData(mail.split('@')[0])
					data['youtube'] = ytDatas

					service.people().deleteContact(resourceName=person['resourceName']).execute()
					mails.pop(mails.index(mail))

					datas.append(data)

			if len(mails) == 0:
				break

			sleep(2)
	else:
		for mail in mails:
			print('\n' + mail + ' : ')
			ytDatas = ytData(mail.split('@')[0])
			datas.append(ytDatas)

	with open(('./output'),'w') as f:
		json.dump(datas,f)

if __name__ == '__main__':
	main()
