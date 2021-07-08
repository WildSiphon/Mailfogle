# [Mailfogle](https://github.com/WildSiphon/Mailfogle)

**OSINT tool** allowing the <u>**exploration**</u> and the <u>**scrapping**</u> of a user's public data from a Google email address (gmail, googlemail) to find ***YouTube account***, ***Google Maps Contributions*** and more.

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png" alt="bulb" style="zoom:33%;" /> The script

### Needs

To access all the features (you can still use the script without) :

+ **Google account**
+ **Google People API**
+ **Selenium**

If `Selenium` is not configured, it will scrap only the *name* and the *number of contributions* from **Google Maps** public profile.
If you can't connect to `Google People API`, it will only try to find **YouTube accounts** matching the *username* in the mail address.

### Operation

This script does :

- **connect** to `People API` via a *Google account*
- **add the emails** to dig to the *account's contact list*
- **get all the *Google ID*** of the targets
- **scrap the data** of `Google Maps Contributions` if profiles are public
- **search for a YouTube account** corresponding to the *username* of the email address
- **delete the email address** of the account's contact list

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f6e0.png" alt="hammer_and_wrench" style="zoom:33%;" /> Installation

### Download files and dependencies

```bash
git clone https://github.com/WildSiphon/Mailfogle.git
cd Mailfogle
pip3 install -r requirements.txt
```

### Configure Selenium

*This script is configured to use Selenium with Firefox*

**Download** the latest `GeckoDriver` from [here](https://github.com/mozilla/geckodriver/releases) and **extract** it in `/usr/bin` (or somewhere else but must be in the `PATH`).

### Configure API

Create a new project on https://console.cloud.google.com/ and add `People API` to it.

Generate `ID clients OAuth 2.0` and download them. Rename the file `credentials.json` and place it in the same folder as the project. 

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4c8.png" alt="chart_with_upwards_trend" style="zoom:33%;" />Use

### Usual use

Write the addresses to explore in the `emails.txt` file.

```
google@gmail.com
larry.page@gmail.com
```

Then run the script.

```bash
python3 mailfogle.py
```

Demonstration using YouTube creator's names and the address (sadly none of them is related to a YouTube channel) :<img src="./demo/demo.gif" alt="demo" style="zoom:75%;" />

### First use

The first time you will use it, you will be asked to log into a Google account. Once the permissions to edit contacts are granted, the script will save the login token in `token.json`. No more connection will be required after that.

We advise you not to log into a personal account but to use an account reserved for OSINT. The script does not retrieve any of your personal information, but if it crashes for some reason, contacts added during its execution will not be deleted. 

You can still manage contacts manually [here](https://contacts.google.com/).

## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4da.png" alt="books" style="zoom:33%;" />Output

Results are displayed in console, but all the informations are recorded and stored in `./output.json`. This is much more than just what is printed on the terminal.

### Example

`output.json`

```json
[{"mail": "s*@gmail.com",
  "userTypes": ["GOOGLE_USER"],
  "name": "S* D*",
  "googleID": "11*******************",
  "profilePic": "https://lh3.googleusercontent.com/**",
  "maps": {
      "url": "https://www.google.com/maps/contrib/11*******************",
      "contributions": {"reviews": 12,"ratings": 45,"photos": 97,"videos": 2,"answers": 499,"edits": 0,"placesAdded": 0,"roadsAdded": 0,"factsChecked": 1,"q&a": 0,"publishedLists": 0},
      "localGuide": {"level": 5,"points": 1222},
      "reviews": [
          {"place": "H* P*",
          "address": "1 Cour du C* S*-A*, 7**** P*",
          "stars": 5,
          "when": "il y a 5 mois",
          "comment": "Excellent accueil et conseils. J'y retournerai avec plaisir!",
          "visited": "Visité en février"}],
      "medias": {
          "views": 722596,
          "content":[
              {"medias":[
                  "https://lh5.googleusercontent.com/p/**",
                  "https://lh5.googleusercontent.com/p/**",
                  "https://lh3.googleusercontent.com/**"],
              "place": "Restaurant S* M*",
              "address": "67 Rue des E*, 7**** P*"}]}},
  "youtube": {
      "username": "s*",
      "channel": "S*",
      "url": "https://www.youtube.com/channel/**",
      "creation": "2006-06-28T01:02:53+00:00",
      "videos":[
          {"title": "25 de mayo de 2020",
           "link": "https://www.youtube.com/**",
           "thumbnail": "https://i4.ytimg.com/vi/**.jpg",
           "description": null,
           "published": "2020-05-25T19:58:11+00:00",
           "updated": "2021-05-26T23:33:55+00:00",
           "views": 4,
           "thumbUp": 0,
           "stars": 0.0}]
}}]
```

### General format

| Key        | Value                                                        |
| :--------- | :----------------------------------------------------------- |
| mail       | Target's email address [*string*]                            |
| userTypes  | User types as sent by Google [*list of strings*]             |
| googleID   | Google ID starting with '10' or '11' and making 21 characters [*string*] |
| profilePic | Link to the target's profile picture [*string*]              |
| name       | [Optional] : Target's name if found while scrapping maps data [*string*] |
| maps       | [Optional] : If target's Google Maps profile is public : See after [*dict*] |
| youtube    | See after [*dict*]                                           |

### Maps case format

#### General

| Key           | Value                                                        |
| ------------- | ------------------------------------------------------------ |
| url           | Link to the target's Google Maps & Contributions page [*string*] |
| contributions | Number of "reviews", "ratings", "photos", "videos", "answers", "edits", "placesAdded", "roadsAdded", "factsChecked", "q&a" and "publishedLists" [*dict* of *int*]<br>If Selenium is not configured, it will only be a string |
| localGuide    | [Optional] : If the target is a Local Guide, informations about "level" and "points" [*dict of int*] |
| reviews       | [Optional] : If the target posted reviews : See after [*list of dict*] |
| medias        | [Optional] : If the target posted medias : See after [*dict*] |

#### Reviews

List of each review posted.

| Key     | Value                                                        |
| ------- | ------------------------------------------------------------ |
| place   | Name of the place of the review (or rating) posted [*string*] |
| address | Address of the place of the review (or rating) posted [*string*] |
| stars   | Number of stars given with the review (or rating) [*int*]    |
| when    | [Optional] : When the review (or rating) was posted [*string*] |
| comment | [Optional] : Comment posted with the review [*string*]       |
| visited | [Optional] : When the place was visited [*string*]           |

#### Medias

##### General

| Key     | Value                                                      |
| ------- | ---------------------------------------------------------- |
| views   | Number of times people have seen the medias posted [*int*] |
| content | See after [*list of dict*]                                 |

##### Content

| Key     | Value                                                        |
| ------- | ------------------------------------------------------------ |
| place   | Name of the place of the review (or rating) posted [*string*] |
| address | Address of the place of the review (or rating) posted [*string*] |
| medias  | All the links of the medias posted refering to this place (pictures or videos) [*list of strings*] |

### YouTube case format

#### General

| Key      | Value                                           |
| -------- | ----------------------------------------------- |
| channel  | YouTube account name [*string*]                 |
| url      | Link to the channel [*string*]                  |
| creation | Creation date of the YouTube account [*string*] |
| videos   | See after [*list of dict*]                      |

#### Videos

List of informations about each video of the channel.
| Key         | Value                                                        |
| ----------- | ------------------------------------------------------------ |
| title       | Video title [*string*]                                       |
| link        | Link to the video [*string*]                                 |
| thumbnail   | Link to video thumbnail [*string*]                           |
| description | Video description [*string*] or ['*null*'] if no description |
| published   | Video publication date [*string*]                            |
| updated     | Video last updated date [*string*]                           |
| views       | Number of views [*int*]                                      |
| thumbUp     | Number of thumbs up [*int*]                                  |
| stars       | Number of stars (from 1 to 5 calculated according to the ratio of thumbs up and thumb down) [*float*] |


## <img src="https://github.githubassets.com/images/icons/emoji/unicode/1f4dd.png" alt="memo" style="zoom:33%;" /> Stuff to add

+ Colors in the printed output (feel free to help me with that)
+ ~~A way to get the name of the person without clicking the *Google Maps Contributions* link~~
+ ~~A way to scrap the data of *Google Maps Contributions*~~
+ ~~A commented version of the code lol~~
+ A way to recover the name of the target if *Google Maps* profile is private
+ Add some infos to scrap from Google Maps profile (date of each media or medias from reviews)
+ Another way to find a person's Google ID without using the API (using the API is efficient but I'd rather not have to use it)
+ Configure the script so that it can use Selenium with any geckodriver (not just Firefox)

## References

+ This article explaining a lot about Google ID : https://medium.com/week-in-osint/getting-a-grasp-on-googleids-77a8ab707e43
+ This online solution that allows you to search for only one address at a time : https://tools.epieos.com/email.php

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.fr.html)





