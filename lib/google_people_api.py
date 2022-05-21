import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GooglePeopleApi:
    def __init__(self, mails):
        self.scopes = ["https://www.googleapis.com/auth/contacts"]
        self.creds = None
        self.service = None
        self.mails = mails
        try:
            self._connect()
            print("Connected to Google people API")
            self.connected = True
            self._import_contacts()
        except:
            print("Cannot connect to Google people API")
            print("Retry after deleting 'token.json'")
            self.connected = False

    def _connect(self):
        # Check if 'token.json' exist or not
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file(
                "token.json", self.scopes
            )

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if not self.creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.scopes
                )
                self.creds = flow.run_local_server(port=0)
            elif self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        # Create service
        self.service = build("people", "v1", credentials=self.creds)

    def _import_contacts(self):
        # Import the mail as a contact to the account
        for mail in self.mails:
            self.service.people().createContact(
                body={"emailAddresses": [{"value": mail}]}
            ).execute()

    def _download_contacts(self):
        results = (
            self.service.people()
            .connections()
            .list(
                pageSize=1000,
                resourceName="people/me",
                personFields="names,photos,emailAddresses,metadata",
            )
            .execute()
        )
        return results.get("connections", [])

    def _delete_contact(self, name):
        # Sometimes the google API has trouble deleting the contact
        try:
            self.service.people().deleteContact(resourceName=name).execute()
        # Start again until it succeeds
        except:
            self._delete_contact(name)

    def get_data(self):
        connections = self._download_contacts()
        connections = list(
            filter(
                lambda contact: "emailAddresses" in contact.keys()
                and contact["emailAddresses"][0]["value"] in self.mails,
                connections,
            )
        )

        users_data = []
        for person in connections:
            user = {}
            mail = person["emailAddresses"][0]["value"]

            if mail not in self.mails:
                continue

            user["mail"] = mail

            if len(person["metadata"]["sources"]) > 1:
                sources = person["metadata"]["sources"][1]
                user["user_type"] = sources["profileMetadata"]["userTypes"][0].replace(
                    "_", " "
                )
                user["google_ID"] = sources["id"]
                user["profile_pic"] = person["photos"][0]["url"]

            self._delete_contact(person["resourceName"])
            self.mails.remove(user["mail"])

            users_data.append(user)

        return users_data
