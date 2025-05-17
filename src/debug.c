#include "debug.h"
#include <stdio.h>

int printd(const char* fmt, int dv)
{
	if (!ZSTD_DEBUG) return 0;
	int done=0;
	char buffer[256];
	sprintf(buffer,"DEBUG: %s",fmt);
	done = fprintf(stderr, buffer, dv);
	return done;
}

int printdn(const char* fmt, int dv)
{
	if (!ZSTD_DEBUG_NOTICE) return 0;
	int done=0;
	char buffer[256];
	sprintf(buffer,"DEBUG notice: %s",fmt);
	done = fprintf(stderr, buffer, dv);
	return done;
}

int printdi(const char* fmt, int dv)
{
	if (!ZSTD_DEBUG_INFO) return 0;
	int done=0;
	char buffer[256];
	sprintf(buffer,"DEBUG info: %s",fmt);
	done = fprintf(stderr, buffer, dv);
	return done;
}

int printd2(const char* fmt, int dv, int dv2)
{
	if (!ZSTD_DEBUG) return 0;
	int done=0;
	char buffer[256];
	sprintf(buffer,"DEBUG: %s",fmt);
	done = fprintf(stderr,buffer, dv, dv2);
	return done;
}
int printd2n(const char* fmt, int dv, int dv2)
{
	if (!ZSTD_DEBUG) return 0;
	int done=0;
	char buffer[256];
	sprintf(buffer,"DEBUG notice: %s",fmt);
	done = fprintf(stderr,buffer, dv, dv2);
	return done;
}
