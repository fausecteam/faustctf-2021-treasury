SERVICE := treasury
DESTDIR ?= dist_root
SERVICEDIR ?= /srv/$(SERVICE)

.PHONY: build install

build:
	$(MAKE) -C src

install: build
	mkdir -p $(DESTDIR)$(SERVICEDIR)
	cp src/treasury $(DESTDIR)$(SERVICEDIR)/
	mkdir -p $(DESTDIR)/etc/systemd/system
	cp src/treasury@.service $(DESTDIR)/etc/systemd/system/
	cp src/treasury.socket $(DESTDIR)/etc/systemd/system/
	cp src/system-treasury.slice $(DESTDIR)/etc/systemd/system/
