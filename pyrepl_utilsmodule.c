
/*   Copyright 2000-2001 Michael Hudson mwh@python.net
 *
 *                        All Rights Reserved
 *
 *
 * Permission to use, copy, modify, and distribute this software and
 * its documentation for any purpose is hereby granted without fee,
 * provided that the above copyright notice appear in all copies and
 * that both that copyright notice and this permission notice appear in
 * supporting documentation.
 *
 * THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
 * THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
 * INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
 * RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
 * CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include <Python.h>

/* nothing here that can't be done in Python, but it helps to be able 
   to do it quicker */

static char* _unctrl_map[255];

static PyObject*
pyrepl_utils_init_unctrl_map(PyObject* self, PyObject* args)
{
	PyObject* dict;
	PyObject* pyc;
	PyObject* pys;
	int c = 0;
	char cc;

	if (!PyArg_ParseTuple(args, "O", &dict)) {
		return NULL;
	}

	if (!PyDict_Check(dict)) {
		PyErr_SetString(PyExc_TypeError,
				"init_unctrl_map: must be dict");
	}

	for (c = 0; c < 256; c++) {
		cc = c;
		pyc = PyString_FromStringAndSize(&cc,1);
		if (!pyc) return NULL;
		pys = PyDict_GetItem(dict, pyc);
		if (!pys) {
			PyErr_Format(PyExc_KeyError,
				     "%c",cc);
			_unctrl_map[0] = NULL;
			return NULL;
		}
		if (!PyString_Check(pys)) {
			PyErr_SetString(PyExc_TypeError,
				"init_unctrl_map: found non-string");
		}
		Py_INCREF(pys); /* this ain't going away */
		_unctrl_map[c] = PyString_AS_STRING(pys);
		Py_DECREF(pyc);
	}

	Py_INCREF(Py_None);
	return Py_None;
}

static char pyrepl_utils_init_unctrl_map_doc[] = 
" init_unctrl_map(unctrl_map:dict) -> None\n\
\n\
Call this before calling disp_str.";

static PyObject*
pyrepl_utils_disp_str(PyObject* self, PyObject* args)
{
	char *s;
	char *r;
	char **temp;
	int slen = 0, rlen = 0;
	int i, j, k, n;
	PyObject *list, *ret;

	if (!PyArg_ParseTuple(args, "s#", &s, &slen)) {
		return NULL;
	}

	if (!_unctrl_map[0]) {
		PyErr_SetString(PyExc_RuntimeError,
				"bad boy!");
		return NULL;
	}

	temp = malloc(sizeof(char*)*slen);
	if (!temp) {
		PyErr_NoMemory();
		return NULL;
	}

	for (i = 0; i < slen; i++) {
		temp[i] = _unctrl_map[(unsigned char)s[i]];
		rlen += strlen(temp[i]);
	}

	r = malloc(rlen + 1);
	if (!r) {
		free(temp);
		PyErr_NoMemory();
		return NULL;
	}

	list = PyList_New(rlen);
	if (!list) {
		free(r);
		free(temp);
		return NULL;
	}

	for (i = 0, j = 0; i < slen; i++) {
		n = strlen(temp[i]);
		memcpy(&r[j], temp[i], n);
		PyList_SET_ITEM(list, j, PyInt_FromLong(1));
		k = j + 1;
		j += n;
		while (k < j) {
			PyList_SET_ITEM(list, k, PyInt_FromLong(0));
			k++;
		}
	}

	free(temp);
	r[rlen] = '\000';

	ret = Py_BuildValue("(sN)", r, list);

	free(r);

	return ret;
}

static char pyrepl_utils_disp_str_doc[] = 
" disp_str(buffer:string) -> (string, [int])\n\
\n\
Return the string that should be the printed represenation of\n\
|buffer| and a list detailing where the characters of |buffer|\n\
get used up.  E.g:\n\
\n\
>>> disp_str('\\003')\n\
('^C', [1, 0])\n\
\n\
the list always contains 0s or 1s at present; it could conceivably\n\
go higher as and when unicode support happens.\n\
\n\
You MUST call init_unctrl_map before using this version.";


PyMethodDef pyrepl_utils_methods[] = {
	{ "init_unctrl_map", pyrepl_utils_init_unctrl_map, 
	  METH_VARARGS,      pyrepl_utils_init_unctrl_map_doc },
	{ "disp_str",        pyrepl_utils_disp_str, 
	  METH_VARARGS,      pyrepl_utils_disp_str_doc },
	{ NULL, NULL }
};

static char pyrepl_utils_doc[] = 
"Utilities to help speed up pyrepl.";

void init_pyrepl_utils(void)
{
	Py_InitModule3("_pyrepl_utils", 
		       pyrepl_utils_methods,
		       pyrepl_utils_doc);
}
