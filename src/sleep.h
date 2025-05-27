#ifndef SLEEP_H
#define SLEEP_H

// source: https://stackoverflow.com/a/1157217/29314471
/* msleep(): Sleep for the requested number of milliseconds. */
int msleep(long msec);
int nanosleep(const struct timespec*, struct timespec*);
#endif