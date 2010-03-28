/*
 * Grab partial image from camera. Camera must be format 7
 *    (scalable image size) compatible.
 *
 * Written by Damien Douxchamps <ddouxchamps@users.sf.net>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <stdio.h>
#include <stdint.h>
#include <dc1394/dc1394.h>
#include <stdlib.h>
#include <time.h>
#include <inttypes.h>
#include <string.h>
#include <fitsio.h>
#include <xpa.h>

#include <sys/time.h>

int main(int argc, char *argv[])
{
    fitsfile *fptr;
    long fpixel=1, nelements, naxes[3];
    dc1394camera_t *camera;
    int grab_n_frames;
    struct timeval start_time, end_time;
    time_t start_sec, end_sec;
    suseconds_t start_usec, end_usec;
    float elapsed_time, fps;
    int i, status;
    unsigned int min_bytes, max_bytes, max_height, max_width;
    unsigned int actual_bytes;
    uint64_t total_bytes = 0;
    unsigned int width, height;
    dc1394video_frame_t *frame=NULL;
    dc1394_t * d;
    dc1394camera_list_t * list;
    dc1394error_t err;
    char *filename;

    grab_n_frames = atoi(argv[1]);
    filename = argv[2];

    width = 320;
    height = 240;
    naxes[0] = width;
    naxes[1] = height;
    naxes[2] = grab_n_frames;

    nelements = naxes[0]*naxes[1]*naxes[2];

    stderr = freopen("grab_cube.log", "w", stderr);

    d = dc1394_new ();
    if (!d)
        return 1;
    err=dc1394_camera_enumerate (d, &list);
    DC1394_ERR_RTN(err,"Failed to enumerate cameras");

    if (list->num == 0) {
        dc1394_log_error("No cameras found");
        return 1;
    }

    camera = dc1394_camera_new (d, list->ids[0].guid);
    if (!camera) {
        dc1394_log_error("Failed to initialize camera with guid %"PRIx64,
                list->ids[0].guid);
        return 1;
    }
    dc1394_camera_free_list (list);

    printf("Using camera with GUID %"PRIx64"\n", camera->guid);

    /*-----------------------------------------------------------------------
     *  setup capture for format 7
     *-----------------------------------------------------------------------*/
    // err=dc1394_video_set_operation_mode(camera, DC1394_OPERATION_MODE_1394B);
    // DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot operate at 1394B");
    
    // libdc1394 doesn't work well with firewire800 yet so set to legacy 400 mode
    dc1394_video_set_iso_speed(camera, DC1394_ISO_SPEED_400);

    // configure camera for format7
    err = dc1394_video_set_mode(camera, DC1394_VIDEO_MODE_FORMAT7_1);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot choose format7_0");
    printf ("I: video mode is format7_0\n");

    err = dc1394_format7_get_max_image_size (camera, DC1394_VIDEO_MODE_FORMAT7_1, 
					     &max_width, &max_height);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot get max image size for format7_0");
    printf ("I: max image size is: height = %d, width = %d\n", max_height, max_width);
    printf ("I: current image size is: height = %d, width = %d\n", height, width);

    err = dc1394_format7_set_roi (camera, 
				  DC1394_VIDEO_MODE_FORMAT7_1, 
				  DC1394_COLOR_CODING_MONO8, // not sure why RAW8/16 don't work
                                  DC1394_USE_MAX_AVAIL, 
				  0, 0, // left, top
				  width, height); // width, height
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set roi");
    printf ("I: roi is (0, 0) - (%d, %d)\n", width, height);

    err = dc1394_format7_get_total_bytes (camera, DC1394_VIDEO_MODE_FORMAT7_0, &total_bytes);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot get total bytes");
    printf ("I: total bytes is %"PRIu64" before SFF enabled\n", total_bytes);

    // err = dc1394_feature_set_value (camera, DC1394_FEATURE_GAIN, 24);
    //DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Error setting gain");

    err=dc1394_capture_setup(camera, 16, DC1394_CAPTURE_FLAGS_DEFAULT);
    DC1394_ERR_CLN_RTN(err, dc1394_camera_free(camera), "Error capturing");

    /*-----------------------------------------------------------------------
     *  print allowed and used packet size
     *-----------------------------------------------------------------------*/
    err=dc1394_format7_get_packet_parameters(camera, DC1394_VIDEO_MODE_FORMAT7_0, &min_bytes, &max_bytes);

    DC1394_ERR_RTN(err,"Packet para inq error");
    printf( "camera reports allowed packet size from %d - %d bytes\n", min_bytes, max_bytes);

    err=dc1394_format7_get_packet_size(camera, DC1394_VIDEO_MODE_FORMAT7_0, &actual_bytes);
    DC1394_ERR_RTN(err,"dc1394_format7_get_packet_size error");
    printf( "camera reports actual packet size = %d bytes\n", actual_bytes);

    err=dc1394_format7_get_total_bytes(camera, DC1394_VIDEO_MODE_FORMAT7_0, &total_bytes);
    DC1394_ERR_RTN(err,"dc1394_query_format7_total_bytes error");
    printf( "camera reports total bytes per frame = %"PRId64" bytes\n",
            total_bytes);

    /*-----------------------------------------------------------------------
     *  have the camera start sending us data
     *-----------------------------------------------------------------------*/
    err=dc1394_video_set_transmission(camera,DC1394_ON);
    if (err!=DC1394_SUCCESS) {
        dc1394_log_error("unable to start camera iso transmission");
        dc1394_capture_stop(camera);
        dc1394_camera_free(camera);
        exit(1);
    }

    // set up FITS image and capture
    fits_create_file(&fptr, filename, &status);
    dc1394_get_image_size_from_video_mode(camera, DC1394_VIDEO_MODE_FORMAT7_0, &width, &height);
    fits_create_img(fptr, BYTE_IMG, 3, naxes, &status);

    /*-----------------------------------------------------------------------
     *  capture frames and measure the time for this operation
     *-----------------------------------------------------------------------*/
    gettimeofday(&start_time, NULL);

    printf("Start capture:\n");

    for( i = 0; i < grab_n_frames; ++i) {
        /*-----------------------------------------------------------------------
         *  capture one frame
         *-----------------------------------------------------------------------*/
        err=dc1394_capture_dequeue(camera, DC1394_CAPTURE_POLICY_WAIT, &frame);
        if (err!=DC1394_SUCCESS) {
            dc1394_log_error("unable to capture");
            dc1394_capture_stop(camera);
            dc1394_camera_free(camera);
            exit(1);
        }

	// attempt to preallocate image array and write to memory before dumping to disk.
	// turns out to be slow due to large size of images. cfitsio buffering is far
	// more efficient.

	//memcpy(im_buffer+2*i*naxes[0]*naxes[1], 
	//frame->image-1, 
	//naxes[0]*naxes[1]*sizeof(short));

	// just writing each frame to the FITS file goes pretty fast
	fits_write_img(fptr, 
		       TBYTE, 
		       fpixel+i*naxes[0]*naxes[1], 
		       naxes[0]*naxes[1], 
		       frame->image-1, 
		       &status);

        // release buffer
        dc1394_capture_enqueue(camera,frame);
    }

    gettimeofday(&end_time, NULL);
    printf("End capture.\n");

    /*-----------------------------------------------------------------------
     *  stop data transmission
     *-----------------------------------------------------------------------*/
    start_sec = start_time.tv_sec;
    start_usec = start_time.tv_usec;
    end_sec = end_time.tv_sec;
    end_usec = end_time.tv_usec;

    elapsed_time = (float)((end_sec + 1.0e-6*end_usec) - (start_sec + 1.0e-6*start_usec));
    fps = grab_n_frames/elapsed_time;
    printf("Elapsed time = %g seconds.\n", elapsed_time);
    printf("Framerate = %g fps.\n", fps);

    err=dc1394_video_set_transmission(camera,DC1394_OFF);
    DC1394_ERR_RTN(err,"couldn't stop the camera?");

    /*-----------------------------------------------------------------------
     *  save FITS image to disk
     *-----------------------------------------------------------------------*/
    //fits_write_img(fptr, TBYTE, fpixel, naxes[0]*naxes[1]*naxes[2], im_buffer, &status);
    fits_close_file(fptr, &status);
    fits_report_error(stderr, status);
    //free(im_buffer);

    printf("wrote: %s\n", filename);
    printf("Image is %d bits/pixel.\n", frame->data_depth);

    /*-----------------------------------------------------------------------
     *  close camera, cleanup
     *-----------------------------------------------------------------------*/
    dc1394_capture_stop(camera);
    dc1394_video_set_transmission(camera, DC1394_OFF);
    dc1394_camera_free(camera);
    dc1394_free (d);
    return 0;
}
