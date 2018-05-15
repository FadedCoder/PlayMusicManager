from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .forms import SignUpForm, MusicUploadForm
from .models import Profile
from gmusicapi.protocol import musicmanager
from gmusicapi import Musicmanager
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.django_util.storage import DjangoORMStorage as Storage
import os
import subprocess
import logging
from distutils import spawn


logger = logging.getLogger(__name__)


def index(request):
    args = {}
    if request.user.is_authenticated:
        credential = request.user.profile.google_oauth
        if not credential:
            return HttpResponse('No credentials found. Remake an account.')
        manager = Musicmanager()
        # TODO: Maybe change mac address for each user?
        login_success = manager.login(
            credential,
            uploader_name="GMusicManagerOnline - {}".format(request.user.username))
        quota = manager.get_quota()
        args.update({
            'login_success': login_success,
            'currently_uploaded': quota[0],
            'upload_limit': quota[1]
        })
        manager.logout()
    return render(request, 'core/index.html', args)


def registration(request):
    form = SignUpForm()
    flow = OAuth2WebServerFlow(*musicmanager.oauth)
    auth_uri = flow.step1_get_authorize_url()
    args = {'form': form, 'auth_uri': auth_uri}
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            credential = flow.step2_exchange(form.cleaned_data.get('oauth_code'))
            user = form.save()
            user.refresh_from_db()
            storage = Storage(Profile, 'user', user, 'google_oauth')
            storage.put(credential)
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('index')
        args.update({'form': form})
    return render(request, 'core/register.html', args)


def upload(request):
    # TODO: Async status updates?
    if not request.user.is_authenticated:
        return HttpResponse('log in first')
    credential = request.user.profile.google_oauth
    if not credential:
        return HttpResponse('no creds')
    manager = Musicmanager()
    # TODO: Maybe change mac address for each user?
    login_success = manager.login(
        credential,
        uploader_name="GMusicManagerOnline - {}".format(request.user.username))
    form = MusicUploadForm()
    args = {'can_login': login_success, 'form': form, 'success': False}
    if request.method == "POST":
        form = MusicUploadForm(request.POST, request.FILES)
        if form.is_valid():
            music = form.save()
            music_file = request.FILES.get('music_file')
            ext = music_file.name[music_file.name.rfind('.'):]
            fs = FileSystemStorage()
            filename = fs.save("{0}{1}".format(request.user.username, ext), music_file)
            music_filepath = fs.path(filename)
            post_filepath = music_filepath + ".mp3"
            options = {i: getattr(music, i) for i in
                       ['title', 'album', 'composer', 'genre', 'language',
                        'artist', 'album_artist']}
            options.update({'quality': '320'})
            _transcode(music_filepath, options, post_filepath)
            if os.path.isfile(music_filepath):
                os.remove(music_filepath)
            manager.upload(post_filepath,
                           enable_matching=True,
                           enable_transcoding=False)  # Already transcoding.
            if os.path.isfile(post_filepath):
                os.remove(post_filepath)
            args.update({'success': True})
        args.update({'form': form})
    manager.logout()
    return render(request, 'core/upload.html', args)


def youtube_upload(request):
    return render(request, 'core/youtube.html')


def _locate_mp3_transcoder():
    transcoders = ['ffmpeg', 'avconv']
    transcoder_details = {}

    for transcoder in transcoders:
        cmd_path = spawn.find_executable(transcoder)
        if cmd_path is None:
            transcoder_details[transcoder] = 'not installed'
            continue

        with open(os.devnull, "w") as null:
            stdout = subprocess.check_output([cmd_path, '-codecs'], stderr=null).decode("ascii")
        mp3_encoding_support = ('libmp3lame' in stdout and 'disable-libmp3lame' not in stdout)
        if mp3_encoding_support:
            transcoder_details[transcoder] = "mp3 encoding support"
            break  # mp3 decoding/encoding supported
        else:
            transcoder_details[transcoder] = 'no mp3 encoding support'
    else:
        raise ValueError('ffmpeg or avconv must be in the path and support mp3 encoding'
                         "\ndetails: %r" % transcoder_details)

    return cmd_path


def _transcode(filepath, options, out_filepath):
    cmd_path = _locate_mp3_transcoder()
    cmd = [cmd_path, '-i', filepath]
    cmd.extend(['-q:a', str(options.pop('quality'))])
    for (i, j) in options.items():
        cmd.extend(['-metadata', '{0}="{1}"'.format(i, j)])
    cmd.extend(['-c', 'libmp3lame', out_filepath])
    logger.info('Running transcode command %r', cmd)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        audio_out, err_output = proc.communicate()
        if proc.returncode != 0:
            err_output = ("(return code: %r)\n" % proc.returncode) + err_output.decode("ascii")
            raise IOError  # handle errors in except
    except (OSError, IOError) as e:
        err_msg = "transcoding command (%r) failed: %s. " % (' '.join(cmd), e)
        if 'No such file or directory' in str(e):
            err_msg += '\nffmpeg or avconv must be installed and in the system path.'
        if err_output is not None:
            err_msg += "\nstderr: '%s'" % err_output
        logger.exception('transcoding failure:\n%s', err_msg)
        raise IOError(err_msg)
    return True
