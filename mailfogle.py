import json
import argparse
from sys import exit
from time import sleep
from lib.maps import mapsData
from lib.youtube import youtubeData
import lib.googlePeopleAPI as gpa

def printBanner():
    for line in open("assets/banner.txt","r"):
        print(line.replace("\n",""))

def printInformations(datas: dict):
    """Print the main informations."""

    user_type = (
        ['NOT A GOOGLE USER'] if 'userTypes' not in datas
        else [ut.replace('_',' ') for ut in datas['userTypes']]
    )
    print(f"\n{datas['mail']} : {', '.join(user_type)}\n")

    # GOOGLE USER
    if "userTypes" in datas:
        if "name" in datas: print(f"\tName : {datas['name']}")
        print(
            f"\tGoogle ID : {datas['googleID']}" + 
            f"\n\tProfile picture : {datas['profilePic']}"
        )

        # Maps profile not private
        if "maps" in datas:
            print(f"\n\tMaps Contributions & Reviews ({datas['maps']['url']})")

            if "localGuide" in datas['maps']:
                level  = datas['maps']['localGuide']['level']
                points = datas['maps']['localGuide']['points']
                print(f"\t\tLocal Guide level {level} with {points} points")

            if isinstance(datas['maps']['contributions'],dict):
                nbContrib = sum(
                    datas['maps']['contributions'][what]
                    for what in datas['maps']['contributions']
                )
                reviews_ratings = (
                    datas['maps']['contributions']['reviews'] +
                    datas['maps']['contributions']['ratings']
                )
                medias = (
                    datas['maps']['contributions']['photos'] +
                    datas['maps']['contributions']['videos']
                )
                print(
                    f"\t\t{nbContrib} contributions including " +
                    f"{reviews_ratings} reviews & ratings and {medias} medias"
                )

                count = 0
                if datas['maps']['contributions']['photos'] or datas['maps']['contributions']['videos']:
                    count = sum(
                        len(c['medias']) 
                        for c in datas['maps']['medias']['content']
                    )
                reviews_ratings = (
                    len(datas['maps']['reviews'])
                    if 'reviews' in datas['maps'] else 0
                )
                print(
                    "\t\t\t" + " "*len(str(nbContrib)) +
                    f"scrapped in fact {reviews_ratings} reviews & ratings " +
                    f"and {count} medias"
                )

            else:
                print(
                    f"\t\t{datas['maps']['contributions']} contributions" +
                    "/!\\ This data is sometimes wrong. " +
                    "Configure Selenium to scrap more accurate informations /!\\"
                )

        else:
            print(
                "\n\tGoogle maps profile is private, " +
                "can\'t scrap informations from it"
            )

    # YouTube informations
    if "youtube" in datas:
        print(
            f"\tYouTube : User \"{datas['youtube']['username']}\" found " +
            "/!\\ Maybe not the one you're looking for /!\\"
        )
        creation = datas['youtube']['creation']
        creation_date = creation[:len(creation)-6].replace('T',' ')
        print(
            f"\t\tChannel \"{datas['youtube']['channel']}\" created {creation_date}"
        )
        print(f"\t\t{datas['youtube']['url']}")
        print(
            f"\t\t{sum(video['views'] for video in datas['youtube']['videos'])} " +
            f"cumulative views on {len(datas['youtube']['videos'])} " +
            "last posted video(s) found"
        )

def main(mails,output,browser):

    apiFlag = False
    try:
        gpa.connect()
        apiFlag = True
        print("Connected to Google people API")
    except:
        print("Cannot connect to Google people API")
        print("Retry after deleting \"token.json\"")

    datas = []

    if apiFlag:

        gpa.importContacts(mails)
        while True:

            connections = gpa.downloadContacts()
            connections = list(filter(
                lambda contact : "emailAddresses" in contact.keys() 
                    and contact['emailAddresses'][0]['value'] in mails,
                connections,
            ))
            
            for person in connections:
                data = {}
                mail = person['emailAddresses'][0]['value']

                if mail in mails:
                    data['mail'] = mail
                    if len(person['metadata']['sources']) > 1:
                        sources = person['metadata']['sources'][1]
                        data['userTypes']  = sources['profileMetadata']['userTypes']
                        data['googleID']   = sources['id']
                        data['profilePic'] = person['photos'][0]['url']

                        mpDatas = mapsData(
                            url=(
                                "https://www.google.com/maps/contrib/" +
                                data['googleID']
                            ),
                            browser=browser,
                        )
                        if mpDatas: # If profile is public
                            data['maps'] = mpDatas
                            data['name'] = data['maps']['name']
                            data['maps'].pop("name")

                    ytDatas = youtubeData(mail.split("@")[0])
                    if ytDatas: data['youtube'] = ytDatas

                    printInformations(data)

                    gpa.deleteContact(person['resourceName'])
                    mails.pop(mails.index(mail))

                    datas.append(data)

            if len(mails) == 0: break
            sleep(2)

    else:
        for mail in mails:
            ytDatas = youtubeData(mail.split("@")[0])
            data = {"mail" : mail}
            if ytDatas :
                data["youtube"] = ytDatas
            printInformations(data)
            datas.append(ytDatas)

    with open((f"./{output}.json"),"w") as f:
        json.dump(datas,f, indent=2)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Explore and scrap user\'s public data from Google account"
    )
    parser.add_argument(
        "-e",
        # metavar="EMAIL",
        dest="email",
        type=str,
        nargs="?",
        default=None,
        help="target\'s mail"
    )
    parser.add_argument(
        "-f",
        dest="file",
        type=str,
        nargs="?",
        default=None,
        help="path to a file listing the email addresses of the targets"
    )
    parser.add_argument(
        "-o",
        dest="output",
        type=str,
        nargs="?",
        default="output",
        help="choose output name (default is \"output\")",
    )
    parser.add_argument(
        "-b",
        dest="browser",
        choices=["firefox","chrome"],
        default="firefox",
        help="select browser \"chrome\" or \"firefox\" (default is \"firefox\")",
    )
    args = parser.parse_args()

    printBanner()

    mails = []

    if args.email: mails.append(args.email)
    if args.file:  mails.extend(open(args.file).read().splitlines())

    if not mails:
        exit(
            "Please specify target\'s mail\n" +
            "mailfogle.py [-h] for more informations"
        )

    if args.browser.lower() not in ['firefox','chrome']:
        exit(
            "Please choose a browser between \"Firefox\" and \"Chrome\"\n" + 
            "mailfogle.py [-h] for more informations"
        )
    else: browser = args.browser.lower()

    main(mails=mails,output=args.output,browser=browser)