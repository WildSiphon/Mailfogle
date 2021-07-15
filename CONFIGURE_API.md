# Configure API

## Platform

Go to to https://console.cloud.google.com/ and connect with a google account.

## Creation of a project

+ Click on `Select a project` then `NEW PROJECT`

<img src="./assets/configureAPI/project-selectnew.png" alt="project-selectnew"  />

+ Choose a name and create it

 <img src="./assets/configureAPI/project-create.png" alt="project-create"/>

+ You should see a notification which says that the project has been correctly created

 <img src="./assets/configureAPI/project-creatednotification.png" alt="project-creatednotification"/>

## Adding Google People API

+ Go to API Dashboard

 <img src="./assets/configureAPI/GPAPI-dashboard.png" alt="GPAPI-dashboard"/>

+ Click on `+ Enable APIS AND SERVICES`

<img src="./assets/configureAPI/GPAPI-enableAPIandservices.png" alt="GPAPI-enableAPIandservices"/>

+ Search for `Google People API`

<img src="./assets/configureAPI/GPAPI-searchpeople.png" alt="GPAPI-searchpeople"/>

+ Click on the first result

<img src="./assets/configureAPI/GPAPI-findpeople.png" alt="GPAPI-findpeople"/>

+ Enable `Google People API`

 <img src="./assets/configureAPI/GPAPI-enablepeople.png" alt="GPAPI-enablepeople"/>

+ You should see a notification which says that the API has been correctly enabled

<img src="./assets/configureAPI/GPAPI-enabledpeoplenotification.png" alt="GPAPI-enabledpeoplenotification"/>

## Configuration of the API


+ Go back to API Dashboard and click on `OAuth consent screen`. You will be asked to choose a `User Type`. Select `External`

 <img src="./assets/configureAPI/configuration-externaluse.png" alt="configuration-externaluse"/>

+ Fill the `OAuth consent screen` forms with your informations

 <img src="./assets/configureAPI/configuration-registration1.png" alt="configuration-registration1"/>

 <img src="./assets/configureAPI/configuration-registration2.png" alt="configuration-registration2"/>

+ Pass the `Scopes` forms

 <img src="./assets/configureAPI/configuration-registrationscopes.png" alt="configuration-registrationscopes"/>

+ Add a test user

<img src="./assets/configureAPI/configuration-registrationtestuser.png" alt="configuration-registrationtestuser"/>

+ Click `Back to dashboard` on `Summary` panel

## Getting credentials

+ In the `CREDENTIALS` panel, in menu `CREATE CREDENTIALS` select  `Create OAuth client ID` 

<img src="./assets/configureAPI/credentials-create.png" alt="credentials-create"/>

+ Configure `OAuth` for `Desktop app` then create it

 <img src="./assets/configureAPI/credentials-oauth.png" alt="credentials-oauth"/>

+ Click on `DOWNLOAD JSON`, rename the file `credentials.json` and place it in the same folder as the project

<img src="./assets/configureAPI/credentials-oauthdl.png" alt="credentials-oauthdl"/>