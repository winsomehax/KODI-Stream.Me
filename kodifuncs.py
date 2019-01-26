import xbmcaddon
import xbmcgui
from xbmcplugin import addDirectoryItem, endOfDirectory, setContent
from xbmcgui import ListItem
from routing import Plugin


def error_notice(err):
    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')

    xbmcgui.Dialog().ok(__addonname__, err, "", "")


def kodi_get_settings_user():
    return xbmcaddon.Addon().getSetting("user")


class KodiPlugin:
    handle = 0

    def __init__(self):
        self.handle = Plugin().handle

    def start_vid_folder(self):
        setContent(self.handle, "videos")

    def folder_done(self):
        endOfDirectory(self.handle)

    def make_folder(self, folder_name, url, icon_name):
        li = ListItem(folder_name, iconImage=icon_name)
        li.setProperty('IsPlayable', 'False')
        addDirectoryItem(self.handle, url=url, listitem=li, isFolder=True)

    def make_selectable(self, name, url):
        li = ListItem(name, iconImage='DefaultUser.png')
        li.setProperty('IsPlayable', 'False')
        li.setInfo("video", {'mediatype': 'video'})  # needed to make it selectable?
        addDirectoryItem(self.handle, url=url, listitem=li)

    def make_playable(self, playablename, thumbnail, duration, url):
        li = ListItem(playablename, iconImage='DefaultTVShows.png')
        li.setProperty('IsPlayable', 'True')
        li.setInfo("video", {'mediatype': 'video', 'duration': duration})
        li.addStreamInfo('video', {'duration': duration})
        li.setArt({'icon': thumbnail})
        li.setArt({'poster': thumbnail})
        li.setArt({'thumb': thumbnail})
        li.setArt({'banner': thumbnail})
        addDirectoryItem(self.handle, url=url, listitem=li)

    def open_settings(self):
        xbmcaddon.Addon().open_settings()
