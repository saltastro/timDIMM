#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <fitsio.h>
#include <gsl/gsl_statistics.h>

#ifdef SPECTRIM
#include "FBSpectrim.h"
#else
#include "fbus.h"
#endif

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

Box box[4];
Back back;
long nelements, naxes[2], fpixel;
int boxsize = 13;

double stardist(int i, int j) {
  return( sqrt( (box[i].cenx-box[j].cenx)*(box[i].cenx-box[j].cenx) +
		(box[i].ceny-box[j].ceny)*(box[i].ceny-box[j].ceny) ) );
}

double seeing(double var, double d, double r) {
  double lambda;
  double b, K, seeing;

  lambda = 0.65e-6;
  b = r/d;

  /* pixel scale of 0.78 "/pixel, convert to rad */
  var = var*pow(0.78/206265.0,2);

  K = 0.364*(1.0 - 0.532*pow(b, -1/3) - 0.024*pow(b, -7/3));

  seeing = 206265.0*0.98*pow(d/lambda, 0.2)*pow(var/K, 0.6);

  return seeing;
}

double old_seeing(double var, double d, double r) {
  double lambda;
  double r0;

  lambda = 0.55e-6;

  /* pixel scale of 0.78 "/pixel, convert to rad */
  var = var*pow(0.78/206265.0,2);

  r0 = pow(2.0*(lambda*lambda)*( 
				( 0.1790*pow(d, (-1.0/3.0)) - 
				  0.0968*pow(r, (-1.0/3.0)) )/var 
				), 0.6);

  return 206265.0*0.98*lambda/r0;
}

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
  
  char * buffer;
  fitsfile *fptr;
  int i, j, f, status, nimages, anynul, nboxes;
  char fitsfile[256];
  char *froot;
  FILE *init, *out;
  float xx = 0.0, yy = 0.0, xsum = 0.0, ysum = 0.0;
  double dist01[900], dist02[900], dist03[900];
  double dist12[900], dist13[900], dist23[900];
  double sig01[900], sig02[900], sig03[900];
  double sig12[900], sig13[900], sig23[900];
  double mean01, mean02, mean03, mean12, mean13, mean23;
  double var01, var02, var03, var12, var13, var23, rad;
  double avesig01, avesig02, avesig03, avesig12, avesig13, avesig23;
  double d = 0.05;
  double r_01, r_02, r_03, r_12, r_13, r_23, seeing_ave;
  r_01 = 2.0*d;
  r_02 = 2.0*d;
  r_03 = 3.0*d;
  r_12 = 3.0*d;
  r_13 = 2.0*d;
  r_23 = 2.0*d;

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
 
  /* allocate the buffer */
  if (!(buffer = malloc(nelements*sizeof(char)))) {
    printf("Couldn't Allocate Image Buffer\n");
    exit(-1);
  }

  FB_VideoLive(TRUE, ALIGN_ANY);
  FB_WaitVSync(12);

  nimages = 900;
  froot = "/dev/shm/video/seeing.fits";

  for (f=0; f<nimages; f++) {
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
    for (i=0; i<4; i++) {
      xsum += box[i].cenx;
      ysum += box[i].ceny;
    }
    back.x = xsum/4.0;
    back.y = ysum/4.0;
    background(buffer);

    //printf("file: %s  \t  background = %f noise = %f\n", 
    //	   fitsfile, back.background, back.sigma);

    for (i=0; i<4; i++) {
      box[i].noise = back.sigma;
      //box[i].r = boxsize/2.0;
      centroid(buffer, i);
      //box[i].r = boxsize/3.0;
      centroid(buffer, i);
      //box[i].r = boxsize/4.0;
      centroid(buffer, i);

      /* printf("\t star = %d, counts = %f, \n\t x = %f, y = %f, sigmaxy = %f\n", 
	     i,
	     box[i].counts,
	     box[i].cenx+1,
	     box[i].ceny+1, 
	     box[i].sigmaxy);
      */
    }

    dist01[f] = stardist(0, 1);
    sig01[f] = box[0].sigmaxy*box[0].sigmaxy + box[1].sigmaxy*box[1].sigmaxy;

    dist02[f] = stardist(0, 2);
    sig02[f] = box[0].sigmaxy*box[0].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;

    dist03[f] = stardist(0, 3);
    sig03[f] = box[0].sigmaxy*box[0].sigmaxy + box[3].sigmaxy*box[3].sigmaxy;

    dist12[f] = stardist(1, 2);
    sig12[f] = box[1].sigmaxy*box[1].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;

    dist13[f] = stardist(1, 3);
    sig13[f] = box[1].sigmaxy*box[1].sigmaxy + box[3].sigmaxy*box[3].sigmaxy;

    dist23[f] = stardist(2, 3);
    sig23[f] = box[3].sigmaxy*box[3].sigmaxy + box[2].sigmaxy*box[2].sigmaxy;
 
  }

  sprintf(fitsfile, "!%s", froot);
  fits_create_file(&fptr, fitsfile, &status);
  fits_create_img(fptr, BYTE_IMG, 2, naxes, &status);
  fits_write_img(fptr, TBYTE, fpixel, nelements, buffer, &status);
  fits_close_file(fptr, &status);
  fits_report_error(stderr, status);

  mean01 = gsl_stats_mean(dist01, 1, nimages);
  avesig01 = gsl_stats_mean(sig01, 1, nimages);
  printf("mean01 = %f, avesig01 = %f\n", mean01, avesig01);

  mean02 = gsl_stats_mean(dist02, 1, nimages);
  avesig02 = gsl_stats_mean(sig02, 1, nimages);
  printf("mean02 = %f, avesig02 = %f\n", mean02, avesig02);

  mean03 = gsl_stats_mean(dist03, 1, nimages);
  avesig03 = gsl_stats_mean(sig03, 1, nimages);
  printf("mean03 = %f, avesig03 = %f\n", mean03, avesig03);

  mean12 = gsl_stats_mean(dist12, 1, nimages);
  avesig12 = gsl_stats_mean(sig12, 1, nimages);
  printf("mean12 = %f, avesig12 = %f\n", mean12, avesig12);

  mean13 = gsl_stats_mean(dist13, 1, nimages);
  avesig13 = gsl_stats_mean(sig13, 1, nimages);
  printf("mean13 = %f, avesig13 = %f\n", mean13, avesig13);

  mean23 = gsl_stats_mean(dist23, 1, nimages);
  avesig23 = gsl_stats_mean(sig23, 1, nimages);
  printf("mean23 = %f, avesig23 = %f\n", mean23, avesig23);

  printf("\n");

  var01 = gsl_stats_variance_m(dist01, 1, nimages, mean01);
  var01 = var01 - avesig01;
  printf("sigma01 = %f, seeing01 = %f\n", sqrt(var01), seeing(var01, d, r_01));

  var02 = gsl_stats_variance_m(dist02, 1, nimages, mean02);
  var02 = var02 - avesig02;
  printf("sigma02 = %f, seeing02 = %f\n", sqrt(var02), seeing(var02, d, r_02));

  var03 = gsl_stats_variance_m(dist03, 1, nimages, mean03);
  var03 = var03 - avesig03;
  printf("sigma03 = %f, seeing03 = %f\n", sqrt(var03), seeing(var03, d, r_03));

  var12 = gsl_stats_variance_m(dist12, 1, nimages, mean12);
  var12 = var12 - avesig12;
  printf("sigma12 = %f, seeing12 = %f\n", sqrt(var12), seeing(var12, d, r_12));

  var13 = gsl_stats_variance_m(dist13, 1, nimages, mean13);
  var13 = var13 - avesig13;
  printf("sigma13 = %f, seeing13 = %f\n", sqrt(var13), seeing(var13, d, r_13));

  var23 = gsl_stats_variance_m(dist23, 1, nimages, mean23);
  var23 = var23 - avesig23;
  printf("sigma23 = %f, seeing23 = %f\n\n", sqrt(var23), seeing(var23, d, r_23));

  seeing_ave = (seeing(var01, d, r_01) +
		seeing(var02, d, r_02) +
		seeing(var03, d, r_03) +
		seeing(var12, d, r_12) +
		seeing(var13, d, r_13) +
		seeing(var23, d, r_23))/6.0;

  printf("Ave. seeing = %4.2f\"\n", seeing_ave);

  fprintf(out, "%f %f %f %f %f %f %f\n", 
	  seeing(var01, d, r_01),
	  seeing(var02, d, r_02),
	  seeing(var03, d, r_03),
	  seeing(var12, d, r_12),
	  seeing(var13, d, r_13),
	  seeing(var23, d, r_23),
	  seeing_ave);
	  
  init = fopen("/dev/shm/video/init_cen_all", "w");
  for (i=0; i<4; i++) {
    fprintf(init, "%f %f\n", box[i].cenx, box[i].ceny);
  }
  fclose(init);

  return (status);
}
