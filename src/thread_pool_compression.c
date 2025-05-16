#include <stdbool.h>
#include "thread_pool_compression.h"
#include "util.h"
#include "sleep.h"
#include "debug.h"

/* sample thread function */
void *potok(void *param)
{
    int idx = *(int*)param;
    printdi("Started thread #%d\n", idx);
    thread_pool[idx].exited=0;
    thread_pool[idx].started=1;
	while (true) {
	    if (thread_pool[idx].flag_exit==1){
		printdi("Thread #%d asked to exit\n",idx);
		break;
	    }
	    msleep(10);
	}
    thread_pool[idx].exited=1;
    printdi("Stopped thread #%d\n",idx);
    pthread_exit(0);
}

/* init threads pool and start threads, one time */
int init_thread_pool_compression(void)
{
    static char inited=0;
    if (inited) return inited;

    int threads = UTIL_countAvailableCores();
    printdi("Init threads pool and start %d threads\n", threads);
    thread_pool_size=threads;
    for(int i=0;i<threads;i++){
        /*  get default values for attributes*/
	pthread_attr_init(&thread_pool[i].attr);

	thread_pool[i].flag_exit=0;
	thread_pool[i].started=0;
	thread_pool[i].exited=0;
	/* create new thread*/
	int res=pthread_create(&thread_pool[i].tid,&thread_pool[i].attr,potok,&i);
	msleep(50);
	if (res==0 && thread_pool[i].started) inited++;
    }
    return inited;
}

/* clean threads pool and stops threads, one time */
int free_thread_pool_compression(void)
{
    static char freed=0;
    if (freed) return freed;

    printdi("Free threads pool and stop %d threads\n", thread_pool_size);

    for(int i=0;i<thread_pool_size;i++){
	thread_pool[i].flag_exit=1;
    }
    msleep(100);
    /* force threads to exit */
    for(int i=0;i<thread_pool_size;i++){
	if (thread_pool[i].exited) {
		freed++;
		continue;
	}
	int res=pthread_cancel(thread_pool[i].tid);
	if (res) printd2("Thread #%d failed to exit with error: %d",i,res);
    }

    return freed;
}