
lint:
	@pycodestyle .

format:
	@autopep8 --in-place --recursive --aggressive .

run:
	@python main.py

install:
	@sudo cp -R . /opt/argon-browser
	@sudo cp data/argon.desktop /usr/local/share/applications/argon.browser.desktop
	@sudo cp data/icons/icon.svg /usr/local/share/pixmaps/argon.browser.svg

