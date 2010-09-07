#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <dc1394/dc1394.h>
#include <math.h>
#include <fitsio.h>
#include <gsl/gsl_statistics.h>
#include <xpa.h>
#include <time.h>
#include <sys/time.h>
#include <string.h>
#include <inttypes.h>

#define NXPA 10

typedef struct _Box {
    double  x;
    double  y;
    double  fwhm;
    double  cenx;
    double  ceny;
    double  counts;
    double  background;
    double  noise;
    double  sigmaxythresh;
    double  snr;
    double  sigmaxy;
    double  sigmafwhmthresh;
    double  sigmafwhm;
    int     r;
} Box;

typedef struct _Back {
    double x;
    double y;
    double background;
    double sigma;
    int r;
    int width;
} Back;

Box box[3];
Back back;
long nelements, naxes[2], fpixel;
int boxsize = 20;
double pixel_scale = 1.22;

double stardist(int i, int j) {
    return( sqrt( (box[i].cenx-box[j].cenx)*(box[i].cenx-box[j].cenx) +
		  (box[i].ceny-box[j].ceny)*(box[i].ceny-box[j].ceny) ) );
}

/* this routine uses a. tokovinin's modified equation given in
   2002, PASP, 114, 1156
*/
double seeing(double var, double d, double r) {
    double lambda;
    double b, K, seeing;

    lambda = 0.65e-6;
    b = r/d;
    
    /* pixel scale in "/pixel, convert to rad */
    var = var*pow(pixel_scale/206265.0,2);
    
    K = 0.364*(1.0 - 0.532*pow(b, -1/3) - 0.024*pow(b, -7/3));

    seeing = 206265.0*0.98*pow(d/lambda, 0.2)*pow(var/K, 0.6);

    return seeing;
}

/* this routine uses the classic DIMM equation */
double old_seeing(double var, double d, double r) {
    double lambda;
    double r0;

    lambda = 0.65e-6;

    /* pixel scale in "/pixel, convert to rad */
    var = var*pow(pixel_scale/206265.0,2);
    
    r0 = pow(2.0*(lambda*lambda)*( 
		 ( 0.1790*pow(d, (-1.0/3.0)) - 
		   0.0968*pow(r, (-1.0/3.0)) )/var 
		 ), 0.6);

    // return 206265.0*0.98*lambda/r0;
    return r0;
}

/* measure the background in an annulus around the spot pattern */
int background(char *image, int imwidth, int imheight) {

    int i, j, backpix;
    int low_y, up_y, low_x, up_x;
    double dist, sum, sumsq;
    
    backpix = 0;
    sum = 0.0;
    sumsq = 0.0;

    low_y = back.y - back.r - back.width;
    up_y  = back.y + back.r + back.width;
    low_x = back.x - back.r - back.width;
    up_x  = back.x + back.r + back.width;
    if (low_y < 0) {
	low_y = 0;
    }
    if (up_y >= imheight) {
	up_y = imheight;
    }
    if (low_x < 0) {
	low_x = 0;
    }
    if (up_x >= imwidth) {
	up_x = imwidth;
    }

    for (i=low_y; i<up_y; i++) {
	for (j=low_x; j<up_x; j++) {
	    dist = sqrt(pow(back.x-j, 2) + pow(back.y-i, 2));
	    if (dist >= back.r && dist <= back.r+back.width) {
		sum += image[i*naxes[0]+j];
		backpix++;
	    }
	}
    }

    back.background = sum/backpix;
    //back.background = 0.0;

    for (i=low_y; i<up_y; i++) {
	for (j=low_x; j<up_x; j++) {
	    dist = sqrt(pow(back.x-j, 2) + pow(back.y-i, 2));
	    if (dist >= back.r && dist <= back.r+back.width) {
		sumsq += (image[i*naxes[0]+j]-back.background)*
		    (image[i*naxes[0]+j]-back.background);
	    }
	}
    }

    back.sigma = sqrt(sumsq/backpix);
    //back.sigma = 1.0;

    return 1;

}

/* measure centroid using center-of-mass algorithm */
int centroid(char *image, int imwidth, int imheight, int num) {

    int i, j;
    double  sum    = 0.0;
    double  sumx   = 0.0;
    double  sumxx  = 0.0;
    double  sumy   = 0.0;
    double  sumyy  = 0.0;
    double  val = 0.0;
    double  gain = 0.7;
    double  rmom;
    double  dist;
    double nsigma = 4.0;
    int low_y, up_y, low_x, up_x;
    int sourcepix = 0;

    low_y = box[num].y - box[num].r;
    up_y  = box[num].y + box[num].r;
    low_x = box[num].x - box[num].r;
    up_x  = box[num].x + box[num].r;
    if (low_y < 0) {
	low_y = 0;
    }
    if (up_y >= imheight) {
	up_y = imheight;
    }
    if (low_x < 0) {
	low_x = 0;
    }
    if (up_x >= imwidth) {
	up_x = imwidth;
    }
    
    for (i=low_y; i<up_y; i++) {
	for (j=low_x; j<up_x; j++) {
	    
	    dist = sqrt(pow(box[num].x-j, 2) + pow(box[num].y-i, 2));
	    if (dist <= box[num].r) {
		val = image[i*naxes[0]+j] - back.background;
		if (val >= nsigma*back.sigma) {
		    sum   += val;
		    sumx  += val*j;
		    sumxx += val*j*j;
		    sumy  += val*i;
		    sumyy += val*i*i;
		    sourcepix++;
		}
	    }
	    
	}
    }

    if ( sum <= 0.0 ) {
	box[num].sigmaxy = -1.0;
	box[num].sigmafwhm = -1.0;
	box[num].snr = 0.0;
	box[num].fwhm = -1.0;
	box[num].counts = 1.0;
    } else {
	rmom = ( sumxx - sumx * sumx / sum + sumyy - sumy * sumy / sum ) / sum;
	
	if ( rmom <= 0 ) {
	    box[num].fwhm = -1.0;
	} else {
	    box[num].fwhm = sqrt(rmom)  * 2.354 / sqrt(2.0);
	}

	box[num].counts = sum;
	box[num].cenx   = sumx / sum;
	box[num].ceny   = sumy / sum;
	box[num].noise  = back.sigma*sourcepix;
	box[num].x += gain*(box[num].cenx - box[num].x);
	box[num].y += gain*(box[num].ceny - box[num].y);
	box[num].snr = sum/sqrt(box[num].noise*box[num].noise*sourcepix*sourcepix 
				+ sum);
	box[num].sigmaxy = 1.0 / box[num].snr / sqrt(6.0);
	box[num].sigmafwhm = back.sigma * pow(sourcepix,1.5) / 10.
	    / box[num].fwhm / box[num].counts
	    * 2.354 * 2.354 / 2.0;
    }  

    return 1;

}

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

int add_gaussian(char *buffer, float cenx, float ceny, float a, float sigma) {
    float gauss, rsq;
    int i, j, low_x, up_x, low_y, up_y, size;
    double xoff, yoff;

    xoff = 2.0*drand48() - 1.0;
    yoff = 2.0*drand48() - 1.0;

    cenx += 0.5*xoff;
    ceny += 0.5*yoff;

    size = 30;
    low_x = (int)(cenx-size);
    up_x = (int)(cenx+size);
    low_y = (int)(ceny-size);
    up_y = (int)(ceny+size);

    for (i=low_y; i<up_y; i++) {
	for (j=low_x; j<up_x; j++) {
	    rsq = (cenx - j)*(cenx - j) + (ceny - i)*(ceny - i);
	    gauss = a*expf(-1.0*rsq/(sigma*sigma));
	    if (gauss > 255) 
		gauss = 255;
	    buffer[i*naxes[0]+j] += (char)gauss;
	}
    }

    return 1;
}

int main(int argc, char *argv[]) {
    
    dc1394_t * dc;
    dc1394camera_t * camera;
    dc1394camera_list_t * list;
    dc1394error_t err;
    dc1394video_mode_t mode;
    unsigned int min_bytes, max_bytes, max_height, max_width, winleft, wintop;
    uint64_t total_bytes = 0;

    char *buffer, *buffer2, *average;
    fitsfile *fptr;
    int i, j, f, fstatus, status, nimages, anynul, nboxes, test, xsize, ysize;
    int nbad = 0, nbad_l = 0;
    char filename[256], xpastr[256];
    char *froot, *timestr;
    FILE *init, *out, *cenfile;
    float xx = 0.0, yy = 0.0, xsum = 0.0, ysum = 0.0;
    double *dist, *sig, *dist_l, *sig_l, *weight, *weight_l;
    double mean, var, var_l, avesig;
    double r0, seeing_short, seeing_long, seeing_ave;
    struct timeval start_time, end_time;
    struct tm ut;
    time_t start_sec, end_sec;
    suseconds_t start_usec, end_usec;
    float elapsed_time, fps;

    unsigned int actual_bytes;
    char *names[NXPA];
    char *messages[NXPA];

    double d = 0.060;
    double r = 0.130;
    srand48((unsigned)time(NULL));

    XPA xpa;
    xpa = XPAOpen(NULL);

    stderr = freopen("measure_seeing.log", "w", stderr);

    if (argc <= 1) {
	printf("Must specifiy number of measurements.\n");
	exit(-1);
    }

    nimages = atoi(argv[1]);
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
				 DC1394_USE_MAX_AVAIL,
				 winleft, wintop, // left, top
				 xsize, ysize);
    DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Can't set ROI.");
    printf("I: ROI is (%d, %d) - (%d, %d)\n", 
	   winleft, wintop, winleft+xsize, wintop+ysize);

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

    out = fopen("seeing.dat", "a");
    cenfile = fopen("centroids.dat", "w");
    init = fopen("init_cen_all", "r");

    i = 0;
    while (fscanf(init, "%f %f\n", &xx, &yy) != EOF) {
	box[i].x = xx;
	box[i].cenx = xx;
	box[i].y = yy;
	box[i].ceny = yy;
	box[i].r = boxsize/2.0;
	i++;
    }
    nboxes = i;
    fclose(init); 

    back.r = 60;
    back.width = 10;

    /* allocate the buffers */
    if (!(dist = calloc(nimages, sizeof(double)))) {
	printf("Couldn't allocate dist array.\n");
	exit(-1);
    }
    if (!(sig = calloc(nimages, sizeof(double)))) {
	printf("Couldn't allocate sig array.\n");
	exit(-1);
    }
    if (!(weight = calloc(nimages, sizeof(double)))) {
	printf("Couldn't allocate sig array.\n");
	exit(-1);
    }
    if (!(weight_l = calloc(nimages, sizeof(double)))) {
	printf("Couldn't allocate sig array.\n");
	exit(-1);
    }
    if (!(dist_l = calloc(nimages, sizeof(double)))) {
	printf("Couldn't allocate dist_l array.\n");
	exit(-1);
    }
    if (!(sig_l = calloc(nimages, sizeof(double)))) {
	printf("Couldn't allocate sig_l array.\n");
	exit(-1);
    }
    if (!(buffer = malloc(nelements*sizeof(char)))) {
	printf("Couldn't Allocate Image Buffer\n");
	exit(-1);
    }
    if (!(buffer2 = malloc(nelements*sizeof(char)))) {
	printf("Couldn't Allocate 2nd Image Buffer\n");
	exit(-1);
    }
    if (!(average = malloc(nelements*sizeof(char)))) {
	printf("Couldn't Allocate Average Image Buffer\n");
	exit(-1);
    }

    froot = "seeing.fits";

    gettimeofday(&start_time, NULL);

    /* get initial frame */
    grab_frame(camera, buffer2, nelements*sizeof(char));
    // add_gaussian(buffer2, 195.0, 130.0, 100.0, 2.0);
    // add_gaussian(buffer2, 140.0, 115.0, 100.0, 2.0);

    for (f=0; f<nimages; f++) {
	grab_frame(camera, buffer, nelements*sizeof(char));
	// add_gaussian(buffer, 195.0, 130.0, 15.0, 2.0);
	// add_gaussian(buffer, 140.0, 115.0, 15.0, 2.0);

	// find center of star images and calculate background
	xsum = 0.0;
	ysum = 0.0;
	for (i=0; i<nboxes; i++) {
	    xsum += box[i].cenx;
	    ysum += box[i].ceny;
	}
	back.x = xsum/nboxes;
	back.y = ysum/nboxes;
	background(buffer, naxes[0], naxes[1]);
	
	for (i=0; i<nboxes; i++) {
	    box[i].r = boxsize/2.0;
	    centroid(buffer, naxes[0], naxes[1], i);
	    if (box[i].fwhm > 0.0) {
		fprintf(cenfile,
			"%6.2f %6.2f %5.2f %.4f %.4f %.4f %.4f %.4f \t ",
			box[i].cenx,
			box[i].ceny,
			box[i].fwhm,
			box[i].counts,
			back.background,
			box[i].noise,
			box[i].sigmaxy,
			box[i].snr);
	    }
	}

	if (box[0].snr < box[1].snr) {
	    weight[f] = (box[0].snr/box[0].counts)*(box[0].snr/box[0].counts);
	} else {
	    weight[f] = (box[1].snr/box[1].counts)*(box[1].snr/box[1].counts);
	}

	if (weight[f] == 0.0) {
	    nbad++;
	}

	dist[f] = stardist(0, 1);
	if (dist[f] > 60.0 || dist[f] < 10.0) {
	  printf("\n\n\033[0;31mABORTING measurement!  Lost at least one box.\033[0;39m\n\n");
	  status = -1;
	  return(status);
	}
	sig[f] = sqrt(box[0].sigmaxy*box[0].sigmaxy + box[1].sigmaxy*box[1].sigmaxy);
	fprintf(cenfile, "%.2f %.2f\n", dist[f], sig[f]);


	/* now average two exposures */
	for (j=0; j<nelements; j++) {
	  test = (int)buffer[j] + (int)buffer2[j];
	    if (test <= 254) {
		average[j] = buffer[j]+buffer2[j];
	    } else {
		average[j] = 254;
	    }
	}
	memcpy(buffer2, buffer, nelements*sizeof(char));

	xsum = 0.0;
	ysum = 0.0;
	for (i=0; i<nboxes; i++) {
	    xsum += box[i].cenx;
	    ysum += box[i].ceny;
	}
	back.x = xsum/nboxes;
	back.y = ysum/nboxes;
	background(average, naxes[0], naxes[1]);

	for (i=0; i<nboxes; i++) {
	    box[i].r = boxsize/2.0;
	    //centroid(average, i);
	    //box[i].r = boxsize/3.0;
	    //centroid(average, i);
	    //box[i].r = boxsize/4.0;
	    centroid(average, naxes[0], naxes[1], i);
	}

	if (box[0].snr < box[1].snr) {
	    weight_l[f] = (box[0].snr/box[0].counts)*(box[0].snr/box[0].counts);
	} else {
	    weight_l[f] = (box[1].snr/box[1].counts)*(box[1].snr/box[1].counts);
	}

	if (weight_l[f] == 0.0) {
	    nbad_l++;
	}

	dist_l[f] = stardist(0, 1);
	sig_l[f] = sqrt(box[0].sigmaxy*box[0].sigmaxy + box[1].sigmaxy*box[1].sigmaxy);

	sprintf(filename, "!%s", froot);
	fits_create_file(&fptr, "!seeing.fits", &fstatus);
	fits_create_img(fptr, BYTE_IMG, 2, naxes, &fstatus);
	fits_write_img(fptr, TBYTE, fpixel, nelements, buffer, &fstatus);
	fits_close_file(fptr, &fstatus);
	fits_report_error(stdout, fstatus);

 	if (f % 160 == 0) {
	  status = XPASet(xpa, "timDIMM", "array [xdim=320,ydim=240,bitpix=8]", "ack=false",
			  buffer, nelements, names, messages, NXPA);
	  sprintf(xpastr, "image; box %f %f %d %d 0.0",
		  box[0].x, box[0].y, boxsize, boxsize);
	  status = XPASet(xpa, "timDIMM", "regions", "ack=false",
			  xpastr, strlen(xpastr), names, messages, NXPA);
	  sprintf(xpastr, "image; box %f %f %d %d 0.0",
		  box[1].x, box[1].y, boxsize, boxsize);
	  status = XPASet(xpa, "timDIMM", "regions", "ack=false",
			  xpastr, strlen(xpastr), names, messages, NXPA);
	}
	
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
    
    /* analyze short exposure */
    printf("\t SHORT EXPOSURE\n");
    mean = gsl_stats_wmean(weight, 1, dist, 1, nimages);
    avesig = gsl_stats_mean(sig, 1, nimages);
    printf("mean = %f, avesig = %f\n", mean, avesig);
    
    printf("\n");

    var = gsl_stats_wvariance_m(weight, 1, dist, 1, nimages, mean);
    var = var - avesig;
    seeing_short = seeing(var, d, r);
    r0 = old_seeing(var, d, r);
    printf("sigma = %f, seeing = %f\n", sqrt(var), seeing_short);

    /* analyze long exposure */
    printf("\t LONG EXPOSURE\n");
    mean = gsl_stats_wmean(weight_l, 1, dist_l, 1, nimages);
    avesig = gsl_stats_mean(sig_l, 1, nimages);
    printf("mean_l = %f, avesig_l = %f\n", mean, avesig);

    printf("\n");

    var_l = gsl_stats_wvariance_m(weight_l, 1, dist_l, 1, nimages, mean);
    var_l = var_l - avesig;
    seeing_long = seeing(var_l, d, r);
    printf("sigma_l = %f, seeing_l = %f\n", sqrt(var_l), seeing_long);

    printf("Bad samples:  %d for short, %d for long.\n", nbad, nbad_l);

    seeing_ave = pow(seeing_short, 1.75)*pow(seeing_long,-0.75);
    printf("\033[0;31mExposure corrected seeing = %4.2f\"\033[0;39m\n\n", seeing_ave);
    printf("\033[0;31mFried Parameter, R0 = %.2f cm\033[0;39m\n\n", 100*r0);

    timestr = ctime(&end_sec);
    gmtime_r(&end_sec, &ut);
    fprintf(out, "%d-%02d-%02d %02d:%02d:%02d %f %f %f %f %f\n", 
	    ut.tm_year+1900, 
	    ut.tm_mon+1, 
	    ut.tm_mday, 
	    ut.tm_hour, 
	    ut.tm_min, 
	    ut.tm_sec, 
	    var, 
	    var_l, 
	    seeing_short, 
	    seeing_long, 
	    seeing_ave);

    init = fopen("init_cen_all", "w");
    for (i=0; i<nboxes; i++) {
	fprintf(init, "%f %f\n", box[i].cenx, box[i].ceny);
    }
    fclose(init);
    init = fopen("seeing.out", "w");
    fprintf(init, "%.2f\n", seeing_ave);
    fclose(init);
    init = fopen("r0.out", "w");
    fprintf(init, "%.1f\n", 100*r0);
    fclose(init);
    fclose(cenfile);
    fclose(out);

    return (status);
}
