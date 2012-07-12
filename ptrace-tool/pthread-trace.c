#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>
#include <sys/types.h>
#include <unistd.h>
#include "tracetime.h"
#include "log.h"
/* -------- */
#define TRACEFILE   "ptrace.log"
/* -------- */
typedef struct {
  void* (*m_threadFunc)(void*);
  void* m_pCtx;
} pth_funcWrap;
/* -------- */
/* wrapping functions */
static int (*pthread_create_std)(pthread_t*, const pthread_attr_t*, void*(*func)(void*), void*);
static int (*pthread_mutex_init_std)(pthread_mutex_t*, const pthread_mutexattr_t*);
static int (*pthread_mutex_destroy_std)(pthread_mutex_t*);
static int (*pthread_mutex_lock_std)(pthread_mutex_t*);
static int (*pthread_mutex_trylock_std)(pthread_mutex_t*);
static int (*pthread_mutex_unlock_std)(pthread_mutex_t*);
static int (*pthread_cond_init_std)(pthread_cond_t*, const pthread_condattr_t*);
static int (*pthread_cond_destroy_std)(pthread_cond_t*);
static int (*pthread_cond_signal_std)(pthread_cond_t*);
static int (*pthread_cond_broadcast_std)(pthread_cond_t*);
static int (*pthread_cond_wait_std)(pthread_cond_t*, pthread_mutex_t*);
static int (*pthread_cond_timedwait_std)(pthread_cond_t*, pthread_mutex_t*, const struct timespec*);
/* -------- */
static void* _threadFuncWrap(void*);
static void _threadFuncEndTrap(void*);
/* -------- */
void __attribute__ ((constructor))
pthreadTrace_init(void) {
  /* notify user of usage */
  printf("pthread-trace (c)2012 QVXLabs LLC all rights reserved\n");
  /* load std calls */
  pthread_create_std = dlsym(RTLD_NEXT, "pthread_create");
  pthread_mutex_init_std = dlsym(RTLD_NEXT, "pthread_mutex_init");
  pthread_mutex_destroy_std = dlsym(RTLD_NEXT, "pthread_mutex_destroy");
  pthread_mutex_lock_std = dlsym(RTLD_NEXT, "pthread_mutex_lock");
  pthread_mutex_trylock_std = dlsym(RTLD_NEXT, "pthread_mutex_trylock");
  pthread_mutex_unlock_std = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
  pthread_cond_init_std = dlsym(RTLD_NEXT, "pthread_cond_init");
  pthread_cond_destroy_std = dlsym(RTLD_NEXT, "pthread_cond_destroy");
  pthread_cond_signal_std = dlsym(RTLD_NEXT, "pthread_cond_signal");
  pthread_cond_broadcast_std = dlsym(RTLD_NEXT, "pthread_cond_broadcast");
  pthread_cond_wait_std = dlsym(RTLD_NEXT, "pthread_cond_wait");
  pthread_cond_timedwait_std = dlsym(RTLD_NEXT, "pthread_cond_timedwait");
  /* init engine */
  traceTime_init();
  log_init(TRACEFILE);
  /* log process start */
  log_processStart();
}
/* -------- */
void __attribute__ ((destructor))
pthreadTrace_destroy(void) {
  printf("shutting down pthread-trace\n");
  log_processEnd();
  /* shutdown engine */
  log_destroy();
  traceTime_destroy();
}
/* -------- */
int 
pthread_create(
	       pthread_t* pThread, 
	       const pthread_attr_t* pAttr, 
	       void*(*func)(void*), 
	       void* pArg) {
  /* allcoate wrap ctx */
  pth_funcWrap* pWrap = malloc(sizeof(pth_funcWrap));
  pWrap->m_threadFunc = func;
  pWrap->m_pCtx = pArg;
  /* log creation and create thread */
  log_pThreadCreate();
  return pthread_create_std(pThread, pAttr, _threadFuncWrap, pWrap);
}
/* -------- */
int pthread_mutex_init(
		       pthread_mutex_t* pMtx, 
		       const pthread_mutexattr_t* pAttr) {
  return pthread_mutex_init_std(pMtx, pAttr);
}
/* -------- */
int pthread_mutex_destroy(pthread_mutex_t* pMtx) {
  return pthread_mutex_destroy_std(pMtx);
}
/* -------- */
int pthread_mutex_lock(pthread_mutex_t* pMtx) {
  int retVal;
  log_pThreadLockEnter();
  retVal = pthread_mutex_lock_std(pMtx);
  log_pThreadLockLeave();
  return retVal;
}
/* -------- */
int pthread_mutex_trylock(pthread_mutex_t* pMtx) {
  int retVal = pthread_mutex_trylock_std(pMtx);
  if (!retVal) {
    log_pThreadLockEnter();
    log_pThreadLockLeave();
  }
  return retVal;
}
/* -------- */
int pthread_mutex_unlock(pthread_mutex_t* pMtx) {
  log_pThreadUnlock();
  return pthread_mutex_unlock_std(pMtx);
}
/* -------- */
int pthread_cond_init(pthread_cond_t* pCnd, const pthread_condattr_t* pAttr) {
  return pthread_cond_init_std(pCnd, pAttr);
}
/* -------- */
int pthread_cond_destroy(pthread_cond_t* pCnd) {
  return pthread_cond_destroy_std(pCnd);
}
/* -------- */
int pthread_cond_signal(pthread_cond_t* pCnd) {
  log_pThreadCondSignal();
  return pthread_cond_signal_std(pCnd);
}
/* -------- */
int pthread_cond_broadcast(pthread_cond_t* pCnd) {
  log_pThreadCondBroadcast();
  return pthread_cond_broadcast_std(pCnd);
}
/* -------- */
int pthread_cond_wait(pthread_cond_t* pCnd, pthread_mutex_t* pMtx) {
  int retVal;
  log_pThreadCondWaitEnter();
  log_pThreadUnlock();
  retVal = pthread_cond_wait_std(pCnd, pMtx);
  log_pThreadLockEnter();
  log_pThreadCondWaitLeave();
  return retVal;
}
/* -------- */
int pthread_cond_timedwait(
			   pthread_cond_t* pCnd, 
			   pthread_mutex_t* pMtx, 
			   const struct timespec* pTnSpec) {
  int retVal;
  log_pThreadCondWaitEnter();
  log_pThreadUnlock();
  retVal = pthread_cond_timedwait_std(pCnd, pMtx, pTnSpec);
  log_pThreadLockEnter();
  if (ETIMEDOUT == retVal) 
    log_pThreadCondWaitTimeout();
  else
    log_pThreadCondWaitLeave();
  return retVal;
}
/* -------- */
static void*
_threadFuncWrap(void* pUser) {
  void *pRetVal = NULL;
  pth_funcWrap tWrp = *((pth_funcWrap*)pUser);
  free(pUser);
  /* push custom clean up func to trap thrad end */
  pthread_cleanup_push(_threadFuncEndTrap, NULL);
  /* log start */
  log_pThreadStart();
  /* run users thread */
  pRetVal = tWrp.m_threadFunc(tWrp.m_pCtx);
  /* clean up */
  pthread_cleanup_pop(1);
  return pRetVal;
}
/* -------- */
static void
_threadFuncEndTrap(void* pCtx) {
  log_pThreadEnd();
}
