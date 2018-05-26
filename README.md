# PlayMusicManager
Unofficial Play Music Manager over the web. Made for those who don't use Windows as their main OS. Or wants to manage music via Android.
**Test site: [http://devtest.sohamsen.me](http://devtest.sohamsen.me)**

Only works with a Play Music subscription (so far tested).

Uses `Django 2`.

## Installation

```
git clone https://github.com/FadedCoder/PlayMusicManager.git
# OR
git clone git@github.com:FadedCoder/PlayMusicManager.git
cd PlayMusicManager
python3 -m venv venv
source venv/bin/activate
cd custom-oauth2client
python setup.py install
cd ..
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8080
```

Server will now run on [http://localhost:8080](http://localhost:8080).

## Current features

* Can upload music files directly
* Can upload music from YouTube directly (using `youtube-dl`)
* Can upload all metadata info (except album art)

## Planned features

* Metadata album art upload
* Refining of UI

### This project is not actively worked on. All pull requests are welcome. I'll push each PR to the site where it is hosted so it can be tested there.
