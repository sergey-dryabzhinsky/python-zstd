#ifndef THREAD_POOL_COMPRESSION_H
#define THREAD_POOL_COMPRESSION_H

#include <pthread.h>
#include <stdint.h>

#define THREAD_POOL_MAX_SIZE 256
#define THREAD_JOB_CHUNK_MIN_SIZE 1024

typedef struct {
    pthread_t tid;
    pthread_attr_t attr;
    char flag_exit;
    char exited;
    char started;

    char task_wait_data;
    char task_set;
    char task_working;
    char task_done;
    /* task data */
    char* src;
    uint64_t src_pos;
    size_t chunk_size;
    int level;
    int threads;
    char* dst;
    size_t dest_size;
    int64_t cSize;
} tCThreadPool;

typedef struct {
    char started;
    char stopped;
} tCPoolStatus;

static tCThreadPool thread_pool[THREAD_POOL_MAX_SIZE];
static tCPoolStatus pool_status;
static int thread_pool_size=0;

void *thread_compression_worker(void *param);

int init_thread_pool_compression(void);
int free_thread_pool_compression(void);

#endif // THREAD_POOL_COMPRESSION_H