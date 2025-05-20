#include <stdbool.h>
#include <stdio.h>
#include <zstd.h>
#include <Python.h>
//#define _GNU_SOURCE 1
#include "thread_pool_compression.h"
#include "util.h"
#include "sleep.h"
#include "debug.h"

#define NAMELEN 16

/* sample thread function */
void *thread_compression_worker(void *param)
{
    int idx = *(int*)param;
    ZSTD_CCtx* cctx = 0;
    printdn("Started thread #%d\n", idx);
    thread_pool[idx].exited=0;
    thread_pool[idx].started=1;
    thread_pool[idx].task_wait_data=1;
    thread_pool[idx].task_working=0;
	while (true) {
	    if (thread_pool[idx].flag_exit==1){
		printdn("Thread #%d asked to exit\n",idx);
		break;
	    }
	    msleep(1);// relax cpu load

	    if (thread_pool[idx].task_wait_data==1){
		continue;
	    }
	    if (thread_pool[idx].task_set==0){
		continue;
	    }

	    thread_pool[idx].task_set=0; // drop flag
	    thread_pool[idx].task_wait_data=0; // drop flag
	    thread_pool[idx].task_working=1; // set flag
	    /* make compression magic */
	    Py_BEGIN_ALLOW_THREADS
	    cctx = ZSTD_createCCtx();
	    ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, thread_pool[idx].level);
	    ZSTD_CCtx_setParameter(cctx, ZSTD_c_nbWorkers, thread_pool[idx].threads);
	    size_t cSize = ZSTD_compress2(cctx, thread_pool[idx].dst, (size_t)thread_pool[idx].dest_size, thread_pool[idx].src, (size_t)thread_pool[idx].chunk_size);
	    thread_pool[idx].cSize=cSize;
	    thread_pool[idx].task_done=1;
	    thread_pool[idx].task_working=0; // drop flag
	    thread_pool[idx].task_wait_data=1; // set flag again
	    ZSTD_freeCCtx(cctx);
	    Py_END_ALLOW_THREADS
	}
    thread_pool[idx].exited=1;
    printdn("Stopped thread #%d\n",idx);
    pthread_exit(0);
}

/* init threads pool and start threads, one time */
int init_thread_pool_compression(void)
{
    pool_status.started=0;
    pool_status.stopped=0;
    if (pool_status.started) return pool_status.started;

    int threads = UTIL_countAvailableCores();
    printdn("Init threads pool and start %d threads\n", threads);
    thread_pool_size=threads;
    for(int i=0;i<threads;i++){
        /*  get default values for attributes*/
	pthread_attr_init(&thread_pool[i].attr);

	thread_pool[i].flag_exit=0;
	thread_pool[i].started=0;
	thread_pool[i].exited=0;

	char thname[NAMELEN];
	sprintf(thname,"Worker #%d",i);
	/* create new thread*/
	int res=pthread_create(&thread_pool[i].tid,&thread_pool[i].attr,thread_compression_worker,&i);
	msleep(5);
	if (res==0 && thread_pool[i].started){
		pool_status.started++;
//		pthread_setname_np(thread_pool[i].tid,thname);
	}
	else printd2n("Thread #%d failed to start with error: %d\n",i,res);
    }
    return pool_status.started;
}

/* clean threads pool and stops threads, one time */
int free_thread_pool_compression(void)
{
    pool_status.stopped=0;
    if (pool_status.stopped) return pool_status.stopped;

    printdn("Free threads pool and stop %d threads\n", thread_pool_size);

    for(int i=0;i<thread_pool_size;i++){
	thread_pool[i].flag_exit=1;
    }
    msleep(10);
    /* force threads to exit */
    for(int i=0;i<thread_pool_size;i++){
	if (thread_pool[i].exited) {
		pool_status.stopped++;
		continue;
	}
	int res=pthread_cancel(thread_pool[i].tid);
	if (res) printd2n("Thread #%d failed to exit with error: %d\n",i,res);
	else pool_status.stopped++;
    }

    return pool_status.stopped;
}
