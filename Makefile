# Makefile for routines for ieee1394-based DIMM camera

CC = gcc
CFLAGS = -O2 -I/opt/local/include
LDFLAGS = -L/opt/local/lib -framework CoreFoundation -framework Carbon -lIOKit -lm -lcfitsio -lxpa -ldc1394
EXECS = grab_cube

all:	grab_cube

clean: 
	rm -f *.o; rm -f *~; rm -f ${EXECS}

grab_cube:	grab_cube.c
	${CC} ${CFLAGS} grab_cube.c ${LDFLAGS} -o grab_cube
