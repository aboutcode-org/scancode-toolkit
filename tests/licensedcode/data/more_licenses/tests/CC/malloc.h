// EPOS-- Application-level Dynamic Memory Utility Declarations

// This work is licensed under the Creative Commons 
// Attribution-NonCommercial-NoDerivs License. To view a copy of this license, 
// visit http://creativecommons.org/licenses/by-nc-nd/2.0/ or send a letter to 
// Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.

#ifndef __malloc_h
#define __malloc_h

#include <utility/heap.h>

__BEGIN_SYS
extern Heap app_heap;
__END_SYS

inline void * malloc(unsigned int bytes) { 
    return __SYS(app_heap).alloc(bytes);
}
inline void * calloc(unsigned int n, unsigned int bytes) {
    return __SYS(app_heap).calloc(n * bytes); 
}
inline void * realloc(void * ptr, unsigned int bytes) {
    return __SYS(app_heap).realloc(ptr, bytes);
}
inline void free(void * ptr) {
    __SYS(app_heap).free(ptr); 
}

inline void * operator new(unsigned int bytes) {
    return __SYS(app_heap).alloc(bytes);
}
inline void * operator new[](unsigned int bytes) { 
    return __SYS(app_heap).alloc(bytes); 
}
inline void operator delete(void * object) {
    __SYS(app_heap).free(object);
}



#endif
