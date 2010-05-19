# Makefile for routines for ieee1394-based DIMM camera

CC = gcc
CFLAGS = -O2 -I/opt/local/include
LDFLAGS = -L/opt/local/lib -framework CoreFoundation -framework Carbon -lIOKit -lm -lcfitsio -lxpa -ldc1394
EXECS = grab_cube grab_cube_16bpp_binned grab_cube_8bpp_binned measure_seeing ave_frames

all:	${EXECS}

clean: 
	rm -f *.o; rm -f *~; rm -f ${EXECS}

grab_cube:	grab_cube.c
	${CC} ${CFLAGS} grab_cube.c ${LDFLAGS} -o grab_cube

grab_cube_16bpp_binned:	grab_cube_16bpp_binned.c
	${CC} ${CFLAGS} grab_cube_16bpp_binned.c ${LDFLAGS} -o grab_cube_16bpp_binned

grab_cube_8bpp_binned:	grab_cube_8bpp_binned.c
	${CC} ${CFLAGS} grab_cube_8bpp_binned.c ${LDFLAGS} -o grab_cube_8bpp_binned

measure_seeing:	measure_seeing.c
	${CC} ${CFLAGS} measure_seeing.c ${LDFLAGS} -lgsl -lgslcblas -o measure_seeing

ave_frames:	ave_frames.c
	${CC} ${CFLAGS} ave_frames.c ${LDFLAGS} -o ave_frames
