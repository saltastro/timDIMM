#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <dc1394/dc1394.h>
#include <math.h>
#include <fitsio.h>
#include <gsl/gsl_statistics.h>
#include <xpa.h>

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
int boxsize = 13;
float pixel_scale = 0.61;

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

  return 206265.0*0.98*lambda/r0;
}

/* measure the background in an annulus around the spot pattern */
int background(char *image) {

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
  if (up_y >= 480) {
    up_y = 479;
  }
  if (low_x < 0) {
    low_x = 0;
  }
  if (up_x >= 640) {
    up_x = 639;
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

  return 1;

}

/* measure centroid using center-of-mass algorithm */
int centroid(char *image, int num) {

  int i, j;
  double  sum    = 0.0;
  double  sumx   = 0.0;
  double  sumxx  = 0.0;
  double  sumy   = 0.0;
  double  sumyy  = 0.0;
  double  val = 0.0;
  double  rmom;
  double  dist;
  int low_y, up_y, low_x, up_x;
  int sourcepix = 0;

  low_y = box[num].y - box[num].r;
  up_y  = box[num].y + box[num].r;
  low_x = box[num].x - box[num].r;
  up_x  = box[num].x + box[num].r;
  if (low_y < 0) {
    low_y = 0;
  }
  if (up_y >= 480) {
    up_y = 479;
  }
  if (low_x < 0) {
    low_x = 0;
  }
  if (up_x >= 640) {
    up_x = 639;
  }

  for (i=low_y; i<up_y; i++) {
    for (j=low_x; j<up_x; j++) {

      dist = sqrt(pow(box[num].x-j, 2) + pow(box[num].y-i, 2));
      if (dist <= box[num].r) {
	val = image[i*naxes[0]+j] - back.background;
	sum   += val;
	sumx  += val*j;
	sumxx += val*j*j;
	sumy  += val*i;
	sumyy += val*i*i;
	sourcepix++;
      }

    }
  }

  if ( sum <= 0.0 ) {
    box[num].sigmaxy = -1.0;
    box[num].sigmafwhm = -1.0;
    box[num].cenx = 0.0;
    box[num].ceny = 0.0;
    box[num].fwhm = -1.0;
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
    box[num].x = box[num].cenx;
    box[num].y = box[num].ceny;
    box[num].sigmaxy= box[num].noise * sourcepix / box[num].counts / sqrt(6.0);
    box[num].sigmafwhm = box[num].noise * pow(sourcepix,1.5) / 10.
      / box[num].fwhm / box[num].counts
      * 2.354 * 2.354 / 2.0;
  }  

  return 1;

}

int main() {
  
  char *buffer, *buffer2, *average;
  fitsfile *fptr;
  int i, j, f, status, nimages, anynul, nboxes, test;
  char fitsfile[256];
  char *froot;
  FILE *init, *out;
  float xx = 0.0, yy = 0.0, xsum = 0.0, ysum = 0.0;
  double dist01[900], dist02[900], dist12[900];
  double sig01[900], sig02[900], sig12[900];
  double dist01_l[900], dist02_l[900], dist12_l[900];
  double sig01_l[900], sig02_l[900], sig12_l[900];
  double mean01, mean02, mean12;
  double var01, var02, var12;
  double avesig01, avesig02, avesig12;
  double seeing_ave_short, seeing_ave_long, seeing_ave;

  double d = 0.076;
  double r = 0.143;

  out = fopen("/dev/shm/video/seeing.dat", "a");
  init = fopen("/dev/shm/video/init_cen_all", "r");
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

  back.r = 40;
  back.width = 5;

  status = 0;
  anynul = 0;
  naxes[0] = 640;
  naxes[1] = 480;
  fpixel = 1;
  
  nelements = naxes[0]*naxes[1];

  /* init card */
  if (FB_Init() == RET_ERROR) {
    printf("FlashBus failed init\n");
    return(-1);
  }

  /* configure video capture */
  FB_SetVideoConfig(TYPE_COMPOSITE, STANDARD_NTSC, 1, 0);

  /* set up offscreen video capture */
  if (FB_VideoOffscreen(naxes[0], naxes[1], 8, TRUE) != RET_SUCCESS) {
    printf("Couldn't set offscreen capture\n");
    return(-1);
  }
 
  /* allocate the buffers */
  if (!(buffer = malloc(nelements*sizeof(char)))) {
    printf("Couldn't Allocate Image Buffer\n");
    exit(-1);
  }
  if (!(buffer2 = malloc(nelements*sizeof(char)))) {
    printf("Couldn't Allocate 2nd Image Buffer\n");
    exit(-1);
  }
  if (!(average = malloc(nelements*sizeof(float)))) {
    printf("Couldn't Allocate Average Image Buffer\n");
    exit(-1);
  }

  FB_VideoLive(TRUE, ALIGN_ANY);
  FB_WaitVSync(12);

  nimages = 500;
  froot = "/dev/shm/video/seeing.fits";

  for (f=0; f<nimages; f++) {
    /* first do a single exposure */
    FB_WaitVSync(1);
    FB_CopyVGARect(0, 
		   0, 
		   naxes[0], 
		   naxes[1], 
		   buffer, 
		   -1, 
		   COPYDIR_FROMOFFSCREEN);
    xsum = 0.0;
    ysum = 0.0;
    for (i=0; i<nboxes; i++) {
      xsum += box[i].cenx;
      ysum += box[i].ceny;
    }
    back.x = xsum/nboxes;
    back.y = ysum/nboxes;
    background(buffer);

    for (i=0; i<nboxes; i++) {
      box[i].noise = back.sigma;
      //box[i].r = boxsize/2.0;
      centroid(buffer, i);
      //box[i].r = boxsize/3.0;
      centroid(buffer, i);
      //box[i].r = boxsize/4.0;
      centroid(buffer, i);
    }

    dist01[f] = stardist(0, 1);
    sig01[f] = box[0].sigmaxy*box[0].sigmaxy + box[1].sigmaxy*box[1].sigmaxy;

    dist02[f] = stardist(0, 2);
    sig02[f] = box[0].sigmaxy*box[0].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;

    dist12[f] = stardist(1, 2);
    sig12[f] = box[1].sigmaxy*box[1].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;

    /* now average two exposures */
    FB_WaitVSync(1);
    FB_CopyVGARect(0, 
		   0, 
		   naxes[0], 
		   naxes[1], 
		   buffer, 
		   -1, 
		   COPYDIR_FROMOFFSCREEN);
    FB_WaitVSync(1);
    FB_CopyVGARect(0, 
		   0, 
		   naxes[0], 
		   naxes[1], 
		   buffer2, 
		   -1, 
		   COPYDIR_FROMOFFSCREEN);
    for (j=0; j<nelements; j++) {
      test = buffer[j]+buffer2[j];
      if (test <= 254) {
	average[j] = buffer[j]+buffer2[j];
      } else {
	average[j] = 254;
      }
    }
    xsum = 0.0;
    ysum = 0.0;
    for (i=0; i<nboxes; i++) {
      xsum += box[i].cenx;
      ysum += box[i].ceny;
    }
    back.x = xsum/nboxes;
    back.y = ysum/nboxes;
    background(average);

    for (i=0; i<nboxes; i++) {
      box[i].noise = back.sigma;
      //box[i].r = boxsize/2.0;
      centroid(average, i);
      //box[i].r = boxsize/3.0;
      centroid(average, i);
      //box[i].r = boxsize/4.0;
      centroid(average, i);
    }

    dist01_l[f] = stardist(0, 1);
    sig01_l[f] = box[0].sigmaxy*box[0].sigmaxy + box[1].sigmaxy*box[1].sigmaxy;

    dist02_l[f] = stardist(0, 2);
    sig02_l[f] = box[0].sigmaxy*box[0].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;

    dist12_l[f] = stardist(1, 2);
    sig12_l[f] = box[1].sigmaxy*box[1].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;

  }

  sprintf(fitsfile, "!%s", froot);
  fits_create_file(&fptr, fitsfile, &status);
  fits_create_img(fptr, BYTE_IMG, 2, naxes, &status);
  fits_write_img(fptr, TBYTE, fpixel, nelements, buffer, &status);
  fits_close_file(fptr, &status);
  fits_report_error(stderr, status);

  /* analyze short exposure */
  printf("\t SHORT EXPOSURE\n");
  mean01 = gsl_stats_mean(dist01, 1, nimages);
  avesig01 = gsl_stats_mean(sig01, 1, nimages);
  printf("mean01 = %f, avesig01 = %f\n", mean01, avesig01);

  mean02 = gsl_stats_mean(dist02, 1, nimages);
  avesig02 = gsl_stats_mean(sig02, 1, nimages);
  printf("mean02 = %f, avesig02 = %f\n", mean02, avesig02);

  mean12 = gsl_stats_mean(dist12, 1, nimages);
  avesig12 = gsl_stats_mean(sig12, 1, nimages);
  printf("mean12 = %f, avesig12 = %f\n", mean12, avesig12);

  printf("\n");

  var01 = gsl_stats_variance_m(dist01, 1, nimages, mean01);
  var01 = var01 - avesig01;
  printf("sigma01 = %f, seeing01 = %f\n", sqrt(var01), seeing(var01, d, r));

  var02 = gsl_stats_variance_m(dist02, 1, nimages, mean02);
  var02 = var02 - avesig02;
  printf("sigma02 = %f, seeing02 = %f\n", sqrt(var02), seeing(var02, d, r));

  var12 = gsl_stats_variance_m(dist12, 1, nimages, mean12);
  var12 = var12 - avesig12;
  printf("sigma12 = %f, seeing12 = %f\n", sqrt(var12), seeing(var12, d, r));

  seeing_ave_short = (seeing(var01, d, r) +
		      seeing(var02, d, r) +
		      seeing(var12, d, r))/3.0;

  printf("Ave. short exposure seeing = %4.2f\"\n", seeing_ave_short);

  fprintf(out, "short = %f %f %f\n", 
	  seeing(var01, d, r),
	  seeing(var02, d, r),
	  seeing(var12, d, r));

  /* analyze long exposure */
  printf("\t LONG EXPOSURE\n");
  mean01 = gsl_stats_mean(dist01_l, 1, nimages);
  avesig01 = gsl_stats_mean(sig01_l, 1, nimages);
  printf("mean01 = %f, avesig01 = %f\n", mean01, avesig01);

  mean02 = gsl_stats_mean(dist02_l, 1, nimages);
  avesig02 = gsl_stats_mean(sig02_l, 1, nimages);
  printf("mean02 = %f, avesig02 = %f\n", mean02, avesig02);

  mean12 = gsl_stats_mean(dist12_l, 1, nimages);
  avesig12 = gsl_stats_mean(sig12_l, 1, nimages);
  printf("mean12 = %f, avesig12 = %f\n", mean12, avesig12);

  printf("\n");

  var01 = gsl_stats_variance_m(dist01_l, 1, nimages, mean01);
  var01 = var01 - avesig01;
  printf("sigma01 = %f, seeing01 = %f\n", sqrt(var01), seeing(var01, d, r));

  var02 = gsl_stats_variance_m(dist02_l, 1, nimages, mean02);
  var02 = var02 - avesig02;
  printf("sigma02 = %f, seeing02 = %f\n", sqrt(var02), seeing(var02, d, r));

  var12 = gsl_stats_variance_m(dist12_l, 1, nimages, mean12);
  var12 = var12 - avesig12;
  printf("sigma12 = %f, seeing12 = %f\n", sqrt(var12), seeing(var12, d, r));

  seeing_ave_long = (seeing(var01, d, r) +
		     seeing(var02, d, r) +
		     seeing(var12, d, r))/3.0;

  printf("Ave. long exposure seeing = %4.2f\"\n", seeing_ave_long);

  fprintf(out, "long = %f %f %f\n", 
	  seeing(var01, d, r),
	  seeing(var02, d, r),
	  seeing(var12, d, r));
	  
  seeing_ave = pow(seeing_ave_short, 1.75)*pow(seeing_ave_long,-0.75);
  printf("Exposure corrected seeing = %4.2f\"\n\n", seeing_ave);

  fprintf(out, "short ave = %f\n", seeing_ave_short);
  fprintf(out, "long ave  = %f\n", seeing_ave_long);
  fprintf(out, "corr ave  = %f\n", seeing_ave);

  init = fopen("/dev/shm/video/init_cen_all", "w");
  for (i=0; i<nboxes; i++) {
    fprintf(init, "%f %f\n", box[i].cenx, box[i].ceny);
  }
  fclose(init);

  fclose(out);

  return (status);
}
