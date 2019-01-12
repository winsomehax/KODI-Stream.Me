from urllib2 import urlopen, HTTPError
from json import loads
import kodifuncs as kf


class streamSDM:

    live = False
    title = ""
    url = ""
    username = ""
    displayName = ""
    lastStarted = ""
    thumbnail = ""
    tags = []
    topics = []
    whenCreated = ""
    duration = ""
    jsonstore = ""

    def __init__(self, title, url):
        self.title = title
        self.url = url


class userSDM:

    userSlug = ""
    displayName = ""
    description = ""

    def __init__(self, user, name, desc):
        self.userSlug = user
        self.displayName = name
        self.description = desc


# get a list of all stream.me live streams
class allStreams:

    liveStreams = []

    def _processStreams(self, url):
        streams = []
        response = urlopen(url)
        j = loads(response.read())
        for s in j['_embedded']['streams']:
            if (s['_links'].has_key('hlsmp4')):
                stream = streamSDM(s['title'], s['_links']['hlsmp4']['href'])
                stream.Live, stream.username, stream.displayName, stream.lastStarted, stream.thumbnail = True, s[
                    'username'], s['displayName'], s['lastStarted'], s['_links']['thumbnail']['href']
                for t in s['topics']:
                    stream.topics.append(t['slug'])
                for t in s['tags']:
                    stream.topics.append(t['slug'])
                stream.jsonstore = j  # may as well stick it in there
                streams.append(stream)
            else:
                print "skip no hlsmp4"

        # the call will only return a max 120 at a time (according to stream.me barebones dev docs), but if the json returned has a _links.next, there's more by following the 'next' link.
        if j['_links'].has_key('next'):
            next = j['_links']['next']
            streams.extend(self._processStreams(next))

        return streams

    def refresh(self):
        self.liveStreams = self._processStreams(
            'https://www.stream.me/api-live/v2/streams?limit=120')


# get the publicly available details for my stream.me user (as set in the kodi settings for this plugin)
class myAccount():

    following = []
    username = ""

    def __init__(self):
        self.username = self.getUsername()
        if self.username == "":
            kf.errornotice()
            self.username = 'winsomehax'  # replace empty setting with a useful default

        self.refreshFollowing()

    def getUsername(self):
        return (kf.kodi_getsettingsuser())

    # recursive function to get the json detailing followers and return a list of user objects. Not to be called directly from outside
    def _loadFollowing(self, url):
        followers = []
        response = urlopen(url)
        j = loads(response.read())
        for u in j["_embedded"]["users"]:
            user = userSDM(u['slug'], u['username'], u['description'])
            followers.append(user)

        # If the json returned has a _links.next, there's more by following the 'next' link - recursive call. Pass up the list joined together
        if j.has_key('_links'):
            if j['_links'].has_key('next'):
                followers.extend(self._loadFollowing(j['_links']['next']))

        return (followers)

    def refreshFollowing(self):
        self.following = self._loadFollowing(
            "https://www.stream.me/api-user/v1/"+self.username+"/following?limit=40")

    def __iter__(self):
        for f in self.following:
            yield f

# get the archived streams for a particular user
class userArchive:

    streams = []
    user = ""

    def __init__(self, user):
        self.user = user

    def refresh(self):
        self.streams = []
        response = urlopen('https://www.stream.me/api-vod/v2/' +
                           self.user+'/archives')
        j = loads(response.read())
        vods = j['_embedded']['vod']
        for vod in vods:
            title = vod['title']
            url = vod['_links']['hlsmp4']['href']
            s = streamSDM(title, url)
            s.Live, s.username, s.displayName, s.thumbnail, s.duration, s.whenCreated = True, vod['username'], vod[
                'displayName'], vod['_links']['thumbnail']['href'], vod['duration'], vod['whenCreated']
            self.streams.append(s)


# get the streams that are live for a particular user
class userLive:

    streams = []
    user = ""

    def __init__(self, user):
        self.user = user

    def refresh(self):
        self.streams = []
        try:
            response = urlopen(
                'https://www.stream.me/api-user/v1/'+self.user+'/channel/')

        except HTTPError:
            return False

        j = loads(response.read())
        for s in j['_embedded']['streams']:
            try:
                title = s['displayName'] + " - "+s['title']
                t = streamSDM(title, s["_links"]["hlsmp4"]["href"])
                t.Live, t.username, t.displayName, t.thumbnail, t.lastStarted = True, s[
                    'username'], s['displayName'], s['_links']['thumbnail']['href'], s['lastStarted']
                self.streams.append(t)

            except KeyError:
                # kodidialogs.errornotice()
                # some streams appear to lack hlsmp4? dunno.. Ignore them. Can't be played anyway.
                pass

        return True


# get the streams that are live for a list of users
class usersLive:

    streams = []
    users = []

    def __init__(self, users):
        self.users = users

    def refresh(self):
        for u in self.users:
            r = userLive(u.userSlug)
            r.refresh()
            self.streams.extend(r)
