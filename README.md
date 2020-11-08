# Django Backend Of COMP90018 Mobile Computing Systems Programming
***Must Run With Linux/MacOS***

## Run directly:
1. pip3 install -r requirement.txt
1. python3 manage.py runserver --settings=MobileBackend.settings.prod 0:8080
## Run with Docker:
1. sh build.sh
1. docker run -d -p 8080:8080 --name mobile-backend mobile-backend
