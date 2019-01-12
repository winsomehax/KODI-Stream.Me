import xbmcaddon
import xbmcgui
from xbmcplugin import addDirectoryItem, endOfDirectory, setContent
from xbmcgui import ListItem
from routing import Plugin

def errornotice(err):
    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')

    xbmcgui.Dialog().ok(__addonname__, err, "", "")

def kodi_getsettingsuser():
    return (xbmcaddon.Addon().getSetting("user"))


class kodiPlugin():
    handle=0

    def __init__(self):
        self.handle=Plugin().handle

    def startVidFolder(self):
        setContent(self.handle, "videos")

    def folderDone(self):
        endOfDirectory(self.handle)

    def makeFolder(self,foldername, url, iconname):
        li = ListItem(foldername, iconImage=iconname)
        li.setProperty('IsPlayable', 'False')
        addDirectoryItem(self.handle, url=url, listitem=li, isFolder=True)

    def makeSelectable(self,name,url):
        li = ListItem(name, iconImage='DefaultUser.png')
        li.setProperty('IsPlayable', 'False')
        li.setInfo("video", {'mediatype': 'video'})   # needed to make it selectable?
        addDirectoryItem(self.handle, url=url, listitem=li)

    def makePlayable(self,playablename, thumbnail, duration, url):
        li = ListItem(playablename, iconImage='DefaultTVShows.png')
        li.setProperty('IsPlayable', 'True')
        li.setInfo("video", {'mediatype': 'video', 'duration': duration})
        li.addStreamInfo('video', { 'duration': duration})
        li.setArt({'icon': thumbnail})
        li.setArt({'poster': thumbnail})
        li.setArt({'thumb': thumbnail})
        li.setArt({'banner': thumbnail})
        addDirectoryItem(self.handle, url=url, listitem=li)

    def openSettings(self):
        xbmcaddon.Addon().openSettings()
