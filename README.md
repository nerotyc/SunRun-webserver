
# SunRun - sports activity manager

## Live Version

At [run.djk-sonnen.de](https://run.djk-sonnen.de/) you can see the system in production.
You can 

## Installation
### 1. Python installation

### 2. Pip installation
- https://bootstrap.pypa.io/get-pip.py or _installation/get-pip.py
- Admin Shell: python _installation/get-pip.py

MacOS & Linux:
```
python3 -m pip install --user --upgrade pip
python3 -m pip --version
```

Windows:
```
py -m pip --version
// pip 9.0.1 from c:\python36\lib\site-packages (Python 3.6.1)
py -m pip install --upgrade pip
```

```
pip install virtualenv
or
py -m pip install --user virtualenv
```

### 3. Create virtual environment
maxOS & Linux
```
python3 -m venv env
```

Windows:
```
py -m venv env
```

### 4. activating virtualenv
```
_scripts/_(_)?source.(sh|bat)
```
or
```
cd env/Scripts
Win: activate.bat
UNIX: source activate
```

### 5. Pip install requirements:
```
cd _installation
pip3 install -r requirements.txt
```

### 6. Setup Configurations:
```
_scripts/_(_)?setup.(sh|bat)
```

---
## ToDo's
1. Resetting passwords by email (setting up mail server)

---

# Related Projects

## Flutter mobile app

### Playstore entry
No Playstore entry yet

### GitHub Project
Click [here](https://github.com/nerotyc/SunRun-app) to see the source code of SunRun's mobile flutter app.

## SunRun API

### API Docs
[Here](http://api-docs.run.djk-sonnen.de/api/v1/ui/) you can find the swagger documentation of the api's endpoints.

### GitHub API Project
Click [here](https://github.com/Nerotyc/SunRun-api) to see the api documentation implementation on GitHub.
