#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
/* This is really a test of semaphore handling
   (sem_{init,destroy,post,wait}).  Using semaphores a barrier
   function is created.  Helgrind-3.3 (p.k.a Thrcheck) does understand
   the barrier semantics implied by the barrier, as pieced together
   from happens-before relationships obtained from the component
   semaphores.  However, it does falsely report one race.  Ah well.
   Helgrind-3.4 is pure h-b and so reports no races (yay!). */
/* This code is derived from
   gcc-4.3-20071012/libgomp/config/posix/bar.c, which is

   Copyright (C) 2005 Free Software Foundation, Inc.
   Contributed by Richard Henderson <rth@redhat.com>.

   and available under version 2.1 or later of the GNU Lesser General
   Public License.

   Relative to the libgomp sources, the gomp_barrier_t type here has
   an extra semaphore field, xxx.  This is not functionally useful,
   but it is used to create enough extra inter-thread dependencies
   that the barrier-like behaviour of gomp_barrier_t is evident to
   Thrcheck.  There is no other purpose for the .xxx field. */
static sem_t* my_sem_init(char*, int, unsigned);
static int my_sem_destroy(sem_t*);
static int my_sem_wait(sem_t*); static int my_sem_post(sem_t*);
typedef struct
{
  pthread_mutex_t mutex1;
  pthread_mutex_t mutex2;
  sem_t* sem1;
  sem_t* sem2;
  unsigned total;
  unsigned arrived;
  sem_t* xxx;
} gomp_barrier_t;

typedef long bool;

void
gomp_barrier_init (gomp_barrier_t *bar, unsigned count)
{
  pthread_mutex_init (&bar->mutex1, NULL);
  pthread_mutex_init (&bar->mutex2, NULL);
  bar->sem1 = my_sem_init ("sem1", 0, 0);
  bar->sem2 = my_sem_init ("sem2", 0, 0);
  bar->xxx  = my_sem_init ("xxx",  0, 0);
  bar->total = count;
  bar->arrived = 0;
}

void
gomp_barrier_destroy (gomp_barrier_t *bar)
{
  /* Before destroying, make sure all threads have left the barrier.  */
  pthread_mutex_lock (&bar->mutex1);
  pthread_mutex_unlock (&bar->mutex1);

  pthread_mutex_destroy (&bar->mutex1);
  pthread_mutex_destroy (&bar->mutex2);
  my_sem_destroy(bar->sem1);
  my_sem_destroy(bar->sem2);
  my_sem_destroy(bar->xxx);
}

void
gomp_barrier_reinit (gomp_barrier_t *bar, unsigned count)
{
  pthread_mutex_lock (&bar->mutex1);
  bar->total = count;
  pthread_mutex_unlock (&bar->mutex1);
}

void
gomp_barrier_wait (gomp_barrier_t *bar)
{
  unsigned int n;
  pthread_mutex_lock (&bar->mutex1);

  ++bar->arrived;

  if (bar->arrived == bar->total)
    {
      bar->arrived--;
      n = bar->arrived;
      if (n > 0) 
        {
          { unsigned int i;
            for (i = 0; i < n; i++)
              my_sem_wait(bar->xxx); // acquire an obvious dependency from
              // all other threads arriving at the barrier
          }
          // 1 up n times, 2 down once
          // now let all the other threads past the barrier, giving them
          // an obvious dependency with this thread.
          do
            my_sem_post (bar->sem1); // 1 up
          while (--n != 0);
          // and wait till the last thread has left
          my_sem_wait (bar->sem2); // 2 down
        }
      pthread_mutex_unlock (&bar->mutex1);
      /* "Resultats professionnels!"  First we made this thread have an
         obvious (Thrcheck-visible) dependency on all other threads
         calling gomp_barrier_wait.  Then, we released them all again,
         so they all have a (visible) dependency on this thread.
         Transitively, the result is that all threads leaving the
         barrier have a a Thrcheck-visible dependency on all threads
         arriving at the barrier.  As required. */
    }
  else
    {
      pthread_mutex_unlock (&bar->mutex1);
      my_sem_post(bar->xxx);
      // first N-1 threads wind up waiting here
      my_sem_wait (bar->sem1); // 1 down 

      pthread_mutex_lock (&bar->mutex2);
      n = --bar->arrived; /* XXX see below */
      pthread_mutex_unlock (&bar->mutex2);

      if (n == 0)
        my_sem_post (bar->sem2); // 2 up
    }
}


/* re XXX, thrcheck reports a race at this point.  It doesn't
   understand that bar->arrived is protected by mutex1 whilst threads
   are arriving at the barrier and by mutex2 whilst they are leaving,
   but not consistently by either of them.  Oh well. */

static gomp_barrier_t bar;

/* What's with the volatile here?  It stops gcc compiling
   "if (myid == 4) { unprotected = 99; }" and
   "if (myid == 3) { unprotected = 88; }" into a conditional
   load followed by a store.  The cmov/store sequence reads and
   writes memory in all threads and cause Thrcheck to (correctly)
   report a race, the underlying cause of which is that gcc is
   generating non threadsafe code.  

   (The lack of) thread safe code generation by gcc is currently a
   hot topic.  See the following discussions:
     http://gcc.gnu.org/ml/gcc/2007-10/msg00266.html
     http://lkml.org/lkml/2007/10/24/673
   and this is interesting background:
     www.hpl.hp.com/techreports/2004/HPL-2004-209.pdf
*/
static volatile long unprotected = 0;

void* child ( void* argV )
{
   long myid = (long)argV;
   //   assert(myid >= 2 && myid <= 5);

   /* First, we all wait to get to this point. */
   gomp_barrier_wait( &bar );

   /* Now, thread #4 writes to 'unprotected' and so becomes its
      owner. */
   if (myid == 4) {
      unprotected = 99;
   }

   /* Now we all wait again. */
   gomp_barrier_wait( &bar );

   /* This time, thread #3 writes to 'unprotected'.  If all goes well,
      Thrcheck sees the dependency through the barrier back to thread
      #4 before it, and so thread #3 becomes the exclusive owner of
      'unprotected'. */
   if (myid == 3) {
      unprotected = 88;
   }

   /* And just to be on the safe side ... */
   gomp_barrier_wait( &bar );
   return NULL;
}


int main (int argc, char *argv[])
{
   long i; int res;
   pthread_t thr[4];
   fprintf(stderr, "starting\n");

   gomp_barrier_init( &bar, 4 );

   for (i = 0; i < 4; i++) {
      res = pthread_create( &thr[i], NULL, child, (void*)(i+2) );
      assert(!res);
   }

   for (i = 0; i < 4; i++) {
      res = pthread_join( thr[i], NULL );
      assert(!res);
   }

   gomp_barrier_destroy( &bar );

   /* And finally here, the root thread can get exclusive ownership
      back from thread #4, because #4 has exited by this point and so
      we have a dependency edge back to the write it did. */
   fprintf(stderr, "done, result is %ld, should be 88\n", unprotected);

   return 0;
}







static sem_t* my_sem_init (char* identity, int pshared, unsigned count)
{
   sem_t* s;

#if defined(VGO_linux) || defined(VGO_solaris)
   s = malloc(sizeof(*s));
   if (s) {
      if (sem_init(s, pshared, count) < 0) {
	 perror("sem_init");
	 free(s);
	 s = NULL;
      }
   }
#elif defined(VGO_darwin)
   char name[100];
   sprintf(name, "anonsem_%s_pid%d", identity, (int)getpid());
   name[ sizeof(name)-1 ] = 0;
   if (0) printf("name = %s\n", name);
   s = sem_open(name, O_CREAT | O_EXCL, 0600, count);
   if (s == SEM_FAILED) {
      perror("sem_open");
      s = NULL;
   }
#else
#  error "Unsupported OS"
#endif

   return s;
}

static int my_sem_destroy ( sem_t* s )
{
   return sem_destroy(s);
}

static int my_sem_wait(sem_t* s)
{
  return sem_wait(s);
}

static int my_sem_post(sem_t* s)
{
  return sem_post(s);
}
