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

	# Check if 'token.json' exist or not
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in
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

	# Create service
	global service
	service = build('people', 'v1', credentials=creds)

def importContact(mail):
	# Import the mail as a contact to the account
	service.people().createContact(body={'emailAddresses': [{'value': mail}]}).execute()

def importMails(apiFlag):
	# get all the contacts written in 'emails.txt' file
	mails = open('emails.txt', 'r').readlines()
	for i in range(len(mails)):
		mails[i] = mails[i].replace('\n','')
		# If API is enabled, import them as contact
		if apiFlag: importContact(mails[i])
	# Return the list 
	return mails

def printInformations(datas):
	# Print if the account exist on Google
	print(f"\n{datas['mail']} : {'NOT A GOOGLE USER' if 'userTypes' not in datas else ', '.join([ut.replace('_',' ') for ut in datas['userTypes']])}\n")

	# If it exists
	if 'userTypes' in datas:
		# Print name found from google maps scrapping
		if 'name' in datas: print(f"\tName : {datas['name']}")
		# Print general infos
		print(f"\tGoogle ID : {datas['googleID']}\n\tProfile picture : {datas['profilePic']}")

		# If infos were scrapped from maps, print them
		if 'maps' in datas:
			print(f"\n\tMaps Contributions & Reviews ({datas['maps']['url']})")

			if 'localGuide' in datas['maps']: # If the target is a Local guide
				print(f"\t\tLocal Guide level {datas['maps']['localGuide']['level']} with {datas['maps']['localGuide']['points']} points")

			# Print informations scrapped with selenium if it worked
			if isinstance(datas['maps']['contributions'],dict):
				# Count the total of contributions
				nbContrib = sum(datas['maps']['contributions'][what] for what in datas['maps']['contributions'])
				print(f"\t\t{nbContrib} contributions including "
						+ f"{datas['maps']['contributions']['reviews']+datas['maps']['contributions']['ratings']} reviews & ratings and "
						+ f"{datas['maps']['contributions']['photos']+datas['maps']['contributions']['videos']} medias")
				# Count the number of contributions scrapped
				count = 0
				if datas['maps']['contributions']['photos'] or datas['maps']['contributions']['videos']:
					count = sum(len(c['medias']) for c in datas['maps']['medias']['content'])
				print(f"\t\t\t" + ' '*len(str(nbContrib)) + f"scrapped in fact {len(datas['maps']['reviews']) if 'reviews' in datas['maps'] else 0} reviews & ratings and {count} medias")
			# print informations scrapped if selenium did not work
			else:
				print(f"\t\t{datas['maps']['contributions']} contributions /!\\ This data is sometimes wrong. Configure Selenium to scrap more accurate informations /!\\")
		else:
			print('\n\tGoogle maps profile is private, can\'t scrap informations from it')

	# If YouTube channel found, print informations scrapped
	if 'youtube' in datas:
		print(f"\tYouTube : User \'{datas['youtube']['username']}\' found /!\\ Maybe not the one you're looking for /!\\")
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
	# If API is enabled
	if apiFlag:
		while True:
			# Download all the contacts
			results = service.people().connections().list(
				resourceName='people/me',
				personFields='names,photos,emailAddresses,metadata').execute()
			connections = results.get('connections', [])

			# Iterate all the contacts downloaded
			for person in connections:
				data = {}
				# Get the current mail of contact
				mail = person['emailAddresses'][0]['value']
				# If the part of the one we're looking for, scrap informations
				if mail in mails:
					data['mail'] = mail
					# If the contact is a GOOGLE USER
					if len(person['metadata']['sources']) > 1:
						data['userTypes'] = person['metadata']['sources'][1]['profileMetadata']['userTypes']
						data['googleID'] = person['metadata']['sources'][1]['id']
						data['profilePic'] = person['photos'][0]['url']

						# Try to get maps infos
						mpDatas = mapsData('https://www.google.com/maps/contrib/' + data['googleID'])
						if mpDatas: # If profile is public
							data['maps'] = mpDatas
							# Add te name found with maps to generals infos
							data['name'] = data['maps']['name']
							data['maps'].pop('name')

					# Try to find a YouTube channel
					ytDatas = youtubeData(mail.split('@')[0])
					if ytDatas:	data['youtube'] = ytDatas

					# Print a console version of infos
					printInformations(data)

					# Delete the contact from list
					service.people().deleteContact(resourceName=person['resourceName']).execute()
					mails.pop(mails.index(mail))

					# Add the data found to big dict
					datas.append(data)

			# Break if no more mails to verify
			if len(mails) == 0:
				break

			# Do it again if mails we were looking for were not downloaded
			sleep(2)

	# If API is not enabled
	else:
		# For each mail, try to find YouTube channel
		for mail in mails:
			print('\n' + mail + ' : ')
			ytDatas = youtubeData(mail.split('@')[0])
			datas.append(ytDatas)

	# Save all the informations in YouTube channel
	with open(('./output.json'),'w') as f:
		json.dump(datas,f)

if __name__ == '__main__':
	main()