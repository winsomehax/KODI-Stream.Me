from routing import Plugin
from mod_user import SDM_User, SDM_Stream, SDM_Account, SDM_MyAccount, SDM_AllStreams
import kodifuncs as kf

plugin = Plugin()
kp = kf.KodiPlugin()

def run():
    plugin.run()


def build_menu_top():
    kp.make_selectable("Set your stream.me username (" +
                       kf.kodi_get_settings_user() + ")", plugin.url_for(open_settings))
    kp.make_folder('Live streams by followed users',
                   plugin.url_for(live_followed), "DefaultFolder.png")
    kp.make_folder('Archived streams by followed users',
                   plugin.url_for(followed_users), "DefaultFolder.png")
    kp.make_folder('All live streams', plugin.url_for(all_live), "DefaultFolder.png")
    kp.folder_done()


def build_open_settings():
    kp.open_settings()


def build_all_streams():
    a = SDM_AllStreams()
    kp.start_vid_folder()

    for s in a.get_all_streams():
        kp.make_playable(s.title, s.thumbnail, "", s.url)

    kp.folder_done()


def build_live_followed():
    my_account = SDM_MyAccount()
    streams = []

    for u in my_account.get_following():
        a = SDM_Account(u.userSlug)
        streams.extend(a.get_live())

    kp.start_vid_folder()

    for s in streams:
        kp.make_playable(s.title, s.thumbnail, "", s.url)

    kp.folder_done()


def build_user_vod_archives(user):
    a = SDM_Account(user)
    kp.start_vid_folder()

    for s in a.get_vod_archive():
        kp.make_playable(s.title, s.thumbnail, s.duration, s.url)

    kp.folder_done()


def build_followed_users():
    m = SDM_MyAccount()
    kp.start_vid_folder()

    for u in m.get_following():
        kp.make_folder(u.display_name, plugin.url_for(
            archived_followed, user=u.userSlug), 'DefaultUser.png')

    kp.folder_done()


@plugin.route('/')
def index():
    build_menu_top()


@plugin.route('/livefollowed/')
def live_followed():
    build_live_followed()


@plugin.route('/alllive/')
def all_live():
    build_all_streams()


@plugin.route('/followed/')
def followed_users():
    build_followed_users()


@plugin.route('/archivedfollowed/<user>')
def archived_followed(user):
    build_user_vod_archives(user)


@plugin.route('/opensettings/')
def open_settings():
    build_open_settings()
