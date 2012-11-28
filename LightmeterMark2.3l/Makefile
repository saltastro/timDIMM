#
# Makefile for LightMeterLinux
# S. Kimeswenger, Innsbruck
#
CFLAGS = -I/opt/local/include -Wall -Werror -Wstrict-prototypes -O -g

all: lightmeter_mark23l_v5.0.o
	cc $(CFLAGS) lightmeter_mark23l_v5.0.o -o lightmeter_mark23l -L/opt/local/lib -lusb

# for the setup root permissions are required
setup:
	chown root.root lightmeter_mark23l
	chmod 7755 lightmeter_mark23l
	ln -s `pwd`/lightmeter_mark23l /usr/local/bin/lightmeter_mark23l

clean:
	rm -f *.o lightmeter_mark23l
