# Mailfogle

OSINT tool allowing the exploration of a user's public data from a Google email address (gmail, googlemail) to find YouTube account, Google Maps Contributions informations and more.

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png" alt="bulb" style="zoom:33%;" /> The script

### Needs

To access all the features :

+ **Google account**
+ **Google People API** 

### Operation

This script does :

- **connect** to `People API` via your Google account
- **add the emails** to dig to your account's contact list
- **download the contact list** to get all the ***Google ID***
- **find stuff** using the ***Google ID*** given by Google
- **search for a YouTube account** corresponding to the *username* of the email address
- **delete the email address** of your account's contact list at the end

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f6e0.png" alt="hammer_and_wrench" style="zoom:33%;" /> Installation

### Download files and dependencies

```bash
git clone https://github.com/WildSiphon/Gexplorer.git
cd Gexplorer
pip3 install -r requirements.txt
```

### Configure API

Create a new project on https://console.cloud.google.com/ and add `People API` to it.

Generate `ID clients OAuth 2.0` and download them. Rename the file `credentials.json` and place it in the same folder. 

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4c8.png" alt="chart_with_upwards_trend" style="zoom:33%;" />Use

### Usual use

Write the addresses to explore in the `emails.txt` file.

```
test@gmail.com
larry.page@gmail.com
```

Then run the script.

```bash
python3 mailfogle.py
```

<img src="./demo/demo.gif" alt="demo" style="zoom:75%;" />

### First use

The first time you will use it, you will be asked to log into a Google account. Once the permissions to edit contacts are granted, the script will save the login token in `token.json`. No more connection will be required after that.

We advise you not to log into a personal account but to use an account reserved for OSINT. The script does not retrieve any of your personal information, but if it crashes for some reason, contacts added during its execution will not be deleted. 

You can still manage contacts manually [here](https://contacts.google.com/).

### Use without People API's credentials

If you can't connect to `Google People API`, you can still run the script. It will only try to find **YouTube accounts** matching the *username* in the mail address.

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4da.png" alt="books" style="zoom:33%;" />Output

The results are displayed in console, but more information are recorded and stored in `./output.json`.

### General format

| Key        | Value                                                        |
| :--------- | :----------------------------------------------------------- |
| mail       | Target email address (*string*)                              |
| userTypes  | User types as sent by Google (*list of strings*)             |
| googleID   | Google ID starting with '10' or '11' and making 21 characters (*string*) |
| profilePic | Link to the target's profile picture (*string*)              |
| maps       | Link to 'contribution & reviews' on maps by the target (you can find the name of the target here) (*string*) |
| youtube    | See after (*dict*)                                           |

### YouTube case format

#### General

| Key      | Value                                           |
| -------- | ----------------------------------------------- |
| channel  | YouTube account name (*string*)                 |
| url      | Link to the channel (*string*)                  |
| creation | Creation date of the YouTube account (*string*) |
| videos   | See after (*list of dict*)                      |

#### Videos

List of informations about each video of the channel.
| Key         | Value                                                        |
| ----------- | ------------------------------------------------------------ |
| title       | Video title (*string*)                                       |
| link        | Link to the video (*string*)                                 |
| thumbnail   | Link to video thumbnail (*string*)                           |
| description | Video description (*string* or *null* if no description)     |
| published   | Video publication date (*string*)                            |
| updated     | Video last updated date (*string*)                           |
| views       | Number of views (*int*)                                      |
| thumbUp     | Number of thumbs up (*int*)                                  |
| stars       | Number of stars (from 1 to 5 calculated according to the ratio of thumbs up and thumb down) (*float*)<br>*Not specified if the number of thumbUp is 0* |


## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4dd.png" alt="memo" style="zoom:33%;" /> Stuff to add

+ Colors in the printed output
+ A way to get the name of the person without clicking the *Google Maps Contributions* link
+ A way to scrap the data of *Google Maps Contributions*
+ A commented version of the code lol

## References

+ This article explaining a lot about Google ID : https://medium.com/week-in-osint/getting-a-grasp-on-googleids-77a8ab707e43
+ This online solution that allows you to search for only one address at a time : https://tools.epieos.com/email.php

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.fr.html)





