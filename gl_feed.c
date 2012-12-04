#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <dc1394/dc1394.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>
#include <string.h>
#include <inttypes.h>
#include <X11/X.h>
#include <X11/Xlib.h>
#include <GL/gl.h>
#include <GL/glx.h>
#include <GL/glu.h>

#define REG_CAMERA_ABS_MIN                  0x000U
#define REG_CAMERA_ABS_MAX                  0x004U
#define REG_CAMERA_ABS_VALUE                0x008U

Display                 *dpy;
Window                  root;
GLint                   att[] = { GLX_RGBA, GLX_DEPTH_SIZE, 24, GLX_DOUBLEBUFFER, None };
XVisualInfo             *vi;
Colormap                cmap;
XSetWindowAttributes    swa;
Window                  win;
GLXContext              glc;
XWindowAttributes       gwa;
XEvent                  xev;

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

void DrawImage(unsigned char *buf) {

    GLuint textureid;
    glGenTextures(1, &textureid);
    glBindTexture(GL_TEXTURE_2D, textureid);
    
    glClearColor(1.0, 1.0, 1.0, 1.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0., 640., 480., 0., 0., 20.);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    gluLookAt(0., 0., 10., 0., 0., 0., 0., 1., 0.);

    glBegin(GL_LINE_LOOP);
    glColor3f(0., 1., 0.0);
    glVertex3f(260., 220., 1.);
    glVertex3f(380., 220., 1.);
    glVertex3f(380., 260., 1.);
    glVertex3f(260., 260., 1.);
    glEnd();

    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, 320, 240, 0, GL_RED, GL_UNSIGNED_BYTE, buf);
    //gluBuilt2DMipmaps(GL_TEXTURE_2D, 4, 320, 240, GL_RGBA, GL_UNSIGNED_BYTE, buf);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP);
    glEnable(GL_TEXTURE_2D);
    
    glBegin(GL_QUADS);
    glColor4f(1., 1., 1., 3.0); 
    glTexCoord3f(0., 0., 0.); glVertex3f(0., 0., 0.);
    glTexCoord3f(1., 0., 0.); glVertex3f(640., 0., 0.);
    glTexCoord3f(1., 1., 0.); glVertex3f(640, 480., 0.);
    glTexCoord3f(0., 1., 0.); glVertex3f(0., 480., 0.);
    glEnd(); 

}

int main(int argc, char *argv[]) {
    unsigned char *buffer;
    int i, npixels;

    dc1394_t * dc;
    dc1394camera_t * camera;
    dc1394camera_list_t * list;
    dc1394featureset_t features;
    dc1394error_t err;
    dc1394video_mode_t mode;
    unsigned int min_bytes, max_bytes, max_height, max_width, winleft, wintop;
    uint64_t total_bytes = 0;
    
    struct timeval start_time, end_time;
    struct tm ut;
    time_t start_sec, end_sec;
    suseconds_t start_usec, end_usec;
    float elapsed_time, fps;

    int gain, brightness, rate, xsize, ysize, nimages;
    double exptime;
    
    srand48((unsigned)time(NULL));
    
    gain = 500;
    exptime = 3.0e-3;
    rate = 330;
    brightness = 300;

    xsize = 320;
    ysize = 240;
    npixels = xsize * ysize;
    
    stderr = freopen("video.log", "w", stderr);
    
    if (!(buffer = malloc(npixels*sizeof(char)))) {
      printf("Couldn't Allocate Image Buffer\n");
      exit(-1);
    }

    /* set up camera for observation */
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

    // set the frame rate to absolute value in frames/sec and get value from commandline
    err = dc1394_feature_set_mode(camera, DC1394_FEATURE_FRAME_RATE, DC1394_FEATURE_MODE_MANUAL);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set framerate to manual");
    err = dc1394_feature_set_absolute_control(camera, DC1394_FEATURE_FRAME_RATE, DC1394_TRUE);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set framerate to absolute mode");
    err = dc1394_feature_set_absolute_value(camera, DC1394_FEATURE_FRAME_RATE, 1.0*rate);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set framerate");
    printf("I: framerate is %d fps\n", rate);

    // set the shutter speed to absolute value in seconds (input ms on commandline)
    err = dc1394_feature_set_mode(camera, DC1394_FEATURE_SHUTTER, DC1394_FEATURE_MODE_MANUAL);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set shutter to manual");
    err = dc1394_feature_set_absolute_control(camera, DC1394_FEATURE_SHUTTER, DC1394_TRUE);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set shutter to absolute mode");
    err = dc1394_feature_set_absolute_value(camera, DC1394_FEATURE_SHUTTER, exptime);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set exptime");
    printf("I: exptime is %f ms\n", exptime);

    // set gain manually.  use relative value here in range 48 to 730. 
    err = dc1394_feature_set_mode(camera, DC1394_FEATURE_GAIN, DC1394_FEATURE_MODE_MANUAL);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set gain to manual");
    err = dc1394_feature_set_value(camera, DC1394_FEATURE_GAIN, gain);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set gain");
    printf ("I: gain is %d\n", gain);

    // set brightness manually.  use relative value in range 0 to 1023.
    err = dc1394_feature_set_mode(camera, DC1394_FEATURE_BRIGHTNESS, DC1394_FEATURE_MODE_MANUAL);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set brightness to manual");
    err = dc1394_feature_set_value(camera, DC1394_FEATURE_BRIGHTNESS, brightness);
    DC1394_ERR_CLN_RTN(err,dc1394_camera_free (camera),"cannot set brightness");
    printf ("I: brightness is %d\n", brightness);

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
    
    /* set up opengl window */
    dpy = XOpenDisplay(NULL);
    if(dpy == NULL) {
        printf("\n\tcannot connect to X server\n\n");
        exit(0); 
    }
    root = DefaultRootWindow(dpy);
    vi = glXChooseVisual(dpy, 0, att);
    if (vi == NULL) {
        printf("\n\tno appropriate visual found\n\n");
        exit(0);
    }
    cmap = XCreateColormap(dpy, root, vi->visual, AllocNone);
    swa.colormap = cmap;
    swa.event_mask = ExposureMask | KeyPressMask;
    win = XCreateWindow(dpy, root, 0, 0, 640, 480, 0, vi->depth, InputOutput, \
                        vi->visual, CWColormap | CWEventMask, &swa);
    XMapWindow(dpy, win);
    XStoreName(dpy, win, "IEEE1394 Real-time Display");
    glc = glXCreateContext(dpy, vi, NULL, GL_TRUE);
    glXMakeCurrent(dpy, win, glc);
    glEnable(GL_DEPTH_TEST); 

    XNextEvent(dpy, &xev);
    if(xev.type == Expose) {
        nimages = 0;
        printf("\nPress any key to exit.\n\n");
        gettimeofday(&start_time, NULL);
        while (1) {
            while (XPending(dpy) > 0) {
                XNextEvent(dpy, &xev);
                if(xev.type == KeyPress) {
                    gettimeofday(&end_time, NULL);
                    glXMakeCurrent(dpy, None, NULL);
                    glXDestroyContext(dpy, glc);
                    XDestroyWindow(dpy, win);
                    XCloseDisplay(dpy);

                    printf("End capture.\n");

                    start_sec = start_time.tv_sec;
                    start_usec = start_time.tv_usec;
                    end_sec = end_time.tv_sec;
                    end_usec = end_time.tv_usec;

                    elapsed_time = (float)((end_sec + 1.0e-6*end_usec) - (start_sec + 1.0e-6*start_usec));
                    fps = nimages/elapsed_time;
                    printf("Elapsed time = %g seconds.\n", elapsed_time);
                    printf("Framerate = %g fps.\n", fps);
 
                    /*------------------------------------------------------------
                     *  stop data transmission
                     *------------------------------------------------------------*/
                    err = dc1394_video_set_transmission(camera,DC1394_OFF);
                    DC1394_ERR_RTN(err,"couldn't stop the camera?");
                    exit(0);
                }
            }

            grab_frame(camera, buffer, npixels*sizeof(char));
            XGetWindowAttributes(dpy, win, &gwa);
            glViewport(0, 0, gwa.width, gwa.height);
            DrawImage(buffer);
            glXSwapBuffers(dpy, win);
            nimages++;
        }
    }
} /* this is the } which closes int main(int argc, char *argv[]) { */
