#!/usr/bin/env python

import gi
import re
import sys
import signal
import os
import shutil
import logging
import json

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, GLib, Gio, WebKit2, GObject, Gdk

logger = logging.getLogger("main")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

APPLICATION_NAME = "argon-browser"
USER_AGENT_MOBILE = "Mozilla/5.0 (Linux; Android 8.1.0; Pixel Build/OPM4.171019.021.D1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36"
USER_AGENT_DESKTOP = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"


class AppWindow(object):
    """ Main browser window """

    def __init__(self, application):
        """ Init window """

        self.app = application

        self.create_widgets()

        # Fire up the main window
        self.MainWindow = self.builder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        self.MainWindow.set_keep_above(True)

        self.MainWindow.set_icon_from_file(
            os.path.join(self.app.app_dir, 'data', 'icons', 'icon.png'))
        screen = self.MainWindow.get_screen()
        self.MainWindow.move(screen.get_width(), screen.get_width(
        ) - self.MainWindow.get_default_size().width)

        self.MainWindow.show_all()

    def create_widgets(self):
        """ Creates the widgets for the window """
        # Read GUI from file and retrieve objects from Gtk.Builder
        self.builder = Gtk.Builder.new_from_file("glade/main.glade")
        self.builder.connect_signals(self)

        self.webview = WebKit2.WebView()
        self.webview.connect("notify::is-loading", self.is_loading)
        self.webview.connect("load-changed",
                             self.on_load_changed)
        self.webview.connect("load-failed", self.on_load_failed)
        self.webview.connect("decide-policy", self.on_policy_decision)

        webviewSettings = WebKit2.Settings(
            enable_fullscreen=True,
            enable_smooth_scrolling=True,
            enable_dns_prefetching=True,
            enable_webgl=True,
            enable_media_stream=True,
            enable_mediasource=True,
            enable_encrypted_media=True,
            enable_developer_extras=True
        )

        self.webview.load_uri(self.app.get_config()['homepage'])
        container = self.builder.get_object("main_container")
        container.add(self.webview)

        self.webview.show_all()

    def on_back_btn_clicked(self, widget):
        """ Handles the click on the browsers back button """
        self.webview.go_back()

    def on_btn_forward_clicked(self, widget):
        """ Handle Forward button click """
        self.webview.go_forward()

    def on_btn_refresh_clicked(self, widget):
        """ Handle page refresh """
        self.webview.reload()

    def on_btn_close_clicked(self, widget):
        """ Closes the application """
        self.MainWindow.destroy()

    def on_search_input(self, widget):
        """ Handles the url change of search bar """
        url = widget.get_text()

        if not re.match("^(http(s)?(:\/\/))?(www\.)?[a-zA-Z0-9-_\.]+\.[a-z]+$", url):
            self.webview.load_uri("https://www.google.pt/search?q=" + url)
            return

        if not "://" in url:
            url = "https://" + url

        use_mobile_version = any(
            x for x in self.app.config['mobile_version'] if x in url)

        if use_mobile_version:
            logger.info("Loading mobile version for %s" % url)
            self.webview.get_settings().set_user_agent(USER_AGENT_MOBILE)
        else:
            self.webview.get_settings().set_user_agent(USER_AGENT_DESKTOP)

        self.webview.load_uri(url)

    def on_btn_open_in_default_browser_clicked(self, widget):
        """ Open the current page in the default browser """
        uri = self.webview.get_uri()
        Gio.app_info_launch_default_for_uri(uri)
        self.MainWindow.destroy()

    def is_loading(self, view, data):
        pass

    def on_load_changed(self, webview, event):
        """ Handle the Load event on the webview """
        url = webview.get_uri()
        logger.info("Navigating to url: " + url)

        if event == WebKit2.LoadEvent.STARTED:
            search_bar = self.builder.get_object("search_bar")
            search_bar.set_text(url)

    def on_policy_decision(self, webview, decision, decision_type):
        """ Intercept requests in order to change some stuff like replacing video urls with embeded versions """
        if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:

            if not self.app.config['embeded_redirects']['enabled']:
                return True

            for site in self.app.config['embeded_redirects']['sites']:
                match = re.findall(site["pattern"], webview.get_uri())

                if match:
                    logger.info(match[0])
                    url = site["url"].replace("%id%", match[0])
                    webview.load_uri(url)
                    return False

        return True

    def on_load_failed(self, webview, event, url, error):
        """ Handles page load failed event """
        logger.info("Error loading page: %s Error: %s " % (url, error))


class Application(Gtk.Application):
    """ Main Application class """

    def __init__(self, *args, **kwargs):
        """ Application Constructor """
        logger.info("Starting application")
        super(Application, self).__init__(*args, application_id="net.brunopaz.argon-browser",
                                          flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                                          **kwargs)

        self.app_dir = os.path.dirname(os.path.realpath(__file__))
        self.load_config()

        self.win = None

        self.add_main_option("url", ord("u"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.STRING, "Command line test", None)

    def load_config(self):
        """ Load the application confiugraiton file """
        config_dir = os.path.join(
            GLib.get_user_config_dir(), APPLICATION_NAME)
        config_file = os.path.join(config_dir, 'config.json')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            shutil.copy(os.path.join(self.app_dir, 'data',
                                     'config.json'), config_file)

        with open(config_file) as f:
            self.config = json.loads(f.read())

    def get_config(self):
        return self.config

    def do_activate(self):
        win = AppWindow(self)

    def do_command_line(self, command_line):
        """ Handle command line options. Not really used for now """
        self.options = command_line.get_options_dict()

        self.activate()
        return 0


def main():
    app = Application()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
