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

#ifndef ZSTD_DEFAULT_CLEVEL
/*-=====  Pre-defined compression levels  =====-*/

#define ZSTD_DEFAULT_CLEVEL 5
#define ZSTD_MAX_CLEVEL     22
#endif

static PyObject *py_zstd_compress(PyObject* self, PyObject *args) {

    PyObject *result;
    const char *source;
    uint32_t source_size;
    char *dest;
    uint32_t dest_size;
    uint32_t header_size;
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

    header_size = sizeof(source_size);

    dest_size = ZSTD_compressBound(source_size);
    result = PyBytes_FromStringAndSize(NULL, header_size + dest_size);
    if (result == NULL) {
        return NULL;
    }
    dest = PyBytes_AS_STRING(result);

    memcpy(dest, &source_size, header_size);

    dest += header_size;

    if (source_size > 0) {
        // Low level == old version
        cSize = ZSTD_compress(dest, dest_size, source, source_size, level);
        if (ZSTD_isError(cSize))
            PyErr_Format(ZstdError, "Compression error: %s", ZSTD_getErrorName(cSize));
        Py_SIZE(result) = cSize + header_size;
    }
    return result;
}

static PyObject *py_zstd_uncompress(PyObject* self, PyObject *args) {

    PyObject *result;
    const char *source;
    uint32_t source_size;
    uint32_t dest_size;
    uint32_t header_size;
    size_t cSize;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#", &source, &source_size))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#", &source, &source_size))
        return NULL;
#endif

    header_size = sizeof(dest_size);

    memcpy(&dest_size, source, header_size);
    result = PyBytes_FromStringAndSize(NULL, dest_size);

    source += header_size;

    if (result != NULL && dest_size > 0) {
        char *dest = PyBytes_AS_STRING(result);

        cSize = ZSTD_decompress(dest, dest_size, source, source_size - header_size);
        if (ZSTD_isError(cSize))
            PyErr_Format(ZstdError, "Decompression error: %s", ZSTD_getErrorName(cSize));
    }

    return result;
}

static PyMethodDef ZstdMethods[] = {
    {"ZSTD_compress",  py_zstd_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"ZSTD_uncompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"compress",  py_zstd_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"uncompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"decompress",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {"dumps",  py_zstd_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"loads",  py_zstd_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
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
