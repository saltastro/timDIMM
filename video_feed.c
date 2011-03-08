#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <dc1394/dc1394.h>
#include <math.h>
#include <fitsio.h>
#include <xpa.h>
#include <time.h>
#include <sys/time.h>
#include <string.h>
#include <inttypes.h>

#define NXPA 10

int grab_frame(dc1394camera_t *c, char *buf, int nbytes) {
    dc1394video_frame_t *frame=NULL;
    dc1394error_t err;

    err = dc1394_capture_dequeue(c, DC1394_CAPTURE_POLICY_WAIT, &frame);
    if (err != DC1394_SUCCESS) {
	dc1394_log_error("Unable to capture.");
	dc1394_capture_stop(c);
	dc1394_camera_free(c);
	exit(1);
    }

    memcpy(buf, frame->image, nbytes);
    dc1394_capture_enqueue(c, frame);
    return 1;
}

int main(int argc, char *argv[]) {
    
    long nelements, naxes[2], fpixel;
    dc1394_t * dc;
    dc1394camera_t * camera;
    dc1394camera_list_t * list;
    dc1394error_t err;
    dc1394video_mode_t mode;
    unsigned int min_bytes, max_bytes, max_height, max_width, winleft, wintop;
    uint64_t total_bytes = 0;

    unsigned char *buffer, *buffer2;
    unsigned char *average;
    fitsfile *fptr;
    int i, j, f, fstatus, status, nimages, anynul, nboxes, test, xsize, ysize;
    int nbad = 0, nbad_l = 0;
    char filename[256], xpastr[256];
    char *timestr;
    FILE *init, *out, *cenfile;
    float xx = 0.0, yy = 0.0, xsum = 0.0, ysum = 0.0;
    double *dist, *sig, *dist_l, *sig_l, *weight, *weight_l;
    double mean, var, var_l, avesig, airmass;
    double r0, seeing_short, seeing_long, seeing_ave;
    struct timeval start_time, end_time;
    struct tm ut;
    time_t start_sec, end_sec;
    suseconds_t start_usec, end_usec;
    float elapsed_time, fps;

    unsigned int actual_bytes;
    char *names[NXPA];
    char *messages[NXPA];
    int packet;

    stderr = freopen("video.log", "w", stderr);

    srand48((unsigned)time(NULL));

    XPA xpa;
    xpa = XPAOpen(NULL);

    packet = atoi(argv[1]);

    fstatus = 0;
    status = 0;
    anynul = 0;
    xsize = 320;
    ysize = 240;
    naxes[0] = xsize;
    naxes[1] = ysize;
    fpixel = 1;
  
    nelements = naxes[0]*naxes[1];

    mode = DC1394_VIDEO_MODE_FORMAT7_1;
    dc = dc1394_new();
    if (!dc)
	return -1;
    err = dc1394_camera_enumerate(dc, &list);
    DC1394_ERR_RTN(err, "Failed to enumerate cameras.");

    if (list->num == 0) {
	dc1394_log_error("No cameras found.");
	return -1;
    }

    camera = dc1394_camera_new(dc, list->ids[0].guid);
    if (!camera) {
	dc1394_log_error("Failed to initialize camera with guid %"PRIx64".", 
			 list->ids[0].guid);
	return -1;
    }
    dc1394_camera_free_list(list);

    printf("Using camera with GUID %"PRIx64"\n", camera->guid);

    // need to use legacy firewire400 mode for now.  800 not quite reliable.
    dc1394_video_set_iso_speed(camera, DC1394_ISO_SPEED_400);

    // configure camera for format7
    err = dc1394_video_set_mode(camera, mode);
    DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Can't choose video mode.");

    err = dc1394_format7_get_max_image_size(camera, mode, &max_width, &max_height);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot get max image size.");
    printf ("I: max image size is: height = %d, width = %d\n", max_height, max_width);
    printf ("I: current image size is: height = %d, width = %d\n", ysize, xsize);

    winleft = 0;
    wintop = 0;

    err = dc1394_format7_set_roi(camera,
				 mode,
				 DC1394_COLOR_CODING_MONO8,
//				 DC1394_USE_MAX_AVAIL,
				 packet,
				 winleft, wintop, // left, top
				 xsize, ysize);
    DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Can't set ROI.");
    printf("I: ROI is (%d, %d) - (%d, %d)\n", 
	   winleft, wintop, winleft+xsize, wintop+ysize);

    err=dc1394_video_set_framerate(camera, DC1394_FRAMERATE_MAX);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set framerate");

    err = dc1394_feature_set_value (camera, DC1394_FEATURE_SHUTTER, 256);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set shutter");
    printf ("I: shutter is 50\n");

    err = dc1394_format7_get_total_bytes(camera, DC1394_VIDEO_MODE_FORMAT7_1, &total_bytes);
    DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Can't get total bytes.");
    printf("I: total bytes per frame are %"PRIu64"\n", total_bytes);

    err = dc1394_capture_setup(camera, 16, DC1394_CAPTURE_FLAGS_DEFAULT);
    DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Error capturing.");

    // start the camera up
    err = dc1394_video_set_transmission(camera, DC1394_ON);
    if (err != DC1394_SUCCESS) {
	dc1394_log_error("Unable to start camera iso transmission.");
	dc1394_capture_stop(camera);
	dc1394_camera_free(camera);
	return -1;
    }

    printf("Camera successfully initialized.\n");

    if (!(buffer = malloc(nelements*sizeof(char)))) {
	printf("Couldn't Allocate Image Buffer\n");
	exit(-1);
    }

   if (!(average = calloc(nelements, sizeof(char)))) {
       printf("Couldn't Allocate Average Image Buffer\n");
       exit(-1);
   }

   gettimeofday(&start_time, NULL);

    f = 0;

    while (1) {
	grab_frame(camera, buffer, nelements*sizeof(char));
//	for (j=0; j<nelements; j++) {
//	    average[j] += 0.1*(buffer[j]-average[j]);
//	}
	fits_create_file(&fptr, "!video.fits", &fstatus);
	fits_create_img(fptr, BYTE_IMG, 2, naxes, &fstatus);
	fits_write_img(fptr, TBYTE, fpixel, nelements, buffer, &fstatus);
	fits_close_file(fptr, &fstatus);
	fits_report_error(stdout, fstatus);

// 	if (f % 160 == 0) {
	  status = XPASet(xpa, "timDIMM", "array [xdim=320,ydim=240,bitpix=8]", "ack=false",
			  buffer, nelements, names, messages, NXPA);
	  sprintf(xpastr, "image; box 160.0 120.0 60 20 0.0");
          status = XPASet(xpa, "timDIMM", "regions", "ack=false",
                          xpastr, strlen(xpastr), names, messages, NXPA);
//	}
	f++;
    }

    gettimeofday(&end_time, NULL);
    printf("End capture.\n");

    start_sec = start_time.tv_sec;
    start_usec = start_time.tv_usec;
    end_sec = end_time.tv_sec;
    end_usec = end_time.tv_usec;

    elapsed_time = (float)((end_sec + 1.0e-6*end_usec) - (start_sec + 1.0e-6*start_usec));
    fps = nimages/elapsed_time;
    printf("Elapsed time = %g seconds.\n", elapsed_time);
    printf("Framerate = %g fps.\n", fps);

    /*-----------------------------------------------------------------------
     *  stop data transmission
     *-----------------------------------------------------------------------*/
    err=dc1394_video_set_transmission(camera,DC1394_OFF);
    DC1394_ERR_RTN(err,"couldn't stop the camera?");
    
    return (status);
}
