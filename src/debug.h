#ifndef DEBUG_H
#define DEBUG_H

#ifndef ZSTD_DEBUG
#define ZSTD_DEBUG 0
#endif

/*prints messages to stderr only if debug defined */
int printd(const char* fmt, int dv);
int printd2(const char* fmt, int dv, int dv2);

#endif