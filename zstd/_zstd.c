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

#define PY_SSIZE_T_CLEAN
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

/* Not all supported compilers understand the C99 'inline' keyword.  */

#if !defined __STDC_VERSION__ || __STDC_VERSION < 199901L
# if defined __SUNPRO_C || defined __hpux || defined _AIX
#  define inline
# elif defined _MSC_VER || defined __GNUC__
#  define inline __inline
# endif
#endif

#ifndef ZSTD_CLEVEL_MIN
# define ZSTD_CLEVEL_MIN -5
#endif

#ifndef ZSTD_CLEVEL_MAX
# define ZSTD_CLEVEL_MAX 22
#endif

#ifndef ZSTD_CLEVEL_DEFAULT
# define ZSTD_CLEVEL_DEFAULT 3
#endif

/* Python 2/3 differences.  */
#if PY_MAJOR_VERSION >= 3

/* Module data was added in Python 3.  */
static struct PyModuleDef ZstdModuleDef;
struct module_state {
    PyObject *error;
};
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#define ZstdError   (GETSTATE(PyState_FindModule(&ZstdModuleDef))->error)

/* This is used in a few places where we specifically want the
   "normal" string type: bytes for Py2, unicode for Py3.  */
#define PlainString_FromString(s) PyUnicode_FromString(s)

#else

static PyObject *ZstdError;
#define PlainString_FromString(s) PyString_FromString(s)

#endif


/* This does what 3.x's "y*" argument tuple code would do, in a 2.x/3.x-
   agnostic way.  Returns 0 on success, -1 on failure (in which case an
   exception has been set).  As with "y*", caller is responsible for
   calling PyBuffer_Release.  */
static int
obj_AsByteBuffer(PyObject *obj, Py_buffer *view)
{
    if (PyObject_GetBuffer(obj, view, PyBUF_SIMPLE) != 0) {
        PyErr_SetString(PyExc_TypeError, "a bytes-like object is required");
        return -1;
    }
    if (!PyBuffer_IsContiguous(view, 'C')) {
        PyBuffer_Release(view);
        PyErr_SetString(PyExc_TypeError, "a contiguous buffer is required");
        return -1;
    }
    return 0;
}


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
    PyObject *src;
    Py_buffer srcbuf;
    PyObject *dst;
    char *dst_ptr;
    size_t dst_size;
    size_t c_size;
    int level = ZSTD_CLEVEL_DEFAULT;

    static char *kwlist[] = {"data", "level", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|i:compress", kwlist,
                                     &src, &level))
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

    if (obj_AsByteBuffer(src, &srcbuf))
        return NULL;

    dst_size = ZSTD_compressBound(srcbuf.len);
    dst = PyBytes_FromStringAndSize(NULL, dst_size);
    if (dst == NULL) {
        PyBuffer_Release(&srcbuf);
        return NULL;
    }

    dst_ptr = PyBytes_AS_STRING(dst);

    Py_BEGIN_ALLOW_THREADS;
    c_size = ZSTD_compress(dst_ptr, dst_size, srcbuf.buf, srcbuf.len,
                           level);
    Py_END_ALLOW_THREADS;

    if (ZSTD_isError(c_size)) {
        PyErr_Format(ZstdError, "Compression error: %s",
                     ZSTD_getErrorName(c_size));
        Py_CLEAR(dst);
    } else {
        _PyBytes_Resize(&dst, c_size);
    }

    PyBuffer_Release(&srcbuf);
    return dst;
}


PyDoc_STRVAR(decompress_doc,
    "decompress(data)\n"
    "--\n\n"
    "Decompress data and return the uncompressed form.\n"
    "Raises a zstd.Error exception if any error occurs.");

static PyObject *decompress(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyObject *src;
    Py_buffer srcbuf;
    PyObject *dst;
    char *dst_ptr;
    size_t dst_size;
    size_t c_size;
    unsigned long long raw_frame_size;

    static char *kwlist[] = {"data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:decompress", kwlist,
                                     &src))
        return NULL;

    if (obj_AsByteBuffer(src, &srcbuf))
        return NULL;

    raw_frame_size = ZSTD_getFrameContentSize(srcbuf.buf, srcbuf.len);
    if (raw_frame_size == ZSTD_CONTENTSIZE_ERROR) {
        PyErr_SetString(ZstdError, "compressed data is invalid");
        PyBuffer_Release(&srcbuf);
        return NULL;
    }
    if (raw_frame_size == ZSTD_CONTENTSIZE_UNKNOWN) {
        PyErr_SetString(ZstdError,
                        "decompress() cannot handle compressed data "
                        "with unknown decompressed size");
        PyBuffer_Release(&srcbuf);
        return NULL;
    }
    if (raw_frame_size > (unsigned long long)PY_SSIZE_T_MAX) {
        PyErr_SetString(ZstdError,
                        "decompressed data is too large for a bytes object");
        PyBuffer_Release(&srcbuf);
        return NULL;
    }

    dst_size = (size_t) raw_frame_size;
    dst = PyBytes_FromStringAndSize(NULL, dst_size);

    if (dst != NULL) {
        dst_ptr = PyBytes_AS_STRING(dst);

        Py_BEGIN_ALLOW_THREADS;
        c_size = ZSTD_decompress(dst_ptr, dst_size, srcbuf.buf, srcbuf.len);
        Py_END_ALLOW_THREADS;

        if (ZSTD_isError(c_size)) {
            PyErr_Format(ZstdError, "Decompression error: %s",
                         ZSTD_getErrorName(c_size));
            Py_CLEAR(dst);

        } else if (c_size != dst_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch "
                         "(expected %zu, got %zu bytes)", dst_size, c_size);
            Py_CLEAR(dst);
        }
    }

    PyBuffer_Release(&srcbuf);
    return dst;
}

PyDoc_STRVAR(library_version_doc,
    "library_version()\n"
    "--\n\n"
    "Return the version of the zstd library as a string.\n"
    "The value returned will be different from the LIBRARY_VERSION\n"
    "constant when the library in use at runtime is a different version\n"
    "from the library this module was compiled against.");

static PyObject *library_version(PyObject* self)
{
    return PlainString_FromString(ZSTD_versionString());
}


PyDoc_STRVAR(library_version_number_doc,
    "library_version_number()\n"
    "--\n\n"
    "Return the version of the zstd library as a number.\n"
    "The format of the number is: major*100*100 + minor*100 + release.\n"
    "The value returned will be different from the LIBRARY_VERSION_NUMBER\n"
    "constant when the library in use at runtime is a different version\n"
    "from the library this module was compiled against.");

static PyObject *library_version_number(PyObject* self)
{
#if PY_MAJOR_VERSION >= 3
    return PyLong_FromLong(ZSTD_versionNumber());
#else
    return PyInt_FromLong(ZSTD_versionNumber());
#endif
}

#if defined PYZSTD_LEGACY && PYZSTD_LEGACY > 0

/* Macros and other changes from python-lz4.c
 * Copyright (c) 2012-2013, Steeve Morin
 * All rights reserved. */

static const Py_ssize_t old_max_size = 0x7fffffff;
static const size_t hdr_size = 4;

static inline void store_le32(char *c, size_t x)
{
    c[0] = (x >>  0) & 0xff;
    c[1] = (x >>  8) & 0xff;
    c[2] = (x >> 16) & 0xff;
    c[3] = (x >> 24) & 0xff;
}

static inline size_t load_le32(const char *c)
{
    return
        (((size_t)(unsigned char) c[0]) <<  0) |
        (((size_t)(unsigned char) c[1]) <<  8) |
        (((size_t)(unsigned char) c[2]) << 16) |
        (((size_t)(unsigned char) c[3]) << 24);
}


PyDoc_STRVAR(compress_old_doc,
    "compress_old(data, level="SZD")\n"
    "--\n\n"
    "Compress data and return the compressed form.\n\n"
    "Produces a custom compressed format that is not compatible with\n"
    "the standard .zst file format.  Deprecated.\n\n"
    "Raises a zstd.Error exception if any error occurs.");

static PyObject *compress_old(PyObject* self, PyObject *args, PyObject *kwds)
{
    PyObject *src;
    Py_buffer srcbuf;
    PyObject *dst;
    char *dst_ptr;
    size_t dst_size;
    size_t c_size;
    int level = ZSTD_CLEVEL_DEFAULT;

    static char *kwlist[] = {"data", "level", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|i:compress_old", kwlist,
                                     &src, &level))
        return NULL;

    /* This is old version function - no Error raising here. */
    if (0 == level) level=ZSTD_CLEVEL_DEFAULT;
    if (level < ZSTD_CLEVEL_MIN) level=ZSTD_CLEVEL_MIN;
    if (level > ZSTD_CLEVEL_MAX) level=ZSTD_CLEVEL_MAX;

    if (obj_AsByteBuffer(src, &srcbuf))
        return NULL;

    if (srcbuf.len > old_max_size) {
        PyErr_Format(ZstdError, "input of %zd bytes is too large "
                     "for old compressed format", srcbuf.len);
        PyBuffer_Release(&srcbuf);
        return NULL;
    }

    dst_size = ZSTD_compressBound(srcbuf.len);
    dst = PyBytes_FromStringAndSize(NULL, hdr_size + dst_size);
    if (dst == NULL) {
        PyBuffer_Release(&srcbuf);
        return NULL;
    }
    dst_ptr = PyBytes_AS_STRING(dst);

    store_le32(dst_ptr, srcbuf.len);
    if (srcbuf.len > 0) {

        Py_BEGIN_ALLOW_THREADS;
        c_size = ZSTD_compress(dst_ptr + hdr_size, dst_size,
                               srcbuf.buf, srcbuf.len, level);
        Py_END_ALLOW_THREADS;

        if (ZSTD_isError(c_size)) {
            PyErr_Format(ZstdError, "Compression error: %s",
                         ZSTD_getErrorName(c_size));
            Py_CLEAR(dst);
        } else {
            _PyBytes_Resize(&dst, c_size + hdr_size);
        }
    }

    PyBuffer_Release(&srcbuf);
    return dst;
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
    PyObject *src;
    Py_buffer srcbuf;
    PyObject *dst;
    char *dst_ptr;
    size_t dst_size;
    size_t c_size;

    static char *kwlist[] = {"data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:decompress_old", kwlist,
                                     &src))
        return NULL;

    if (obj_AsByteBuffer(src, &srcbuf))
        return NULL;

    if (srcbuf.len < hdr_size) {
        PyErr_SetString(ZstdError, "input too short");
        PyBuffer_Release(&srcbuf);
        return NULL;
    }
    dst_size = load_le32(srcbuf.buf);

    if (dst_size > old_max_size) {
        PyErr_Format(ZstdError, "invalid size in header: %zu (too large)",
                     dst_size);
        PyBuffer_Release(&srcbuf);
        return NULL;
    }
    dst = PyBytes_FromStringAndSize(NULL, dst_size);

    if (dst != NULL && dst_size > 0) {
        dst_ptr = PyBytes_AS_STRING(dst);

        Py_BEGIN_ALLOW_THREADS;
        c_size = ZSTD_decompress(dst_ptr, dst_size,
                                 srcbuf.buf + hdr_size, srcbuf.len - hdr_size);
        Py_END_ALLOW_THREADS;

        if (ZSTD_isError(c_size)) {
            PyErr_Format(ZstdError, "Decompression error: %s",
                         ZSTD_getErrorName(c_size));
            Py_CLEAR(dst);

        } else if (c_size != dst_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch "
                         "(expected %zu, got %zu bytes)",
                         dst_size, c_size);
            Py_CLEAR(dst);

        }
    }

    PyBuffer_Release(&srcbuf);
    return dst;
}

#endif // PYZSTD_LEGACY > 0

static void zstd_add_constants(PyObject *module)
{
    PyModule_AddStringConstant(module, "VERSION", PKG_VERSION_STR);
    PyModule_AddStringConstant(module, "LIBRARY_VERSION", ZSTD_VERSION_STRING);
    PyModule_AddIntConstant(module, "LIBRARY_VERSION_NUMBER",
                            ZSTD_VERSION_NUMBER);

    PyModule_AddIntConstant(module, "CLEVEL_MIN", ZSTD_CLEVEL_MIN);
    PyModule_AddIntConstant(module, "CLEVEL_MAX", ZSTD_CLEVEL_MAX);
    PyModule_AddIntConstant(module, "CLEVEL_DEFAULT", ZSTD_CLEVEL_DEFAULT);
}

static PyMethodDef ZstdMethods[] = {
    {"compress", (PyCFunction)compress, METH_VARARGS|METH_KEYWORDS,
     compress_doc},
    {"decompress", (PyCFunction)decompress, METH_VARARGS|METH_KEYWORDS,
     decompress_doc},
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

PyDoc_STRVAR(zstd_module_doc,
    "C extension wrapping libzstd.  Not meant to be used directly;\n"
    "use the parent module instead.");

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
    if (module == NULL)
        return NULL;

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

    zstd_add_constants(module);
    return module;
}

#else

PyMODINIT_FUNC init_zstd(void)
{
    PyObject *module = Py_InitModule3("_zstd", ZstdMethods,
                                      zstd_module_doc);
    if (module == NULL)
        return;

    ZstdError = PyErr_NewException("_zstd.Error", NULL, NULL);
    if (ZstdError == NULL) {
        Py_DECREF(module);
        return;
    }
    Py_INCREF(ZstdError);
    PyModule_AddObject(module, "Error", ZstdError);

    zstd_add_constants(module);
}

#endif
