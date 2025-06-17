# McGill-Registration-Bot
Uses Playwright to automatically check a course's status on McGill's course registration service, Minerva. Upon detecting an open seat, the bot makes an attempt to register that course section. The code in this repository has the bot wait 15 minutes between scans.

Installation and Use: Simply run the Python files in an IDE of your choice. Playwright's Python library needs to be installed to work. Instructions can be found on Playwright's Python Installation Guide found here: https://playwright.dev/python/docs/library

Notes:

Some location methods used are not very robust, relying on attributes like text to click certain buttons for instance. This will and should be changed in future revisions to ensure the program doesn't break between updates to the site.
For security reasons, personal login information is never stored.
This was made for educational purposes. Please use responsibly!
