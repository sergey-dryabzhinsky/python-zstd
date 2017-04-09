/*
 * ZSTD Library Python bindings
 * Copyright (c) 2015, Sergey Dryabzhinsky
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
#include <stdlib.h>
#include "python-zstd.h"
#include "zstd.h"


static PyObject *py_zstd_compress(PyObject* self, PyObject *args) {
/**
 * New more interoperable function
 * Uses origin zstd header, nothing more
 * Simple version: not for streaming, no dict support, full block compression
 */

    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    size_t cSize;
    uint32_t level = ZSTD_DEFAULT_CLEVEL;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#|i", &source, &source_size, &level))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#|i", &source, &source_size, &level))
        return NULL;
#endif

    if (level <= 0) level=ZSTD_DEFAULT_CLEVEL;
    if (level > ZSTD_MAX_CLEVEL) level=ZSTD_MAX_CLEVEL;

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
            PyErr_Format(ZstdError, "Compression error: %s", ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
            return NULL;
        }
        Py_SIZE(result) = cSize;
    }
    return result;
}

static PyObject *py_zstd_uncompress(PyObject* self, PyObject *args) {
/**
 * New more interoperable function
 * Uses origin zstd header, nothing more
 * Simple version: not for streaming, no dict support, full block decompression
 */

    PyObject    *result;
    const char  *source;
    uint32_t    source_size;
    uint64_t    dest_size;
    char        error = 0;
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
        PyErr_Format(PyExc_ValueError, "input data invalid or missing content size in frame header");
        return NULL;
    }
    result = PyBytes_FromStringAndSize(NULL, dest_size);

    if (result != NULL) {
        char *dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_decompress(dest, dest_size, source, source_size);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Decompression error: %s", ZSTD_getErrorName(cSize));
            error = 1;
        } else if (cSize != dest_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch -> decomp %lu != %lu [header]", (uint64_t)cSize, dest_size);
            error = 1;
        }
    }

    if (error) {
        Py_CLEAR(result);
        result = NULL;
    }

    return result;
}

#if PYZSTD_LEGACY > 0

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


static PyObject *py_zstd_compress_old(PyObject* self, PyObject *args) {
/**
 * Old format with custom header
 */

    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    size_t cSize;
    uint32_t level = ZSTD_DEFAULT_CLEVEL;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#|i", &source, &source_size, &level))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#|i", &source, &source_size, &level))
        return NULL;
#endif

    if (level <= 0) level=ZSTD_DEFAULT_CLEVEL;
    if (level > ZSTD_MAX_CLEVEL) level=ZSTD_MAX_CLEVEL;

    dest_size = ZSTD_compressBound(source_size);
    result = PyBytes_FromStringAndSize(NULL, hdr_size + dest_size);
    if (result == NULL) {
        return NULL;
    }
    dest = PyBytes_AS_STRING(result);

    store_le32(dest, source_size);
    if (source_size > 0) {

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_compress(dest + hdr_size, dest_size, source, source_size, level);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Compression error: %s", ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
        } else {
            Py_SIZE(result) = cSize + hdr_size;
        }
    }
    return result;
}

static PyObject *py_zstd_uncompress_old(PyObject* self, PyObject *args) {
/**
 * Old format with custom header
 */

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
        PyErr_SetString(PyExc_ValueError, "input too short");
        return NULL;
    }
    dest_size = load_le32(source);
    if (dest_size > INT_MAX) {
        PyErr_Format(PyExc_ValueError, "invalid size in header: 0x%x", dest_size);
        return NULL;
    }
    result = PyBytes_FromStringAndSize(NULL, dest_size);

    if (result != NULL && dest_size > 0) {
        char *dest = PyBytes_AS_STRING(result);

        Py_BEGIN_ALLOW_THREADS
        cSize = ZSTD_decompress(dest, dest_size, source + hdr_size, source_size - hdr_size);
        Py_END_ALLOW_THREADS

        if (ZSTD_isError(cSize)) {
            PyErr_Format(ZstdError, "Decompression error: %s", ZSTD_getErrorName(cSize));
            Py_CLEAR(result);
        } else if (cSize != dest_size) {
            PyErr_Format(ZstdError, "Decompression error: length mismatch - %u [Dcp] != %u [Hdr]", (uint32_t)cSize, dest_size);
            Py_CLEAR(result);
        }
    }

    return result;
}

#endif // PYZSTD_LEGACY


static PyMethodDef ZstdMethods[] = {
    {"ZSTD_compress",  py_zstd_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"ZSTD_uncompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"compress",  py_zstd_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"uncompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"decompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"dumps",  py_zstd_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"loads",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
#if PYZSTD_LEGACY > 0
    {"compress_old",  py_zstd_compress_old, METH_VARARGS, COMPRESS_OLD_DOCSTRING},
    {"decompress_old",  py_zstd_uncompress_old, METH_VARARGS, UNCOMPRESS_OLD_DOCSTRING},
#endif
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
