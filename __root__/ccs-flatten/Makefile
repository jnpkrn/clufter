# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

# Intended way of building is via setup.py, this is primarily for maintenance!

.PHONY: all clean metadata full install deepclean  # symlink

TARGET  = ccs_flatten
OBJS    = flatten.o reslist.o resrules.o restree.o xmlconf.o
CFLAGS  += -Wall
ifdef DEBUG
	CFLAGS  += -g -ggdb
else
	CFLAGS  += -DNDEBUG
endif

SETUP_MAKEFILE  = Makefile.setup
SETUP_CFG       = ../setup.cfg

ccs_flatten     ?= /usr/bin/ccs_flatten
ra_metadata     ?= /usr/share/cluster
ra_metadata_ext ?= metadata

# preferably take values from ../setup.cfg (abuse the similarity of decls)
-include ${SETUP_MAKEFILE}

CFLAGS  += $(shell pkg-config --cflags libxml-2.0)  #-std=c99
LDFLAGS += $(shell pkg-config --libs libxml-2.0)

all: ${TARGET}
${TARGET}: ${OBJS}
	${CC} ${CFLAGS} $^ -o $@ ${LDFLAGS}

${OBJS}: ${SETUP_MAKEFILE} config.h

%.h: ${SETUP_MAKEFILE}
%.h: %.h.in
	sed \
	-e 's|@RA_METADATA@|${ra_metadata}|g' \
	-e 's|@RA_METADATA_EXT@|${ra_metadata_ext}|g' \
	$< > $@

${SETUP_MAKEFILE}: Makefile
${SETUP_MAKEFILE}: $(wildcard ${SETUP_CFG}) | /dev/null
	sed -n \
	-e '/\[pkg_prepare\]/b1;d' \
	-e ':1;n;/\[.*\]/d;/%{.\+}/s|\([^%]\+\)%\({.*}\)s\?\(.*\)|\1$$\2\3|;p;b1' \
	$< > $@

metadata:
	for f in $$( \
	    cd ${ra_metadata}; \
	    ls -1 | xargs grep --exclude '*.metadata' --exclude 'ocf-*' -Fl -- meta-data \
	); do \
	    /bin/bash ${ra_metadata}/$$f meta-data > $$f.${ra_metadata_ext}.tmp \
	    && test -s $$f.${ra_metadata_ext}.tmp \
	    && mv $$f.${ra_metadata_ext}{.tmp,} \
	    || ${RM} -- $$f.${ra_metadata_ext}.tmp; \
	done

full: all metadata

install: full
	install ${TARGET} ${PREFIX}/${ccs_flatten}
	install *.${ra_metadata_ext} ${PREFIX}/${ra_metadata}

#symlink:
#	ln -fs ../build/ccs_flatten .

clean:
	${RM} -- ${TARGET} ${OBJS} config.h *.${ra_metadata_ext}.tmp

deepclean: clean
	${RM} -- *.${ra_metadata_ext}
