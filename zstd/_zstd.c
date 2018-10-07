/*
 * ZSTD Library Python bindings
 * Copyright (c) 2015-2018, Sergey Dryabzhinsky
 * All rights reserved.
 *
 * BSD License
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * * Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <Python.h>
#include "zstd.h"

#if ZSTD_VERSION_NUMBER < 10304
# error "python-zstd must be built using libzstd >= 1.3.4"
#endif

#if (PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION < 6) \
 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 2)
# error "python-zstd must be built using Python 2.(>=6) or 3.(>=2)"
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

#ifndef ZSTD_CLEVEL_MIN
# define ZSTD_CLEVEL_MIN     -5
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

/* Other Python 2/3 differences.  */
#if PY_MAJOR_VERSION >= 3

/* PyString_FromString is used in a few places where we specifically
   want the "normal" string type: bytes for Py2, unicode for Py3.  */
#define PlainString_FromString(s) PyUnicode_FromString(s)

/* The argument-tuple code for a read-only character buffer changed in
   Py3.  */
#define CBUF "y#"

#else

#define PlainString_FromString(s) PyBytes_FromString(s)
#define CBUF "t#"

#endif

/* For use in docstrings.  */
#define S_(x) #x
#define S(x) S_(x)
#define SZL S(ZSTD_CLEVEL_MIN)
#define SZD S(ZSTD_CLEVEL_DEFAULT)
#define SZH S(ZSTD_CLEVEL_MAX)


PyDoc_STRVAR(compress_doc,
    "compress(data, level="SZD")\n"
    "--\n\n"
    "Compress data and return the compressed form.\n"
    "The compression level may be from "SZL" (fastest) to "SZH" (slowest).\n"
    "The default is "SZD".  level=0 is the same as level="SZD".\n"
    "\n"
    "Raises a zstd.Error exception if any error occurs.");

static PyObject *compress(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    size_t cSize;
    int32_t level = ZSTD_CLEVEL_DEFAULT;

    static char *kwlist[] = {"data", "level", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, CBUF"|i:compress", kwlist,
                                     &source, &source_size, &level))
        return NULL;

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

        Py_BEGIN_ALLOW_THREADS;
        cSize = ZSTD_compress(dest, dest_size, source, source_size, level);
        Py_END_ALLOW_THREADS;

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Compression error: %s",
                         ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
            return NULL;
        }
        _PyBytes_Resize(&result, cSize);
    }
    return result;
}


PyDoc_STRVAR(decompress_doc,
    "decompress(data)\n"
    "--\n\n"
    "Decompress data and return the uncompressed form.\n"
    "Raises a zstd.Error exception if any error occurs.");

static PyObject *decompress(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyObject    *result;
    const char  *source;
    uint32_t    source_size;
    uint64_t    dest_size;
    size_t      cSize;

    static char *kwlist[] = {"data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, CBUF":decompress", kwlist,
                                     &source, &source_size))
        return NULL;

    dest_size = (uint64_t) ZSTD_getDecompressedSize(source, source_size);
    if (dest_size == 0) {
        PyErr_SetString(ZstdError,
            "Input data invalid or missing content size in frame header.");
        return NULL;
    }
    result = PyBytes_FromStringAndSize(NULL, dest_size);

    if (result != NULL) {
        char *dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS;
        cSize = ZSTD_decompress(dest, dest_size, source, source_size);
        Py_END_ALLOW_THREADS;

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

PyDoc_STRVAR(version_doc,
    "version()\n"
    "--\n\n"
    "Return the version of the Python bindings as a string.");

static PyObject *version(PyObject* self)
{
    return PlainString_FromString(VERSION);
}


PyDoc_STRVAR(library_version_doc,
    "library_version()\n"
    "--\n\n"
    "Return the version of the zstd library as a string.");

static PyObject *library_version(PyObject* self)
{
    return PlainString_FromString(ZSTD_versionString());
}


PyDoc_STRVAR(library_version_number_doc,
    "library_version_number()\n"
    "--\n\n"
    "Return the version of the zstd library as a number.\n"
    "The format of the number is: major*100*100 + minor*100 + release.\n");

static PyObject *library_version_number(PyObject* self)
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


PyDoc_STRVAR(compress_old_doc,
    "compress_old(data, level="SZD")\n"
    "--\n\n"
    "Compress data and return the compressed form.\n\n"
    "Produces a custom compressed format that is not compatible with\n"
    "the standard .zst file format.  Deprecated.\n\n"
    "Raises a zstd.Error exception if any error occurs.");

static PyObject *compress_old(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    size_t cSize;
    int32_t level = ZSTD_CLEVEL_DEFAULT;

    static char *kwlist[] = {"data", "level", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, CBUF"|i:compress_old", kwlist,
                                     &source, &source_size, &level))
        return NULL;

    /* This is old version function - no Error raising here. */
    if (0 == level) level=ZSTD_CLEVEL_DEFAULT;
    if (level < ZSTD_CLEVEL_MIN) level=ZSTD_CLEVEL_MIN;
    if (level > ZSTD_CLEVEL_MAX) level=ZSTD_CLEVEL_MAX;

    dest_size = ZSTD_compressBound(source_size);
    result = PyBytes_FromStringAndSize(NULL, hdr_size + dest_size);
    if (result == NULL) {
        return NULL;
    }
    dest = PyBytes_AS_STRING(result);

    store_le32(dest, source_size);
    if (source_size > 0) {

        Py_BEGIN_ALLOW_THREADS;
        cSize = ZSTD_compress(dest + hdr_size, dest_size, source,
                              source_size, level);
        Py_END_ALLOW_THREADS;

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Compression error: %s",
                         ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
        } else {
            _PyBytes_Resize(&result, cSize + hdr_size);
        }
    }
    return result;
}

PyDoc_STRVAR(decompress_old_doc,
    "decompress_old(data)\n"
    "--\n\n"
    "Decompress data and return the uncompressed form.\n\n"
    "Expects a custom compressed format that is not compatible with\n"
    "the standard .zst file format.  Deprecated.\n\n"
    "Raises a zstd.Error exception if any error occurs.");

static PyObject *decompress_old(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyObject *result;
    const char *source;
    uint32_t source_size;
    uint32_t dest_size;
    size_t cSize;

    static char *kwlist[] = {"data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, CBUF":decompress_old", kwlist,
                                     &source, &source_size))
        return NULL;

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

        Py_BEGIN_ALLOW_THREADS;
        cSize = ZSTD_decompress(dest, dest_size, source + hdr_size,
                                source_size - hdr_size);
        Py_END_ALLOW_THREADS;

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

#endif // PYZSTD_LEGACY > 0

static PyMethodDef ZstdMethods[] = {
    {"compress", (PyCFunction)compress, METH_VARARGS|METH_KEYWORDS,
     compress_doc},
    {"decompress", (PyCFunction)decompress, METH_VARARGS|METH_KEYWORDS,
     decompress_doc},
    {"version", (PyCFunction)version, METH_NOARGS, version_doc},
    {"library_version", (PyCFunction)library_version, METH_NOARGS,
     library_version_doc},
    {"library_version_number", (PyCFunction)library_version_number,
     METH_NOARGS, library_version_number_doc},
#if defined PYZSTD_LEGACY && PYZSTD_LEGACY > 0
    {"compress_old", (PyCFunction)compress_old, METH_VARARGS|METH_KEYWORDS,
     compress_old_doc},
    {"decompress_old", (PyCFunction)decompress_old, METH_VARARGS|METH_KEYWORDS,
     decompress_old_doc},
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

PyDoc_STRVAR(zstd_module_doc,
    "C extension wrapping libzstd.  Not meant to be used directly;\n"
    "use the parent module instead.");

static struct PyModuleDef ZstdModuleDef = {
        PyModuleDef_HEAD_INIT,
        "_zstd",
        zstd_module_doc,
        sizeof(struct module_state),
        ZstdMethods,
        NULL,
        zstd_traverse,
        zstd_clear,
        NULL
};

PyMODINIT_FUNC PyInit__zstd(void)
{
    PyObject *module = PyModule_Create(&ZstdModuleDef);
    if (module == NULL) {
        return NULL;
    }

    PyDoc_STRVAR(zstd_error_doc,
                 "Zstd compression or decompression error.");

    PyObject *zstd_error = PyErr_NewExceptionWithDoc(
        "_zstd.Error", zstd_error_doc, NULL, NULL);
    if (zstd_error == NULL) {
        Py_DECREF(module);
        return NULL;
    }
    GETSTATE(module)->error = zstd_error;
    Py_INCREF(zstd_error);
    PyModule_AddObject(module, "Error", zstd_error);

    return module;
}

#else

PyMODINIT_FUNC init_zstd(void)
{
    PyObject *module = Py_InitModule("_zstd", ZstdMethods);
    if (module == NULL) {
        return;
    }

    ZstdError = PyErr_NewException("_zstd.Error", NULL, NULL);
    if (ZstdError == NULL) {
        Py_DECREF(module);
        return;
    }
    Py_INCREF(ZstdError);
    PyModule_AddObject(module, "Error", ZstdError);
}

#endif
