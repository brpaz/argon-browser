#!/usr/bin/env python

import gi
import re
import sys
import signal

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, GLib, Gio, WebKit2

class AppWindow(Gtk.ApplicationWindow):

    def is_loading(self, view, data):
        print view.is_loading()

    def on_load_changed(self, webview, event):
        url = webview.get_uri()
        
        if event == WebKit2.LoadEvent.FINISHED:
            self.address_bar.set_text(url)

    def on_load_failed(self, webview, event, url, error):
        print("Error loading", url, "-", error)

    def create_widgets(self):

        self.webview = WebKit2.WebView()
        self.webview.connect("notify::is-loading", self.is_loading)
        self.webview.connect("load-changed",
                              self.on_load_changed)
        self.webview.connect("load-failed", self.on_load_failed)

        webviewSettings = WebKit2.Settings(
            enable_fullscreen=False,
            enable_smooth_scrolling=True,
            enable_dns_prefetching=True,
            enable_webgl=True,
            enable_media_stream=True,
            enable_mediasource=True
        )
        webviewSettings.set_user_agent(
            "Mozilla/5.0 (Linux; Android 8.1.0; Pixel Build/OPM4.171019.021.D1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36")

        self.webview.set_settings(webviewSettings)
        self.go_back = Gtk.Button()

        self.go_back.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon(name="back"), Gtk.IconSize.BUTTON))
        self.go_back.connect("clicked", lambda x: self.webview.go_back())
        self.go_forward = Gtk.Button()
        self.go_forward.add(Gtk.Image.new_from_gicon(
             Gio.ThemedIcon(name="next"), Gtk.IconSize.BUTTON))
        self.go_forward.connect("clicked", lambda x: self.webview.go_forward())

        self.reload = Gtk.Button()

        self.reload.add(Gtk.Image.new_from_gicon(
             Gio.ThemedIcon(name="reload"), Gtk.IconSize.BUTTON))
        self.reload.connect("clicked", lambda x: self.webview.reload())

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(False)

        close_button = Gtk.Button()
        close_button.connect("clicked", lambda x: self.destroy())

        close_button.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon(name="cancel"), Gtk.IconSize.BUTTON))

        settings_button = Gtk.Button()
        settings_button.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon(name="settings"), Gtk.IconSize.BUTTON))

        #settings_button.connect("clicked", self.on_settings_click)
        hb.pack_end(close_button)
        hb.pack_end(settings_button)
        hb.pack_start(self.go_back)
        hb.pack_start(self.go_forward)
        hb.pack_start(self.reload)

        self.address_bar = Gtk.Entry()
        self.address_bar.set_width_chars(50)
        self.address_bar.connect("activate", self.load_url)
        hb.set_custom_title(self.address_bar)

        self.set_titlebar(hb)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add_with_viewport(self.webview)

        self.add(self.scrolled_window)

    def __init__(self, *args, **kwargs):
        super(AppWindow, self).__init__(*args, **kwargs)

        self.set_title("Argon Browser")
       
        self.set_default_size(600, 400)
        self.set_keep_above(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)
  
        self.create_widgets()

        self.webview.load_uri("https://duckduckgo.com/")
        self.show_all()
 
    def load_url(self, widget):
        url = widget.get_text()

        if not re.match("^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$", url):
            self.webview.load_uri("https://www.google.pt/search?q=" + url)
            return
        
        if not "://" in url:
            url = "http://" + url
        self.webview.load_uri(url)

class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, application_id="net.brunopaz.argon-browser",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None

        self.add_main_option("url", ord("u"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.STRING, "Command line test", None)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppWindow(application=self)

        self.window.present()

    def do_command_line(self, command_line):
        self.options = command_line.get_options_dict()

        self.activate()
        return 0


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)



  
