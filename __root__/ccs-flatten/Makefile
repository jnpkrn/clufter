.PHONY: all clean metadata full

TARGET  = ccs_flatten
OBJS    = flatten.o reslist.o resrules.o restree.o xmlconf.o
CFLAGS  += -Wall
#CFLAGS  += -g -ggdb

RAWMETADATA_EXT = metadata
RA_DIR          ?= /usr/share/cluster

ifneq (nocman,0)
	CFLAGS  += -DRAWMETADATA_EXT=\"${RAWMETADATA_EXT}\"
endif

CFLAGS  += $(shell pkg-config --cflags libxml-2.0)
LDFLAGS += $(shell pkg-config --libs libxml-2.0)

all: ${TARGET}
${TARGET}: ${OBJS}
	${CC} ${CFLAGS} ${LDFLAGS} $^ -o $@

metadata:
	for f in $$(find ${RA_DIR} -maxdepth 1 -type f -name '*.sh' -printf '%f\n'); do \
	    /bin/bash ${RA_DIR}/$$f meta-data > $$f.${RAWMETADATA_EXT}.tmp \
	    && test -s $$f.${RAWMETADATA_EXT}.tmp \
	    && mv $$f.${RAWMETADATA_EXT}{.tmp,} \
	    || ${RM} -- $$f.${RAWMETADATA_EXT}.tmp; \
	done

full: all metadata

clean:
	${RM} -- ${TARGET} ${OBJS} *.${RAWMETADATA_EXT}{.tmp,}
