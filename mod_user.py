from urllib2 import urlopen, HTTPError
from json import loads
import __future__

import kodifuncs as kf


class SDM_Stream:
    live = False
    title = ""
    url = ""
    username = ""
    display_name = ""
    lastStarted = ""
    thumbnail = ""
    tags = []
    topics = []
    when_created = ""
    duration = ""
    json_store = ""

    def __init__(self, title, url):
        self.title = title
        self.url = url


class SDM_User:
    userSlug = ""
    display_name = ""
    description = ""

    def __init__(self, user, name, desc):
        self.userSlug = user
        self.display_name = name
        self.description = desc


# get a list of all stream.me live streams
class SDM_AllStreams:
    # live_streams: List[StreamSDM] = []

    def __init__(self):
        pass

    def _process_streams(self, url):
        streams = []

        response = urlopen(url)
        j = loads(response.read())
        for s in j['_embedded']['streams']:
            if 'hlsmp4' in s['_links']:
                stream = SDM_Stream(s['title'], s['_links']['hlsmp4']['href'])
                stream.Live, stream.username, stream.display_name, stream.lastStarted, stream.thumbnail = True, s[
                    'username'], s['displayName'], s['lastStarted'], s['_links']['thumbnail']['href']
                for t in s['topics']:
                    stream.topics.append(t['slug'])
                for t in s['tags']:
                    stream.topics.append(t['slug'])
                stream.json_store = j  # may as well stick it in there
                streams.append(stream)
            else:
                pass
                # skip no hlsmp4

        # the call will only return a max 120 at a time (according to stream.me barebones dev docs),
        # but if the json returned has a _links.next, there's more by following the 'next' link.
        if 'next' in j['_links']:
            next_link = j['_links']['next']
            streams.extend(self._process_streams(next_link))

        return streams

    def get_all_streams(self):
        return self._process_streams(
            'https://www.stream.me/api-live/v2/streams?limit=120')


# get the publicly available details for my stream.me user (as set in the kodi settings for this plugin)
# also, contains methods to get live streams for the user and the archives
class SDM_Account:

    username = ""

    def __init__(self, user):
        self.username = user

    # recursive function to get the json detailing followers and return a list of user objects.
    # Not to be called directly from outside
    def _load_following(self, url):
        followers = []
        response = urlopen(url)
        j = loads(response.read())
        for u in j["_embedded"]["users"]:
            user = SDM_User(u['slug'], u['username'], u['description'])
            followers.append(user)

        # If the json returned has a _links.next, there's more by following the 'next' link - recursive call.
        # Pass up the list joined together
        if '_links' in j:
            if 'next' in j['_links']:
                followers.extend(self._load_following(j['_links']['next']))

        return followers

    def get_following(self):
        return self._load_following(
            "https://www.stream.me/api-user/v1/" + self.username + "/following?limit=40")

    def get_vod_archive(self):
        streams = []
        response = urlopen('https://www.stream.me/api-vod/v2/' +
                           self.username + '/archives')
        j = loads(response.read())
        vods = j['_embedded']['vod']
        for vod in vods:
            title = vod['title']
            url = vod['_links']['hlsmp4']['href']
            s = SDM_Stream(title, url)
            s.Live, s.username, s.display_name, s.thumbnail, s.duration, s.when_created = \
                True, vod['username'], vod['displayName'], vod['_links']['thumbnail']['href'], \
                vod['duration'], vod['whenCreated']
            streams.append(s)

        return streams

    def get_live(self):

        streams = []

        try:
            response = urlopen(
                'https://www.stream.me/api-user/v1/' + self.username + '/channel/')

        except HTTPError:
            return []

        j = loads(response.read())
        for s in j['_embedded']['streams']:
            try:
                title = s['displayName'] + " - " + s['title']
                t = SDM_Stream(title, s["_links"]["hlsmp4"]["href"])
                t.Live, t.username, t.display_name, t.thumbnail, t.lastStarted = \
                    True, s['username'], s['displayName'], s['_links']['thumbnail']['href'], \
                    s['lastStarted']
                streams.append(t)

            except KeyError:
                # some streams appear to lack hlsmp4? dunno.. Ignore them. Can't be played anyway.
                pass

        return streams


# Special case - subclass. Doesn't need you to supply user. It gets it from the settings as it's
# YOUR stream.me user
class SDM_MyAccount(SDM_Account):

    def __init__(self):
        self.username = kf.kodi_get_settings_user()
        if self.username == "":
            self.username = 'winsomehax'  # replace empty setting with a useful default
        SDM_Account.__init__(self, self.username)
