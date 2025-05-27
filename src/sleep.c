#include <time.h>
#include <errno.h>

#include "sleep.h"
#ifndef CLOCK_MONOTONIC
#define CLOCK_MONOTONIC 0
#endif

#ifdef _MSC_VER
#include <windows.h>
// msvc lack nanosleep
  int nanosleep(const struct timespec *ts,
                       struct timespec *rem)
  {
    SleepEx (1000*ts->tv_sec + ts->tv_nsec/1000000, TRUE);
    (void) rem;
  }
#endif // only for windows

/* msleep(): Sleep for the requested number of milliseconds. */
int msleep(long msec)
{
    struct timespec ts;
    int res;

    if (msec < 0)
    {
        errno = EINVAL;
        return -1;
    }

    ts.tv_sec = msec / 1000;
    ts.tv_nsec = (msec % 1000) * 1000000;

    do {
        res = nanosleep(&ts, &ts);
    } while (res && errno == EINTR);

    return res;
}
