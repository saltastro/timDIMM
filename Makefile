# Makefile for routines for ieee1394-based DIMM camera

CC = gcc
CFLAGS = -Wall -O2 -I/opt/local/include
LDFLAGS = -L/opt/local/lib -framework CoreFoundation -framework Carbon -lIOKit \
	-lm -lcfitsio -lxpa -ldc1394
EXECS = grab_cube measure_seeing_saao measure_seeing_astelco ave_frames \
	video_feed grab noise_test

all:	${EXECS}

clean: 
	rm -f *.o; rm -f *~; rm -f ${EXECS}

grab_cube:	grab_cube_8bpp_binned.c
	${CC} ${CFLAGS} grab_cube_8bpp_binned.c ${LDFLAGS} -o grab_cube_8bpp_binned

measure_seeing_saao:	measure_seeing.c
	${CC} ${CFLAGS} measure_seeing.c ${LDFLAGS} -lgsl -lgslcblas -o measure_seeing

measure_seeing_astelco:	measure_seeing_astelco.c
	${CC} ${CFLAGS} measure_seeing_astelco.c ${LDFLAGS} -lgsl \
	-lgslcblas -o measure_seeing_astelco

noise_test:	noise_test.c
	${CC} ${CFLAGS} noise_test.c ${LDFLAGS} -lgsl -lgslcblas -o noise_test

video_feed:	video_feed.c
	${CC} ${CFLAGS} video_feed.c ${LDFLAGS} -o video_feed

grab:	grab.c
	${CC} ${CFLAGS} grab.c ${LDFLAGS} -o grab

ave_frames:	ave_frames.c
	${CC} ${CFLAGS} ave_frames.c ${LDFLAGS} -o ave_frames
