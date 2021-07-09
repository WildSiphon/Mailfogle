# Configure API

Create a new project on https://console.cloud.google.com/ and add `People API` to it :

+ Click on `Select a project` then `NEW PROJECT`. Choose a name and create it 

<img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709103322107.png" alt="image-20210709103322107"  />

<img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709103420711.png" alt="image-20210709103420711"/>

<img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709103556282.png" alt="image-20210709103556282"  />

+ Go to API Dashboard and click on `+ Enable APIS AND SERVICES`

<img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709103833952.png" alt="image-20210709103833952"/>

+ Search for `Google People API` and enable it

<img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709104011761.png" alt="image-20210709104011761"/>

+ In `CREDENTIALS` panel, click on `CONFIGURE CONSENT SCREEN` and fill the form

  <img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709104455277.png" alt="image-20210709104455277"/>

  <img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709104613811.png" alt="image-20210709104613811" style="zoom:150%;" />

+ Go back to `CREDENTIALS` and in menu `+ CREATE CREDENTIALS` click `Create OAuth client ID` (choose `Web application`) 

<img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709104933036.png" alt="image-20210709104933036"/>

+ Now `ID clients OAuth 2.0` will be generated

  <img src="/home/siphon/Dropbox/Informatique/OSINT/Tools/Mailfogle/assets/configureAPI/image-20210709105208170.png" alt="image-20210709105208170"/>

+ Click on the download icon, rename the file `credentials.json` and place it in the same folder as the project