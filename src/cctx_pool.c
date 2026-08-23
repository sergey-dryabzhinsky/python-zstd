#include <stdlib.h>
#include <stddef.h>

#include <Python.h>
#include "pythread.h"

#include "zstd.h"
#include "cctx_pool.h"

static PyThread_type_lock cctx_pool_lock = NULL;
static ZSTD_CCtx** cctx_pool = NULL;
static size_t cctx_pool_count = 0;
static size_t cctx_pool_capacity = 0;

void init_cctx_pool(void)
{
    if (cctx_pool_lock == NULL) {
        cctx_pool_lock = PyThread_allocate_lock();
    }
}

void free_cctx_pool(void)
{
    if (cctx_pool_lock != NULL) {
        PyThread_acquire_lock(cctx_pool_lock, WAIT_LOCK);
    }
    for (size_t i = 0; i < cctx_pool_count; i++) {
        ZSTD_freeCCtx(cctx_pool[i]);
    }
    free(cctx_pool);
    cctx_pool = NULL;
    cctx_pool_count = 0;
    cctx_pool_capacity = 0;
    if (cctx_pool_lock != NULL) {
        PyThread_release_lock(cctx_pool_lock);
        PyThread_free_lock(cctx_pool_lock);
        cctx_pool_lock = NULL;
    }
}

ZSTD_CCtx* cctx_pool_acquire(void)
{
    ZSTD_CCtx* cctx = NULL;

    if (cctx_pool_lock != NULL) {
        PyThread_acquire_lock(cctx_pool_lock, WAIT_LOCK);
        if (cctx_pool_count > 0) {
            cctx = cctx_pool[--cctx_pool_count];
        }
        PyThread_release_lock(cctx_pool_lock);
    }

    if (cctx == NULL) {
        cctx = ZSTD_createCCtx();
    }
    return cctx;
}

void cctx_pool_release(ZSTD_CCtx* cctx)
{
    if (cctx == NULL) {
        return;
    }

    if (cctx_pool_lock == NULL) {
        ZSTD_freeCCtx(cctx);
        return;
    }

    PyThread_acquire_lock(cctx_pool_lock, WAIT_LOCK);
    if (cctx_pool_count == cctx_pool_capacity) {
        /* Grow the pool by doubling capacity whenever a  released context does not fit.
         * The maximum size of the pool is bounded by the peak number of threads.  */
        size_t new_capacity = cctx_pool_capacity ? cctx_pool_capacity * 2 : 8;
        ZSTD_CCtx** new_pool = (ZSTD_CCtx**)realloc(cctx_pool, new_capacity * sizeof(ZSTD_CCtx*));
        if (new_pool == NULL) {
            PyThread_release_lock(cctx_pool_lock);
            ZSTD_freeCCtx(cctx);
            return;
        }
        cctx_pool = new_pool;
        cctx_pool_capacity = new_capacity;
    }
    cctx_pool[cctx_pool_count++] = cctx;
    PyThread_release_lock(cctx_pool_lock);
}
