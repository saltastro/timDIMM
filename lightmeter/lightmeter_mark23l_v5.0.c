/**
** LIGHTMETER USB READOUT
**
** S. Kimeswenger, University Innsbruck, Austria
** 
** version 5.0
** 11.8.2009
**
** REMARK: this version is not tested by the Author yet.
**         it is a kind of "blind" prerelease for the new devices
**
** changes: 
**
** adding new communication for the extended devices -
** with this line enabled it only works with the new devices 
** sending 7 bytes for the light query !
** to move back uncomment this line here
**/
#define NEW_DEVICE

/** if you want no temperature reading comment this line **/
#define TEMPERATURE

/** if you try high speed uncomment this line here 
    you additionally requires a SPEED value in milliseconds
    remark this is EXPERIMENTAL and additionally can be used only 
    without TEMPERATURE **/
/**#define HIGH_SPEED**/
/* here a 10 Hz example - the real speed depends much on
   the speed of the USB device itself **/
#define SPEED 100
/**
**---------------------------------------------------------------------
** @ version 4.1:
** the USB devices are running offline from time to time
**
** as the recovery after 5 seconds is still insuffisient @ our device
** a full reset recovery is implemented now including a reinit of the
** device after some retries of the write 
**


--------------------------------------------------------------------
required additional libraries:

libusb

Fedora:
	yum install libusb
ubuntu:
	apt-get install libusb
--------------------------------------------------------------------
program call requires root priority. It is thus either called as root
with sudo or the root flag is set by:

chown root.root lightmeter_usb
chmod 755 lightmeter_usb
chmod +s lightmeter_usb

lightmeter_usb [sampling]
     the optional paramter sampling is given in full seconds

The program writes to stdout

--------------------------------------------------------------------
Makefile:
CFLAGS = -Wall -Werror -Wstrict-prototypes -O0 -static

all: lightmeter_usb.o
	cc $(CFLAGS) lightmeter_usb.o -o lightmeter_usb -lusb

clean:
	rm -f *.o lightmeter_usb
--------------------------------------------------------------------
**
** This file is based on the fsusb_demo
**
** fsusb_demo is free software; you can redistribute it and/or
** modify it under the terms of the GNU General Public License as
** published by the Free Software Foundation; either version 2 of the
** License, or (at your option) any later version.
**
** fsusb_demo is distributed in the hope that it will be useful, but
** WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
** General Public License for more details.
**
*/

/**

based on:

A USB interface to the Microchip PICDEM FS USB Demo board

Manuel Bessler, m.bessler AT gmx.net, 20050619

Based on usb_pickit.c :
Orion Sky Lawlor, olawlor@acm.org, 2003/8/3
Mark Rages, markrages@gmail.com, 2005/4/1

Simple modification by Xiaofan Chen, 20050811
Email: xiaofan AT sg dot pepperl-fuchs dot com
Notes by Xiaofan Chen, 20050812

*/
#include <usb.h> /* libusb header */
#include <unistd.h> /* for geteuid */
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include <signal.h>

#ifdef HIGH_SPEED
#include <sys/timeb.h>
#endif
/* global variables */
/* device handle for the USB bus */
struct usb_dev_handle * picdem_fs_usb;
/* character field for the output text */
char outstring[256];
/* error counter, wait time after an error and maximum number of errors allowed */
int errcount = 0, ierr = 0;
#define MAX_ERROR 5
#define WAIT_ERROR 5
/* PICkit USB values */ /* From Microchip firmware */
const static int vendorID=0x04d8; // Microchip, Inc
// const static int productID=0x000c; // PICDEM FS USB demo app
const static int productID=0xfcb7; // PICDEM FS USB demo app
const static int configuration=1; /*  Configuration 1*/
const static int interface=0;	/* Interface 0 */
const static int endpoint_in=0x81; /* endpoint 0x81 address for IN */
const static int endpoint_out=1; /* endpoint 1 address for OUT */

const static int timeout=2000; /* timeout in ms */

/* PICDEM FS USB max packet size is 64-bytes */
const static int reqLen=64;
typedef unsigned char byte;

void bad(const char *why) {
	fprintf(stderr,"Fatal error> %s\n",why);
	exit(17);
}

/****************** Internal I/O Commands *****************/

/** Send this binary string command. */
static int send_usb(struct usb_dev_handle * d, int len, const char * src)
{
   int r = usb_bulk_write(d, endpoint_out, (char *)src, len, timeout);
//   if( r != reqLen )
   if( r < 0 )
   {
	  //printf("usb PICDEM FS USB write: %c",src[0]); 
          return -1; //bad("USB write failed"); 
   }
   return 0;
}

/** Read this many bytes from this device */
static int recv_usb(struct usb_dev_handle * d, int len, byte * dest)
{
//   int i;
   int r = usb_bulk_read(d, endpoint_in, (char *)dest, len, timeout);
   if( r != len )
   {
	  //
          // perror("usb PICDEM FS USB read"); 
          return -2; //bad("USB read failed"); 
   }
   return 0;
}


int picdem_fs_usb_readtemp(struct usb_dev_handle * d)
{
   byte answer[reqLen];
   byte question[reqLen];
   int rawval;
   int umr;
   question[0] = 'T';
   if ((ierr = send_usb(d, 1, (char *)question)) != 0) return ierr;
   if ((ierr = recv_usb(d, 2, answer)) != 0) return ierr;
 
   rawval = answer[0] + (answer[1]*256);
  	umr = rawval / 8;  // Statusbits ausblenden
	umr = 625 * umr / 1000;  // Umrechnung von 1/16° zu 1/10°
	sprintf(outstring+strlen(outstring),"%d.%d; °C; ", umr/10, umr%10);
   return 0; 
}

int picdem_fs_usb_readlight(struct usb_dev_handle * d)
{
   byte answer[reqLen];
   byte question[reqLen];
   int rawval;
	int licht_rohwert, licht_messwert, mess_bereich;
#ifdef NEW_DEVICE
	int TslMw0, TslMw1;
#endif
   question[0] = 'L';
   if ((ierr = send_usb(d, 1, (char *)question)) != 0) return ierr;
#  ifdef NEW_DEVICE
   if ((ierr = recv_usb(d, 7, answer)) != 0) return ierr;
#  else
   /* the older 3 byte communication */
   if ((ierr = recv_usb(d, 3, answer)) != 0) return ierr;
#  endif
   rawval = answer[1] + (answer[2]<<8);

	mess_bereich  = answer[2];
	licht_rohwert = (256 * answer[1] + answer[0]);
#       ifdef NEW_DEVICE
	TslMw0 = 256 * answer[4] + answer[3];
	TslMw1 = 256 * answer[6] + answer[5];
#       endif	
	// aus A/D-Wert und Meßbereich Meßwert berechnen:
	switch (mess_bereich)
	{ case 1:
	    licht_messwert = licht_rohwert * 120;
		break;
	  case 2:
	    licht_messwert = licht_rohwert * 8;
		break;
	  case 3:
	    licht_messwert = licht_rohwert * 4;
		break;
	  case 4:
	    licht_messwert = licht_rohwert * 2;
		break;
	  case 5:
	    licht_messwert = licht_rohwert * 1;
		break;
	}

	// Formatierung für Ausgabe auf Monitor:
	if (licht_rohwert < 32000)
	{
#	 	ifdef NEW_DEVICE
		sprintf(outstring+strlen(outstring),"%d; %d; %d; ok;",
		        licht_messwert,TslMw0,TslMw1);
#		else
		sprintf(outstring+strlen(outstring),"%d; ok;", licht_messwert);
#		endif
	}
	else
	{
#	 	ifdef NEW_DEVICE
		sprintf(outstring+strlen(outstring),"%d; %d; %d; err;",
		        licht_messwert,TslMw0,TslMw1);
#		else
		sprintf(outstring+strlen(outstring),"%d; err;", licht_messwert);
#		endif
	}
        return 0;
}



/* debugging: enable debugging error messages in libusb */
extern int usb_debug;

/* Find the first USB device with this vendor and product.
   Exits on errors, like if the device couldn't be found.
*/
struct usb_dev_handle *usb_picdem_fs_usb_open(void)
{
  struct usb_device * device;
  struct usb_bus * bus;

  /*if( geteuid()!=0 )
	 bad("This program must be run as root, or made setuid root");
	 */
  printf("# HOSTNAME: "); system("hostname");
  printf("# Locating Microchip(tm) PICDEM(tm) FS USB Demo Board (vendor 0x%04x/product 0x%04x)\n", vendorID, productID);
  usb_init();
  usb_find_busses();
  usb_find_devices();
  for (bus=usb_get_busses();bus!=NULL;bus=bus->next) 
  {
	 struct usb_device * usb_devices = bus->devices;
	 for( device=usb_devices; device!=NULL; device=device->next )
	 {
		if( device->descriptor.idVendor == vendorID &&
			device->descriptor.idProduct == productID )
		{
		   struct usb_dev_handle *d;
		   printf("# Found USB PICDEM FS USB Demo Board as device '%s' on USB bus %s - ",
				   device->filename,
				   device->bus->dirname);
		   d = usb_open(device);
		   if( d )
		   { /* This is our device-- claim it */
			  if( usb_set_configuration(d, configuration) ) 
			  {
				 bad("Error setting USB configuration.\n");
			  }
			  if( usb_claim_interface(d, interface) ) 
			  {
				 bad("Claim failed-- the USB PICDEM FS USB is in use by another driver.\n");
			  }
			  printf(" Communication established. :");
			  system("date"); 
			  return d;
		   }
		   else 
			  bad("Open failed for USB device");
		}
		/* else some other vendor's device-- keep looking... */
	 }
  }
  bad("Could not find USB PICDEM FS USB Demo Board--\n"
      "you might try lsusb to see if it's actually there.");
  return NULL;
}

static void signal_handler(int sig) {
   /* code exits on SIGHUP regular - esle with signal as exit code */
   usb_close(picdem_fs_usb);
   if ((sig != SIGHUP) && (sig != SIGKILL)) exit(sig);
   else exit(0);
}

int main(int argc, char ** argv) 
{
   int sampling;
   signal(SIGHUP, signal_handler);
   signal(SIGTERM, signal_handler);
   signal(SIGKILL, signal_handler);
   signal(SIGQUIT, signal_handler);
   setbuf(stdout,NULL);	
   setbuf(stderr,NULL);	

   if (argc > 1) sampling = (atoi(argv[1]) < 1 ? 1 : atoi(argv[1]));
   else          sampling = 1;
   redo:

   picdem_fs_usb = usb_picdem_fs_usb_open();
   if (picdem_fs_usb == NULL) return -1;
   errcount = 0;
   while(errcount < MAX_ERROR) {   
       struct tm *tmp;
#      ifdef HIGH_SPEED
       struct timeb tp;
       outstring[0] = 0;
       ftime(&tp); 
       tmp = localtime(&tp.time);
       sprintf(outstring+strlen(outstring),"%i.%i.%i; %i:%2.2i:%2.2i.%4.4i; ",
               tmp->tm_mday,tmp->tm_mon+1,1900+tmp->tm_year,tmp->tm_hour,tmp->tm_min,tmp->tm_sec,tp.millitm);
#      else  
       time_t timer;
       outstring[0] = 0;
       timer = time(NULL);
       tmp = localtime(&timer);
       sprintf(outstring+strlen(outstring),"%i.%i.%i; %i:%2.2i:%2.2i; ",
               tmp->tm_mday,tmp->tm_mon+1,1900+tmp->tm_year,tmp->tm_hour,tmp->tm_min,tmp->tm_sec);
#      endif



#      ifdef TEMPERATURE
       if (picdem_fs_usb_readtemp(picdem_fs_usb) == 0) {
	   if (picdem_fs_usb_readlight(picdem_fs_usb) == 0) {
               errcount = 0;
	       printf("%s\n",outstring);
	       sleep(sampling);
           } else {
             errcount++;
             sleep(WAIT_ERROR);
           }
         } else {
           errcount++;
           sleep(WAIT_ERROR);
         }
#        else
	 if (picdem_fs_usb_readlight(picdem_fs_usb) == 0) {
               errcount = 0;
	       printf("%s\n",outstring);
#              ifdef HIGH_SPEED
	       /* usleep gets very inaccurate for timers below 1-3 milliseconds
                     if you require perfect timing an RTAI module is required (www.rtai.org) */
               usleep((SPEED*1000));
#              else
	       sleep(sampling);
#              endif
         } else {
             errcount++;
             sleep(WAIT_ERROR);
         }
#        endif
   }
   /* an error condition in read or write caused to come here 
      we thus retry the int process */
   usb_close(picdem_fs_usb);
   sleep(10); 
   printf("# ");system("date"); 
   printf("# closed for retry\n");
   goto redo; 
   /* you never be able to come here */
   return 0;
}
