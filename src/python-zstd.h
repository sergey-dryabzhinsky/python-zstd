/*
 * Copyright (c) 2015-2020 Sergey Dryabzhinsky
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of Steeve Morin nor the names of its contributors may be
 *    used to endorse or promote products derived from this software without
 *    specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef _PYTHON_ZSTD_H_
#define _PYTHON_ZSTD_H_


#include "Python.h"


/*-=====  Do you need legacy old-format functions?  =====-*/
#ifndef PYZSTD_LEGACY
#define PYZSTD_LEGACY 0
#endif


/*-=====  Do you build with external library?  =====-*/
#ifndef LIBZSTD_EXTERNAL
#define LIBZSTD_EXTERNAL 0
#endif


/*-=====  Pre-defined compression levels  =====-*/
#ifndef ZSTD_CLEVEL_DEFAULT
#define ZSTD_CLEVEL_DEFAULT 3
#endif

#ifndef ZSTD_MAX_CLEVEL
#define ZSTD_MAX_CLEVEL     22
#endif

#ifndef ZSTDMT_NBWORKERS_MAX
#define ZSTDMT_NBWORKERS_MAX ((sizeof(void*)==4) /*32-bit*/ ? 64 : 256)
#endif

/* --== Negative fast compression levels only since 1.3.4 ==-- */
#if ZSTD_VERSION_NUMBER >= 10304

#define ZSTD_MIN_CLEVEL     -100
#define ZSTD_134_DOCSTR "Also supports ultra-fast levels from -100 (fastest) to -1 (less fast) since module compiled with ZSTD 1.3.4+.\n"

#else

#define ZSTD_MIN_CLEVEL     0
#define ZSTD_134_DOCSTR ""

#endif

#define DISCARD_PARAMETER (void)

static PyObject *ZstdError;

static PyObject *py_zstd_compress_mt(PyObject* self, PyObject *args);
static PyObject *py_zstd_uncompress(PyObject* self, PyObject *args);
static PyObject *py_zstd_module_version(PyObject* self, PyObject *args);
static PyObject *py_zstd_library_version(PyObject* self, PyObject *args);
static PyObject *py_zstd_library_version_int(PyObject* self, PyObject *args);
static PyObject *py_zstd_library_external(PyObject* self, PyObject *args);

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initzstd(void);
#endif

#if PY_MAJOR_VERSION < 3
#define PY_BYTESTR_TYPE "string"
#else
#define PY_BYTESTR_TYPE "bytes"
#endif

#define COMPRESS_DOCSTRING      "compress_mt(string[, level, threads]): "PY_BYTESTR_TYPE" -- Returns compressed string.\n\n\
Optional arg level is the compression level, from 1 (fastest) to 22 (slowest). The default value is 3.\n\
Optional arg threads is the number of worker threads, from 0 to 200. 0 - auto-tune by cpu cores count. The default value is 0.\n\
"ZSTD_134_DOCSTR"\n\
Input data length limited by 2Gb by Python API.\n\
Raises a zstd.Error exception if any error occurs."

#define UNCOMPRESS_DOCSTRING    "decompress("PY_BYTESTR_TYPE"): string -- Returns uncompressed string.\n\nRaises a zstd.Error exception if any error occurs."

#define VERSION_DOCSTRING       "version(): string -- Returns this module version as string."
#define ZSTD_VERSION_DOCSTRING  "ZSTD_version(): string -- Returns ZSTD library version as string."
#define ZSTD_INT_VERSION_DOCSTRING  "ZSTD_version_number(): int -- Returns ZSTD library version as integer.\n Format of the number is: major * 100*100 + minor * 100 + release."
#define ZSTD_EXTERNAL_DOCSTRING  "ZSTD_external(): int -- Returns 0 or 1 if ZSTD library build as external."
#define ZSTD_THREADS_COUNT_DOCSTRING  "ZSTD_threads_count(): int -- Returns ZSTD determined CPU cores count in integer."
#define ZSTD_MAX_THREADS_COUNT_DOCSTRING  "ZSTD_max_threads_count(): int -- Returns ZSTD library determined maximum working threads count in integer."

#if PYZSTD_LEGACY > 0
#define COMPRESS_OLD_DOCSTRING      "compress_old(string[, level]): "PY_BYTESTR_TYPE" -- Compress string, old version, returning the compressed data.\n\nUses custom format. Not compatible with streaming or origin compression tools.\n\nRaises a zstd.Error exception if any error occurs.\n\n@deprecated"
#define UNCOMPRESS_OLD_DOCSTRING    "decompress_old("PY_BYTESTR_TYPE"): string -- Decompress string, old version, returning the uncompressed data.\n\nUses custom format from `compress_old` fucntion.\nNot compatible with streaming or origin compression tools.\n\nRaises a zstd.Error exception if any error occurs.\n\n@deprecated"
#endif

/**************************************
*  Basic Types
**************************************/
#if defined (__STDC_VERSION__) && __STDC_VERSION__ >= 199901L   /* C99 */
# include <stdint.h>
typedef uint8_t  BYTE;
typedef uint16_t U16;
typedef uint32_t U32;
typedef  int32_t S32;
typedef  int64_t S64;
typedef uint64_t U64;
#else
typedef unsigned char       BYTE;
typedef unsigned short      U16;
typedef unsigned int        U32;
typedef   signed int        S32;
typedef   signed long long  S64;
typedef unsigned long long  U64;
#endif

#if defined(_WIN32) && defined(_MSC_VER)
# define inline __inline
# if _MSC_VER >= 1600
#  include <stdint.h>
# else /* _MSC_VER >= 1600 */
   typedef signed char        int8_t;
   typedef signed short       int16_t;
   typedef signed int         int32_t;
   typedef signed long long   int64_t;
   typedef unsigned char      uint8_t;
   typedef unsigned short     uint16_t;
   typedef unsigned int       uint32_t;
   typedef unsigned long long uint64_t;
# endif /* _MSC_VER >= 1600 */
#endif

#if defined(__SUNPRO_C) || defined(__hpux) || defined(_AIX)
#define inline
#endif

#ifdef __linux
#define inline __inline
#endif

#endif // _PYTHON_ZSTD_H_
