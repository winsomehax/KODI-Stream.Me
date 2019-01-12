from routing import Plugin
import mod_user
import kodifuncs as kf


plugin = Plugin()
kp = kf.kodiPlugin()
#followed = mod_user.myAccount()


def run():
    plugin.run()


def build_menu_top():

    kp.makeSelectable("Set your stream.me username (" +
                      kf.kodi_getsettingsuser()+")", plugin.url_for(opensettings))
    kp.makeFolder('Live streams by followed users',
                  plugin.url_for(livefollowed),"DefaultFolder.png")
    kp.makeFolder('Archived streams by followed users',
                  plugin.url_for(followedusers),"DefaultFolder.png")
    kp.makeFolder('All live streams', plugin.url_for(alllive),"DefaultFolder.png")
    kp.folderDone()


def build_opensettings():
    kp.openSettings()


def build_all_streams():


    allstreams = mod_user.allStreams()
    allstreams.refresh()

    kp.startVidFolder()

    for s in allstreams.liveStreams:
        kp.makePlayable(s.title, s.thumbnail, 0, s.url)

    kp.folderDone()


def build_live_followed():

    followed = mod_user.myAccount()
    streams = []
    for u in followed:
        r = mod_user.userLive(u.userSlug)
        r.refresh()
        streams.extend(r.streams)

    kp.startVidFolder()

    for s in streams:
        kp.makePlayable(s.title, s.thumbnail, 0, s.url)

    kp.folderDone()


def build_user_vod_archives(user):

    a = mod_user.userArchive(user)
    a.refresh()


    kp.startVidFolder()

    for s in a.streams:
        kp.makePlayable(s.title, s.thumbnail, s.duration, s.url)

    kp.folderDone()


def build_followed_users():

    followed = mod_user.myAccount()
    followed.refreshFollowing()

    kp.startVidFolder()

    for u in followed:
        kp.makeFolder(u.displayName, plugin.url_for(
            archivedfollowed, user=u.userSlug), 'DefaultUser.png')

    kp.folderDone()


@plugin.route('/')
def index():
    build_menu_top()


@plugin.route('/livefollowed/')
def livefollowed():
    build_live_followed()


@plugin.route('/alllive/')
def alllive():
    build_all_streams()


@plugin.route('/followed/')
def followedusers():
    build_followed_users()


@plugin.route('/archivedfollowed/<user>')
def archivedfollowed(user):
    build_user_vod_archives(user)


@plugin.route('/opensettings/')
def opensettings():
    build_opensettings()
