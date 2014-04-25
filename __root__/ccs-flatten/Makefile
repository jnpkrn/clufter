.PHONY: all clean

TARGET = ccs_flatten
OBJS   = flatten.o reslist.o resrules.o restree.o xmlconf.o
CFLAGS += $(shell pkg-config --cflags libxml-2.0) -I.
LDFLAGS += $(shell pkg-config --libs libxml-2.0)

all: ${TARGET}
${TARGET}: ${OBJS}
	${CC} ${CFLAGS} ${LDFLAGS} $^ -o $@

clean:
	${RM} ${TARGET} ${OBJS}
