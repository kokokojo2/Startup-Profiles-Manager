# Startup-Profiles-Manager
This is a python script for Windows 10 that is capable of launching previously created sets of applications in one click.
## Usage
Usually, Windows loads up lots of applications on startup, and this process significantly slows a system. However, there are many apps that most of the  users don`t use simultaneously. Originally, the idea was to create a script that will unload Windows startup and, as a result, make loading of the OS faster. This is achieved by stacking some applications, that user uses together (for instance, Discord and Steam; or PyCharm, VSCode and Slack) into a sets. As a result, user can remove tons of applications from Windows startup, create sets of apps that he or she uses together and add this script to Windows startup, so when the OS starts up, user choose which set of applications he\she needs to launch now.
## Functionality
So far, this script allows user to:
* create a set (so called profile) with entries that consist of paths to executable files (also specified by user) and other information.
* launch one of previously created profiles (script loops over all specified entries and launches provided executalbes)
* perform CRUD operations on profiles and their entries
* configure things like priority of launching, timeout after launch of each application for every profile independently
* configure script to start with Windows and close itself after a launch of profile
## System requirements
* OS - windows (tested on windows 10, some functions may not work on earlier versions)

## Installation
Clone this branch of a repo:
```
git clone -b console_script https://github.com/kokokojo2/Startup-Profiles-Manager
cd Startup-Profiles-Manager
```
Make and activate virtual environment:
```
python -m venv countdown_env
countdown_env\Scripts\activate
```
Install needed requirements:
```
pip install -r requirements.txt
```
Launch a script:
```
python main.py
```
If you need version that is packed into executable or application with nice UI based on this script, please see other branches or tags. 
