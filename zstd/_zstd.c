/*
 * ZSTD Library Python bindings
 * Copyright (c) 2015-2018, Sergey Dryabzhinsky
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

#include <Python.h>
#include "zstd.h"

#if ZSTD_VERSION_NUMBER < (1*100*100 +0*100 +0)
# error "python-zstd must be built using libzstd >= 1.0.0"
#endif

/*
 * Portability headaches.
 */

/* Python 2.x pyport.h will pull in stdint.h if it exists, but
   3.x pyport.h won't.  */

#if ((defined __STDC_VERSION__ && __STDC_VERSION__ >= 199901L)   /* C99 */ \
     || defined _MSC_VER && _MSC_VER >= 1600) /* MSVC w/o full C99 support */
# include <stdint.h>
#else
typedef signed char       int8_t;
typedef signed short      int16_t;
typedef signed int        int32_t;
typedef unsigned char     uint8_t;
typedef unsigned short    uint16_t;
typedef unsigned int      uint32_t;
#endif

/* Not all supported compilers understand the C99 'inline' keyword.  */

#if !defined __STDC_VERSION__ || __STDC_VERSION < 199901L
# if defined __SUNPRO_C || defined __hpux || defined _AIX
#  define inline
# elif defined _MSC_VER || defined __GNUC__
#  define inline __inline
# endif
#endif

/* Negative (ultra-fast) compression levels are only supported since library
   version 1.3.4.  */
#ifndef ZSTD_CLEVEL_MIN
# if ZSTD_VERSION_NUMBER >= 10304
#  define ZSTD_CLEVEL_MIN     -5
# else
#  define ZSTD_CLEVEL_MIN     1
# endif
#endif

#ifndef ZSTD_CLEVEL_MAX
# define ZSTD_CLEVEL_MAX 22
#endif

#ifndef ZSTD_CLEVEL_DEFAULT
# define ZSTD_CLEVEL_DEFAULT 3
#endif

/* Module data was added in Python 3.  */

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef ZstdModuleDef;
struct module_state {
    PyObject *error;
};
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#define ZstdError   (GETSTATE(PyState_FindModule(&ZstdModuleDef))->error)

#else

static PyObject *ZstdError;

#endif


/**
 * New more interoperable function
 * Uses origin zstd header, nothing more
 * Simple version: not for streaming, no dict support, full block compression
 */
static PyObject *py_zstd_compress(PyObject* self, PyObject *args)
{
    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    size_t cSize;
    int32_t level = ZSTD_CLEVEL_DEFAULT;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#|i", &source, &source_size, &level))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#|i", &source, &source_size, &level))
        return NULL;
#endif

    if (0 == level) level=ZSTD_CLEVEL_DEFAULT;
    /* Fast levels (zstd >= 1.3.4) - [-1..-5] */
    /* Usual levels                - [ 1..22] */
    /* If level less than -5 or 1 - raise Error, level 0 handled before. */
    if (level < ZSTD_CLEVEL_MIN) {
        PyErr_Format(ZstdError, "Bad compression level - less than %d: %d",
                     ZSTD_CLEVEL_MIN, level);
        return NULL;
    }
    /* If level more than 22 - raise Error. */
    if (level > ZSTD_CLEVEL_MAX) {
        PyErr_Format(ZstdError, "Bad compression level - more than %d: %d",
                     ZSTD_CLEVEL_MAX, level);
        return NULL;
    }

    dest_size = ZSTD_compressBound(source_size);
    result = PyBytes_FromStringAndSize(NULL, dest_size);
    if (result == NULL) {
        return NULL;
    }

    if (source_size > 0) {
        dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_compress(dest, dest_size, source, source_size, level);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Compression error: %s",
                         ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
            return NULL;
        }
        Py_SIZE(result) = cSize;
    }
    return result;
}

/**
 * New more interoperable function
 * Uses origin zstd header, nothing more
 * Simple version: not for streaming, no dict support, full block decompression
 */
static PyObject *py_zstd_decompress(PyObject* self, PyObject *args)
{
    PyObject    *result;
    const char  *source;
    uint32_t    source_size;
    uint64_t    dest_size;
    size_t      cSize;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#", &source, &source_size))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#", &source, &source_size))
        return NULL;
#endif

    dest_size = (uint64_t) ZSTD_getDecompressedSize(source, source_size);
    if (dest_size == 0) {
        PyErr_SetString(ZstdError,
            "Input data invalid or missing content size in frame header.");
        return NULL;
    }
    result = PyBytes_FromStringAndSize(NULL, dest_size);

    if (result != NULL) {
        char *dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_decompress(dest, dest_size, source, source_size);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Decompression error: %s",
                         ZSTD_getErrorName(cSize));
            Py_CLEAR(result);

        } else if (cSize != dest_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch "
                         "(expected %lu, got %lu bytes)",
                         dest_size, (unsigned long)cSize);
            Py_CLEAR(result);

        }
    }
    return result;
}

/**
 * Returns this module version as string
 */
static PyObject *py_zstd_module_version(PyObject* self)
{
#if PY_MAJOR_VERSION >= 3
    return PyUnicode_FromString(VERSION);
#else
    return PyString_FromString(VERSION);
#endif
}

/**
 * Returns ZSTD library version as string
 */
static PyObject *py_zstd_library_version(PyObject* self)
{
#if PY_MAJOR_VERSION >= 3
    return PyUnicode_FromString(ZSTD_versionString());
#else
    return PyString_FromString(ZSTD_versionString());
#endif
}

/**
 * Returns ZSTD library version as int (major * 100*100 + minor * 100 + release)
 */
static PyObject *py_zstd_library_version_int(PyObject* self)
{
#if PY_MAJOR_VERSION >= 3
    return PyLong_FromLong(ZSTD_VERSION_NUMBER);
#else
    return PyInt_FromLong(ZSTD_VERSION_NUMBER);
#endif
}

#if defined PYZSTD_LEGACY && PYZSTD_LEGACY > 0

/* Macros and other changes from python-lz4.c
 * Copyright (c) 2012-2013, Steeve Morin
 * All rights reserved. */

static inline void store_le32(char *c, uint32_t x) {
    c[0] = x & 0xff;
    c[1] = (x >> 8) & 0xff;
    c[2] = (x >> 16) & 0xff;
    c[3] = (x >> 24) & 0xff;
}

static inline uint32_t load_le32(const char *c) {
    const uint8_t *d = (const uint8_t *)c;
    return d[0] | (d[1] << 8) | (d[2] << 16) | (d[3] << 24);
}

static const uint32_t hdr_size = sizeof(uint32_t);

/**
 * Old format with custom header
 * @deprecated
 */
static PyObject *py_zstd_compress_old(PyObject* self, PyObject *args)
{
    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    size_t cSize;
    int32_t level = ZSTD_CLEVEL_DEFAULT;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#|i", &source, &source_size, &level))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#|i", &source, &source_size, &level))
        return NULL;
#endif

    /* This is old version function - no Error raising here. */
#if ZSTD_VERSION_NUMBER >= 10304
    /* Fast levels (zstd >= 1.3.4) */
    if (level < ZSTD_CLEVEL_MIN) level=ZSTD_CLEVEL_MIN;
    if (0 == level) level=ZSTD_CLEVEL_DEFAULT;
#else
    if (level <= 0) level=ZSTD_CLEVEL_DEFAULT;
#endif
    if (level > ZSTD_CLEVEL_MAX) level=ZSTD_CLEVEL_MAX;

    dest_size = ZSTD_compressBound(source_size);
    result = PyBytes_FromStringAndSize(NULL, hdr_size + dest_size);
    if (result == NULL) {
        return NULL;
    }
    dest = PyBytes_AS_STRING(result);

    store_le32(dest, source_size);
    if (source_size > 0) {

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_compress(dest + hdr_size, dest_size, source,
                              source_size, level);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Compression error: %s",
                         ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
        } else {
            Py_SIZE(result) = cSize + hdr_size;
        }
    }
    return result;
}

/**
 * Old format with custom header
 * @deprecated
 */
static PyObject *py_zstd_decompress_old(PyObject* self, PyObject *args)
{
    PyObject *result;
    const char *source;
    uint32_t source_size;
    uint32_t dest_size;
    size_t cSize;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#", &source, &source_size))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#", &source, &source_size))
        return NULL;
#endif

    if (source_size < hdr_size) {
        PyErr_SetString(ZstdError, "input too short");
        return NULL;
    }
    dest_size = load_le32(source);
    if (dest_size > INT_MAX) {
        PyErr_Format(ZstdError, "invalid size in header: 0x%x",
                     dest_size);
        return NULL;
    }
    result = PyBytes_FromStringAndSize(NULL, dest_size);

    if (result != NULL && dest_size > 0) {
        char *dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_decompress(dest, dest_size, source + hdr_size,
                                source_size - hdr_size);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Decompression error: %s",
                         ZSTD_getErrorName(cSize));
            Py_CLEAR(result);

        } else if (cSize != dest_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch "
                         "(expected %lu, got %lu bytes)",
                         dest_size, (unsigned long)cSize);
            Py_CLEAR(result);

        }
    }

    return result;
}

#endif // PYZSTD_LEGACY

#define S(x) S_(x)
#define S_(x) #x

static PyMethodDef ZstdMethods[] = {
    {"compress", py_zstd_compress, METH_VARARGS,
     "compress(data[, level]): Compress data, return the compressed form.\n\n"
     "The optional arg 'level' specifies the compression level.\n"
     "It may be from " S(ZSTD_CLEVEL_MIN) " (fastest) to " S(ZSTD_CLEVEL_MAX)
     " (slowest).  The default is " S(ZSTD_CLEVEL_DEFAULT) ".\n"
     "Using level=0 is the same as using level=" S(ZSTD_CLEVEL_DEFAULT) ".\n\n"
     "Raises a zstd.Error exception if any error occurs."
    },
    {"decompress", py_zstd_decompress, METH_VARARGS,
     "decompress(data): Decompress data, return the uncompressed form.\n\n"
     "Raises a zstd.Error exception if any error occurs."
    },
    {"version", (PyCFunction)py_zstd_module_version, METH_NOARGS,
     "version(): Return the version of the Python bindings as a string."
    },
    {"library_version", (PyCFunction)py_zstd_library_version, METH_NOARGS,
     "library_version(): Return the version of the zstd library as a string."
    },
    {"library_version_number", (PyCFunction)py_zstd_library_version_int,
     METH_NOARGS,
     "library_version_int(): Return the version of the zstd library"
     " as a number.\n"
     "The format of the number is: major*10000 + minor*100 + release.\n"
     },
#if defined PYZSTD_LEGACY && PYZSTD_LEGACY > 0
    {"compress_old", py_zstd_compress_old, METH_VARARGS,
     "compress_old(data[, level]): Compress data, return the compressed"
     " form.\n\n"
     "Uses an custom format that is not compatible with the official .zst\n"
     "file format.  Deprecated.\n\n"
     "Raises a zstd.Error exception if any error occurs."
    },
    {"decompress_old",  py_zstd_decompress_old, METH_VARARGS,
     "decompress_old(data[, level]): Decompress data, return the uncompressed"
     " form.\n\n"
     "Uses an custom format that is not compatible with the official .zst\n"
     "file format.  Deprecated.\n\n"
     "Raises a zstd.Error exception if any error occurs."
    },
#endif
    {NULL, NULL, 0, NULL}
};



#if PY_MAJOR_VERSION >= 3

static int zstd_traverse(PyObject *m, visitproc visit, void *arg)
{
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int zstd_clear(PyObject *m)
{
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef ZstdModuleDef = {
        PyModuleDef_HEAD_INIT,
        "_zstd",
        NULL,
        sizeof(struct module_state),
        ZstdMethods,
        NULL,
        zstd_traverse,
        zstd_clear,
        NULL
};

#define INITERROR return NULL
PyObject *PyInit__zstd(void)

#else
#define INITERROR return
PyMODINIT_FUNC init_zstd(void)

#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&ZstdModuleDef);
#else
    PyObject *module = Py_InitModule("_zstd", ZstdMethods);
#endif
    if (module == NULL) {
        INITERROR;
    }

    PyObject *zstd_error = PyErr_NewException("_zstd.Error", NULL, NULL);
    if (zstd_error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }
    Py_INCREF(zstd_error);
    PyModule_AddObject(module, "Error", zstd_error);

#if PY_MAJOR_VERSION >= 3
    GETSTATE(module)->error = zstd_error;
    return module;
#else
    ZstdError = zstd_error;
#endif
}
