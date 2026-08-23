#ifndef CCTX_POOL_H
#define CCTX_POOL_H

#include "zstd.h"

/*
 * Pool of reusable ZSTD_CCtx objects, used by py_zstd_compress_mt2 to
 * avoid re-allocating a fresh context on every call while remaining
 * thread-safe. Each acquired context is owned by exactly one caller
 * until it is released back into the pool.
 *
 * The pool grows on demand but its size is bounded by the peak number of
 * threads that have ever been concurrently inside py_zstd_compress_mt2,
 * one context per in-flight call and no more.
 * The pool never shrinks; it is only freed at module teardown.
 */

/* Initialize the pool. Safe to call more than once. */
void init_cctx_pool(void);

/* Free every context still held by the pool and release the lock. */
void free_cctx_pool(void);

/*
 * Return a context ready for use. If the pool is empty, a new context
 * is created. Returns NULL if allocation fails.
 */
ZSTD_CCtx* cctx_pool_acquire(void);

/*
 * Return a context to the pool for later reuse. If the pool cannot
 * grow to hold it, the context is freed instead.
 */
void cctx_pool_release(ZSTD_CCtx* cctx);

#endif /* CCTX_POOL_H */
