import argparse
import json

from lib.digger import Digger


def main(mails, output, browser):

    data = Digger(mails, browser)

    with open((f"./{output}.json"), "w") as f:
        json.dump(data.as_dict(), f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Explore and scrap user's public data from Google account",
    )
    parser.add_argument(
        "-e",
        "--email",
        dest="email",
        type=str,
        nargs="?",
        default=None,
        help="target's mail",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        type=str,
        nargs="?",
        default=None,
        help="path to a file listing the email addresses of the targets",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        nargs="?",
        required=False,
        default="output",
        help="choose output name (default is 'output')",
    )
    parser.add_argument(
        "-b",
        "--browser",
        dest="browser",
        type=str.lower,
        choices=["firefox", "chrome"],
        required=False,
        default="firefox",
        help='select browser "chrome" or "firefox" (default is "firefox")',
    )
    parser.add_argument(
        "--no-banner",
        dest="nobanner",
        required=False,
        default=False,
        action="store_true",
        help="doesn't display banner",
    )
    args = parser.parse_args()

    if not args.nobanner:
        print(open("assets/banner.txt", "r").read())

    if not (args.email or args.file):
        parser.error("Please specify email(s) to dig")

    mails = []
    if args.email:
        mails.append(args.email)
    if args.file:
        mails.extend(open(args.file).read().splitlines())

    browser = args.browser

    main(mails=mails, output=args.output, browser=browser)
