# Argon Browser

> A minimalist floating browser for Linux, inspired by [Hellium](http://heliumfloats.com/) and [Fluid](https://itunes.apple.com/us/app/fluid-browser/id1077036385?mt=12)

## Motivation

Sometimes I want to see some video or to follow along with a tutorial, while keep working on other things. Thats why I decided to build this application.

## Main Features

* Mimimal browser window always on top.
* Videos from popular platforms like Youtube and Vimeo are opened as full page.
* Some sites can be conifugred to open its Mobile version as default.

## Tech stack

* GTK+3
* Python 2.7

## Install

```
git clone https://github.com/brpaz/argon-browser
make install
```

The application source code will be installed in """/opt/argon-browser""". The simplest possible install. If someone wants to pack this a a deb, snap or flatpak, PRs are welcome.

## Configuration

You can configure some settings like the default homepage, default window size and redirect rules (useful for opening videos on full size). The configuration is a simple json file located in "~/.config/argon-browser/config.json".

## License

MIT @ Bruno Paz
