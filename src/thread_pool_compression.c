#include <stdbool.h>
#include <stdio.h>
#define _GNU_SOURCE
#include "thread_pool_compression.h"
#include "util.h"
#include "sleep.h"
#include "debug.h"

#define NAMELEN 16

/* sample thread function */
void *thread_compression_worker(void *param)
{
    int idx = *(int*)param;
    printdn("Started thread #%d\n", idx);
    thread_pool[idx].exited=0;
    thread_pool[idx].started=1;
	while (true) {
	    if (thread_pool[idx].flag_exit==1){
		printdn("Thread #%d asked to exit\n",idx);
		break;
	    }
	    msleep(10);
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
	msleep(50);
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
    msleep(100);
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