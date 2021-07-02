# Startup-Profiles-Manager
This is a desktop application for Windows OS, that is capable of launching previously created sets of applications in one click.
## Technology stack
* Python 3.9
* Native JS
* Electron
* HTML & CSS
* SQLite3
## Usage
Startup Manager is a utility application that is capable of launching previously created sets of applications in one click. My (the author's) intention of creating this app was solving a problem of Windows startup unflexibility (user can only add a desired application into startup or remove it). However, what if user wants to choose which applications to launch every particular time when Windows starts without constantly adding and removing them from startup? Here comes this app! It allows user to create and configure sets of applications that he/she wants to launch together and adds itself to a Windows startup. So, the next time Windows starts, user can choose one of previously created sets of applications and instantly launch them. See `Work examples` for screen captures of application's work and `Functionality` for better capabilities reference.
## Functionality
So far, this application allows user to:
* create a set (so called profile) with entries that consist of paths to executable files (also specified by user) and other information.
* launch one of previously created profiles (script loops over all specified entries and launches provided executalbes)
* perform CRUD operations on profiles and their entries
* configure things like priority of launching, timeout after launch of each application independently for every profile
* configure script to start with Windows OS and close itself after launch of a profile
## Work examples
## System requirements
* OS - Windows (tested on Windows 10, some functions may not work on earlier versions)
## Installation
If you need a build executable that can run without dependencies installation, please see this tag. Also, you can check out other branches that store script itself (without UI) and source code of an executable file.
### Installation process
After following these steps please check if you machine has installed nodejs. If it is not installed, you can download it [here](https://nodejs.org/en/download/).
Clone this branch of a repo:
```
git clone -b master https://github.com/kokokojo2/Startup-Profiles-Manager
cd Startup-Profiles-Manager
```
Make and activate virtual environment:
```
python -m venv env
env\Scripts\activate
```
Install needed requirements:
```
pip install -r requirements.txt
```
Install electron locally for this project:
```
npm install electron --save-dev
```
Launch the app:
```
python main.py
``` 
