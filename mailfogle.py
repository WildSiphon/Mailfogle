import os.path,json
from time import sleep
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from lib.maps import mapsData
from lib.youtube import youtubeData

def connect():
	SCOPES = ['https://www.googleapis.com/auth/contacts']
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

def printInformations(datas):

	print(f"\n{datas['mail']} : {'NOT A GOOGLE USER' if 'userTypes' not in datas else ', '.join([ut.replace('_',' ') for ut in datas['userTypes']])}\n")

	if 'userTypes' in datas:

		if 'name' in datas: print(f"\tName : {datas['name']}")
		print(f"\tGoogle ID : {datas['googleID']}\n\tProfile picture : {datas['profilePic']}")

		if 'maps' in datas:
			print(f"\n\tMaps Contributions & Reviews ({datas['maps']['url']})")

			if 'localGuide' in datas['maps']:
				print(f"\t\tLocal Guide level {datas['maps']['localGuide']['level']} with {datas['maps']['localGuide']['points']} points")

			if isinstance(datas['maps']['contributions'],dict):
				nbContrib = sum(datas['maps']['contributions'][what] for what in datas['maps']['contributions'])
				print(f"\t\t{nbContrib} contributions including "
						+ f"{datas['maps']['contributions']['reviews']+datas['maps']['contributions']['ratings']} reviews & ratings and "
						+ f"{datas['maps']['contributions']['photos']+datas['maps']['contributions']['videos']} medias")
				count = 0
				if datas['maps']['contributions']['photos'] or datas['maps']['contributions']['videos']:
					count = sum(len(c['medias']) for c in datas['maps']['medias']['content'])
				print(f"\t\t\t" + ' '*len(str(nbContrib)) + f"scrapped in fact {len(datas['maps']['reviews']) if 'reviews' in datas['maps'] else 0} reviews & ratings and {count} medias")
			else:
				print(f"\t\t{datas['maps']['contributions']} contributions /!\\ This data is sometimes wrong. Configure Selenium to scrap more accurate informations /!\\")
		else:
			print('\n\tGoogle maps profile is private, can\'t scrap informations from it')

	if 'youtube' in datas:
		print(f"\n\tYouTube : User \'{datas['youtube']['username']}\' found /!\\ Maybe not the one you're looking for /!\\")
		print(f"\t\tChannel \'{datas['youtube']['channel']}\' created {datas['youtube']['creation'][:len(datas['youtube']['creation'])-6].replace('T',' ')}")
		print(f"\t\t{datas['youtube']['url']}")
		print(f"\t\t{sum(video['views'] for video in datas['youtube']['videos'])} cumulative views on {len(datas['youtube']['videos'])} posted video(s) found")

def main():

	# Try to connect to the Google People API and return a flag if a connection is established
	apiFlag = False
	try:
		connect()
		apiFlag = True
		print(f'Connected to Google people API')
	except:
		print(f'Cannot connect to Google people API')

	# Import contact from the 'emails.txt' file (+ to the contact's list of the account if API connected)
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
					data['mail'] = mail
					if len(person['metadata']['sources']) > 1:
						data['userTypes'] = person['metadata']['sources'][1]['profileMetadata']['userTypes']
						data['googleID'] = person['metadata']['sources'][1]['id']
						data['profilePic'] = person['photos'][0]['url']

						mpDatas = mapsData('https://www.google.com/maps/contrib/' + data['googleID'])
						if mpDatas:
							data['maps'] = mpDatas
							data['name'] = data['maps']['name']
							data['maps'].pop('name')

					ytDatas = youtubeData(mail.split('@')[0])
					if ytDatas:	data['youtube'] = ytDatas

					printInformations(data)

					service.people().deleteContact(resourceName=person['resourceName']).execute()
					mails.pop(mails.index(mail))

					datas.append(data)

			if len(mails) == 0:
				break

			sleep(2)
	else:
		for mail in mails:
			print('\n' + mail + ' : ')
			ytDatas = youtubeData(mail.split('@')[0])
			datas.append(ytDatas)

	with open(('./output.json'),'w') as f:
		json.dump(datas,f)

if __name__ == '__main__':
	main()