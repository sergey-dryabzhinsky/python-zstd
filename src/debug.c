#include "debug.h"
#include <stdio.h>

int printd(const char* fmt, int dv)
{
	int done=0;
	if (ZSTD_DEBUG) done = fprintf(stderr, fmt, dv);
	return done;
}

int printd2(const char* fmt, int dv, int dv2)
{
	int done=0;
	if (ZSTD_DEBUG) done = fprintf(stderr, fmt, dv, dv2);
	return done;
}
