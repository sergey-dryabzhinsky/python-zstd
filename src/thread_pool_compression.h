#ifndef THREAD_POOL_COMPRESSION_H
#define THREAD_POOL_COMPRESSION_H

#include <pthread.h>

#define THREAD_POOL_MAX_SIZE 256
#define THREAD_JOB_CHUNK_MIN_SIZE 1024

typedef struct {
    pthread_t tid;
    pthread_attr_t attr;
    char flag_exit;
    char exited;
    char started;
} tCThreadPool;

static tCThreadPool thread_pool[THREAD_POOL_MAX_SIZE];
static int thread_pool_size=0;

void *potok(void *param);

int init_thread_pool_compression(void);
int free_thread_pool_compression(void);

#endif // THREAD_POOL_COMPRESSION_H