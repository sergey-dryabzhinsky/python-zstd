#ifndef DEBUG_H
#define DEBUG_H

#ifndef ZSTD_DEBUG
#define ZSTD_DEBUG 0
#endif

#ifndef ZSTD_DEBUG_NOTICE
#define ZSTD_DEBUG_NOTICE 0
#endif

#ifndef ZSTD_DEBUG_INFO
#define ZSTD_DEBUG_INFO 0
#endif

#ifndef ZSTD_DEBUG_ERROR
#define ZSTD_DEBUG_ERROR 0
#endif

#define DEBUG_FMT_MAX_LEN 64

/*prints messages to stderr only if debug defined */
int printd(const char* fmt, int dv);
int printdn(const char* fmt, int dv);
int printdi(const char* fmt, int dv);
int printde(const char* fmt, int dv);
int printdes(const char* fmt, const char* dv);
int printd2(const char* fmt, int dv, int dv2);
int printd2n(const char* fmt, int dv, int dv2);
int printd2i(const char* fmt, int dv, int dv2);
int printd2e(const char* fmt, int dv, int dv2);

#endif