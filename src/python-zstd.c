/*
 * ZSTD Library Python bindings
 * Copyright (c) 2015-2020, Sergey Dryabzhinsky
 * All rights reserved.
 *
 * BSD License
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright notice, this
 *   list of conditions and the following disclaimer in the documentation and/or
 *   other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdlib.h>
#include <stddef.h>

/* Since 3.8 it is mandatory to use proper type for # formats */
#define PY_SSIZE_T_CLEAN

/* Simplify passing strings to the various compilers*/
#define str(x) #x
#define xstr(x) str(x)

#include <Python.h>
#include "pythoncapi_compat.h"    // Py_SET_SIZE() for Python 3.8 and older

#include "bytesobject.h"
#include "zstd.h"
#include "util.h"
#include "python-zstd.h"

/**
 * New function for multi-threaded compression.
 * Uses origin zstd header, nothing more.
 * Simple version: not for streaming, no dict support, full block compression.
 * Uses new API with context object.
 */
static PyObject *py_zstd_compress_mt(PyObject* self, PyObject *args)
{

    PyObject *result;
    const char *source;
    Py_ssize_t source_size;
    char *dest;
    Py_ssize_t dest_size;
    size_t cSize;
    int32_t level = ZSTD_CLEVEL_DEFAULT;
    int32_t threads = 0;
    ZSTD_CCtx* cctx = 0;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#|ii", &source, &source_size, &level, &threads))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#|ii", &source, &source_size, &level, &threads))
        return NULL;
#endif

    if (0 == level) level=ZSTD_CLEVEL_DEFAULT;
    /* Fast levels (zstd >= 1.3.4) - [-1..-100] */
    /* Usual levels                - [ 1..22] */
    /* If level less than -100 or 1 - raise Error, level 0 handled before. */
    if (level < ZSTD_MIN_CLEVEL) {
        PyErr_Format(ZstdError, "Bad compression level - less than %d: %d", ZSTD_MIN_CLEVEL, level);
        return NULL;
    }
    /* If level more than 22 - raise Error. */
    if (level > ZSTD_MAX_CLEVEL) {
        PyErr_Format(ZstdError, "Bad compression level - more than %d: %d", ZSTD_MAX_CLEVEL, level);
        return NULL;
    }

    if (threads < 0) {
        PyErr_Format(ZstdError, "Bad threads count - less than %d: %d", 0, threads);
        return NULL;
    }
    if (0 == threads) threads = UTIL_countPhysicalCores();
    /* If threads more than 200 - raise Error. */
    if (threads > ZSTDMT_NBWORKERS_MAX) {
        threads = ZSTDMT_NBWORKERS_MAX;
        // do not fail here, due auto thread counter
        //PyErr_Format(ZstdError, "Bad threads count - more than %d: %d", ZSTDMT_NBWORKERS_MAX, threads);
        //return NULL;
    }

    dest_size = (Py_ssize_t)ZSTD_compressBound(source_size);
    result = PyBytes_FromStringAndSize(NULL, dest_size);
    if (result == NULL) {
        return NULL;
    }

    if (source_size >= 0) {
        dest = PyBytes_AS_STRING(result);

        cctx = ZSTD_createCCtx();

        ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, level);
        ZSTD_CCtx_setParameter(cctx, ZSTD_c_nbWorkers, threads);

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_compress2(cctx, dest, (size_t)dest_size, source, (size_t)source_size);
        Py_END_ALLOW_THREADS

        ZSTD_freeCCtx(cctx);

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Compression error: %s", ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
            return NULL;
        }
        Py_SET_SIZE(result, cSize);
    }
    return result;
}

/**
 * New more interoperable function
 * Uses origin zstd header, nothing more
 * Simple version: not for streaming, no dict support, full block decompression
 */
static PyObject *py_zstd_uncompress(PyObject* self, PyObject *args)
{

    PyObject    *result;
    const char  *source, *src;
    Py_ssize_t  source_size, ss, seek_frame;
    uint64_t    dest_size, frame_size;
    char        error = 0;
    size_t      cSize;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#", &source, &source_size))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#", &source, &source_size))
        return NULL;
#endif

    dest_size = (uint64_t) ZSTD_getFrameContentSize(source, source_size);
    if (dest_size == ZSTD_CONTENTSIZE_UNKNOWN || dest_size == ZSTD_CONTENTSIZE_ERROR) {
        PyErr_Format(ZstdError, "Input data invalid or missing content size in frame header.");
        return NULL;
    }

	// Find real dest_size across multiple frames
	ss = source_size;
	seek_frame = ss - 1;
	src = source;
	while (seek_frame < ss) {
		seek_frame = ZSTD_findFrameCompressedSize(src, ss);
		if (ZSTD_isError(seek_frame)) break;
		src += seek_frame;
		ss -= seek_frame;
		if (ss <=0) break;
		frame_size = (uint64_t) ZSTD_getFrameContentSize(src, ss);
		if (ZSTD_isError(frame_size)) break;
		dest_size += frame_size;
	}

    result = PyBytes_FromStringAndSize(NULL, dest_size);

    if (result != NULL) {
        char *dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS
		// get real dest_size
        cSize = ZSTD_decompress(dest, dest_size, source, source_size);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
			const char *errStr = ZSTD_getErrorName(cSize);
/*			if (strstr(errStr, "buffer is too small") != NULL) {
				// reroll decompression with bigger buffer
				error = 2;
			} else {*/
            	PyErr_Format(ZstdError, "Decompression error: %s", errStr);
            	error = 1;
//			}
        } else if (cSize != dest_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch -> decomp %lu != %lu [header]", (uint64_t)cSize, dest_size);
            error = 1;
        }
    }

    if (error) {
        Py_CLEAR(result);
        result = NULL;
    }

	if (!error) {
    	Py_SET_SIZE(result, cSize);
	}

    return result;
}

/**
 * Returns this module version as string
 */
static PyObject *py_zstd_module_version(PyObject* self, PyObject *args)
{
#if PY_MAJOR_VERSION >= 3
    return PyUnicode_FromFormat("%s", xstr(VERSION));
#else
    return PyString_FromFormat("%s", xstr(VERSION));
#endif
}

/**
 * Returns ZSTD library version as string
 */
static PyObject *py_zstd_library_version(PyObject* self, PyObject *args)
{
#if PY_MAJOR_VERSION >= 3
    return PyUnicode_FromFormat("%s", ZSTD_versionString());
#else
    return PyString_FromFormat("%s", ZSTD_versionString());
#endif
}

/**
 * Returns ZSTD library version as int (major * 100*100 + minor * 100 + release)
 */
static PyObject *py_zstd_library_version_int(PyObject* self, PyObject *args)
{
    return Py_BuildValue("i", ZSTD_VERSION_NUMBER);
}

/**
 * Returns 0 or 1 if ZSTD library build as external
 */
static PyObject *py_zstd_library_external(PyObject* self, PyObject *args)
{
    return Py_BuildValue("i", LIBZSTD_EXTERNAL);
}


/**
 * Returns ZSTD determined threads count, int
 */
static PyObject *py_zstd_threads_count(PyObject* self, PyObject *args)
{
    int32_t threads = UTIL_countPhysicalCores();

    return Py_BuildValue("i", threads);
}

/**
 * Returns ZSTD determined max threads count, int
 */
static PyObject *py_zstd_max_threads_count(PyObject* self, PyObject *args)
{
    return Py_BuildValue("i", ZSTDMT_NBWORKERS_MAX);
}


static PyMethodDef ZstdMethods[] = {
    {"ZSTD_compress",  py_zstd_compress_mt, METH_VARARGS, COMPRESS_DOCSTRING},
    {"ZSTD_uncompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"compress",  py_zstd_compress_mt, METH_VARARGS, COMPRESS_DOCSTRING},
    {"uncompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"decompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"dumps",  py_zstd_compress_mt, METH_VARARGS, COMPRESS_DOCSTRING},
    {"loads",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"version",  py_zstd_module_version, METH_NOARGS, VERSION_DOCSTRING},
    {"ZSTD_version",  py_zstd_library_version, METH_NOARGS, ZSTD_VERSION_DOCSTRING},
    {"ZSTD_version_number",  py_zstd_library_version_int, METH_NOARGS, ZSTD_INT_VERSION_DOCSTRING},
    {"ZSTD_threads_count",  py_zstd_threads_count, METH_NOARGS, ZSTD_THREADS_COUNT_DOCSTRING},
    {"ZSTD_max_threads_count",  py_zstd_max_threads_count, METH_NOARGS, ZSTD_MAX_THREADS_COUNT_DOCSTRING},
    {"ZSTD_external",  py_zstd_library_external, METH_NOARGS, ZSTD_EXTERNAL_DOCSTRING},
    {NULL, NULL, 0, NULL}
};


struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
/* not needed */
#endif

#if PY_MAJOR_VERSION >= 3

static int myextension_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int myextension_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "zstd",
        NULL,
        sizeof(struct module_state),
        ZstdMethods,
        NULL,
        myextension_traverse,
        myextension_clear,
        NULL
};

#define INITERROR return NULL
PyObject *PyInit_zstd(void)

#else
#define INITERROR return
void initzstd(void)

#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("zstd", ZstdMethods);
#endif
    if (module == NULL) {
        INITERROR;
    }

    ZstdError = PyErr_NewException("zstd.Error", NULL, NULL);
    if (ZstdError == NULL) {
        Py_DECREF(module);
        INITERROR;
    }
    Py_INCREF(ZstdError);
    PyModule_AddObject(module, "Error", ZstdError);

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
