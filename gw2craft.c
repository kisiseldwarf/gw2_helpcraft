#define PY_SSIZE_T_CLEAN
#include<Python.h>

int main(int argc, char* argv[]){
    Py_Initialize();
    wchar_t* python_args[argc];
    for(int i = 0; i < argc; i++){
        size_t size = strlen(argv[i]);
        python_args[i] = Py_DecodeLocale(argv[i], &size);
    }
    PySys_SetArgv(argc, python_args);
    FILE* fd = fopen("gw2craft.py","r");
    PyRun_SimpleFile(fd,"gw2craft");
    Py_Finalize();
    return 0;
}
