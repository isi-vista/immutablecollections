#include <Python.h>
#include <structmember.h>

// based off of PVector https://github.com/tobgu/pyrsistent/blob/master/pvectorcmodule.c
static PyTypeObject ImmutableSetType;

// #define debug(...)
#define debug printf

typedef struct {
    PyObject_HEAD;
    PyObject* orderList;
    PyObject* wrappedSet;
    //PyObject *in_weakreflist; /* List of weak references */
} ImmutableSet;

#define HANDLE_ITERATION_ERROR()                         \
    if (PyErr_Occurred()) {                              \
      if (PyErr_ExceptionMatches(PyExc_StopIteration)) { \
        PyErr_Clear();                                   \
      } else {                                           \
        return NULL;                                     \
      }                                                  \
    }

// No access to internal members
static PyMemberDef ImmutableSet_members[] = {
        {NULL}  /* Sentinel */
};

static void ImmutableSet_dealloc(ImmutableSet *self) {
    debug("In dealloc\n");
    PyObject_ClearWeakRefs((PyObject *) self);
    debug("post clear weakrefs\n");

    PyObject_GC_UnTrack((PyObject*)self);
    Py_TRASHCAN_SAFE_BEGIN(self);

    PyMem_Free(self->orderList);
    PyMem_Free(self->wrappedSet);

    PyObject_GC_Del(self);
    Py_TRASHCAN_SAFE_END(self);
    debug("end dealloc\n");
}

static long ImmutableSet_hash(ImmutableSet* self) {
    return PyObject_Hash(self->wrappedSet);
}

static Py_ssize_t ImmutableSet_len(ImmutableSet* self) {
    return PyList_Size(self->orderList);
}

static int ImmutableSet_contains(ImmutableSet* self, PyObject* queryItem) {
    return PySet_Contains(self->wrappedSet, queryItem);
}

static PyObject* ImmutableSet_get_item(ImmutableSet *self, Py_ssize_t pos) {
    return PyList_GetItem(self->orderList, pos);
}

static PySequenceMethods ImmutableSet_sequence_methods = {
        (lenfunc)ImmutableSet_len,            /* sq_length */
        NULL,      /* sq_concat - n/a (immutable) */
        NULL /*(ssizeargfunc)PVector_repeat*/,    /* sq_repeat */
        (ssizeargfunc)ImmutableSet_get_item,  /* sq_item */
        // TODO: should we support slicing?
        NULL,                            /* sq_slice */
        NULL,                            /* sq_ass_item */
        NULL,                            /* sq_ass_slice */
        (objobjproc)ImmutableSet_contains, /* sq_contains */
        NULL,                            /* sq_inplace_concat */
        NULL,                            /* sq_inplace_repeat */
};

static PyMethodDef ImmutableSet_methods[] = {
        //{"index",       (PyCFunction)PVector_index, METH_VARARGS, "Return first index of value"},
        //{"tolist",      (PyCFunction)PVector_toList, METH_NOARGS, "Convert to list"},
        {NULL}
};

static PyObject *ImmutableSet_repr(ImmutableSet *self) {
    // Reuse the list repr code, a bit less efficient but saves some code
    PyObject *list_repr = PyObject_Repr(self->orderList);

    if(list_repr == NULL) {
        // Exception raised during call to repr
        return NULL;
    }

    // TODO: strip []s from list repr
    PyObject *s = PyUnicode_FromFormat("%s%U%s", "i{", list_repr, "}");
    Py_DECREF(list_repr);

    return s;
}

static PyTypeObject ImmutableSetType = {
        PyVarObject_HEAD_INIT(NULL, 0)
        "immutablecollections.ImmutableSet",                         /* tp_name        */
        sizeof(ImmutableSet),                            /* tp_basicsize   */
        0,		                              /* tp_itemsize    */
(destructor)ImmutableSet_dealloc,                /* tp_dealloc     */
        0,                                          /* tp_print       */
        0,                                          /* tp_getattr     */
        0,                                          /* tp_setattr     */
        0,                                          /* tp_compare     */
        (reprfunc)ImmutableSet_repr,                     /* tp_repr        */
        0,                                          /* tp_as_number   */
        &ImmutableSet_sequence_methods,                  /* tp_as_sequence */
        0/*&PVector_mapping_methods*/,                   /* tp_as_mapping  */
(hashfunc)ImmutableSet_hash,                     /* tp_hash        */
        0,                                          /* tp_call        */
        0,                                          /* tp_str         */
        0,                                          /* tp_getattro    */
        0,                                          /* tp_setattro    */
        0,                                          /* tp_as_buffer   */
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags       */
        "ImmutableSet",   	              /* tp_doc         */
0/*(traverseproc)PVector_traverse*/,             /* tp_traverse       */
        0,                                          /* tp_clear          */
        0/*PVector_richcompare*/,                        /* tp_richcompare    */
        0/*offsetof(PVector, in_weakreflist)*/,          /* tp_weaklistoffset */
        0/*PVectorIter_iter*/,                           /* tp_iter           */
        0,                                          /* tp_iternext       */
        ImmutableSet_methods,                            /* tp_methods        */
        ImmutableSet_members,                            /* tp_members        */
        0,                                          /* tp_getset         */
        0,                                          /* tp_base           */
        0,                                          /* tp_dict           */
        0,                                          /* tp_descr_get      */
        0,                                          /* tp_descr_set      */
        0,                                          /* tp_dictoffset     */
};

static PyObject* immutablecollections_immutableset(PyObject *self, PyObject *args) {
    PyObject *argObj = NULL;  /* list of arguments */
    PyObject *it;
    PyObject *(*iternext)(PyObject *);

    ImmutableSet *immutableset = PyObject_GC_New(ImmutableSet, &ImmutableSetType);
    PyObject_GC_Track((PyObject*)immutableset);
    immutableset->orderList = PyList_New(0);
    immutableset->wrappedSet = PySet_New(NULL);

    if(!PyArg_ParseTuple(args, "|O", &argObj)) {
        return NULL;
    }

    it = PyObject_GetIter(argObj);
    if (it == NULL) {
        return NULL;
    }

    iternext = *Py_TYPE(it)->tp_iternext;
    PyObject *item = iternext(it);
    if (item == NULL) {
        Py_DECREF(it);
        HANDLE_ITERATION_ERROR();
        Py_INCREF(self);
        // TODO: should have a singleton empty set object
        return (PyObject *)immutableset;
    } else {
        while (item != NULL) {
            if (!PySet_Contains(immutableset->wrappedSet, item)) {
                PySet_Add(immutableset->wrappedSet, item);
                PyList_Append(immutableset->orderList, item);
            }
            item = iternext(it);
        }

        Py_DECREF(it);
        HANDLE_ITERATION_ERROR();
        return (PyObject *) immutableset;
    }
}

static PyObject *ImmutableSet_subscript(ImmutableSet* self, PyObject* item) {
    // TODO: call get_item on internal list
    return NULL;
}

static PyMethodDef ImmutableCollectionMethods[] = {
        {"immutableset", immutablecollections_immutableset, METH_VARARGS,
                        "immutableset([iterable])\n"
                        "Create a new immutableset containing the elements in iterable.\n\n"
                        ">>> set1 = immutableset([1, 2, 3])\n"
                        ">>> set\n"
                        "immutableset([1, 2, 3])"},
        {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "immutablecollections",          /* m_name */
    "Immutable Collections", /* m_doc */
    -1,                  /* m_size */
    ImmutableCollectionMethods,   /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };


PyObject* moduleinit(void) {
    PyObject* m;

    // Only allow creation/initialization through factory method pvec
    //PVectorType.tp_init = NULL;
    //PVectorType.tp_new = NULL;

    if (PyType_Ready(&ImmutableSetType) < 0) {
        return NULL;
    }


    m = PyModule_Create(&moduledef);

    if (m == NULL) {
        return NULL;
    }

    /*if(EMPTY_VECTOR == NULL) {
        EMPTY_VECTOR = emptyNewPvec();
    }*/

    Py_INCREF(&ImmutableSetType);
    PyModule_AddObject(m, "ImmutableSet", (PyObject *)&ImmutableSetType);

    return m;
}

PyMODINIT_FUNC PyInit_immutablecollections(void) {
    return moduleinit();
}