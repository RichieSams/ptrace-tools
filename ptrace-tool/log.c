#define _GNU_SOURCE
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <stdio.h>
#include "log.h"
#include "tracetime.h"
#define CSTR(X) #X
/* -------- */
enum {
  PROCESS_START = 0,
  PROCESS_END,
  PTHREAD_CREATE,
  PTHREAD_START,
  PTHREAD_END,
  PTHREAD_JOIN,
  PTHRAD_CANCEL,  
  PTHREAD_MUTEX_LOCK_ENTER,
  PTHREAD_MUTEX_LOCK_LEAVE,
  PTHREAD_MUTEX_UNLOCK,
  PTHREAD_COND_SIGNAL,
  PTHREAD_COND_BROADCAST,
  PTHREAD_COND_WAIT_ENTER,
  PTHREAD_COND_WAIT_LEAVE,
  PTHREAD_COND_WAIT_TIMEOUT,
  PTHREAD_MAX
};
/* -------- */
static FILE* gTrace = NULL;       /* output trace file */
/* -------- */
static void _logEvent(const char*);
/* -------- */
void 
log_init(const char* pLogFile) {
  if (NULL == (gTrace = fopen(pLogFile, "w"))) {
    fprintf(stderr, "pthread-trace: error opening logfile\n");
  } else {
    setvbuf(gTrace, NULL, _IOFBF, 1024 * 1024);
  }
}
/* -------- */
void 
log_destroy(void) {
  if (gTrace)
    fclose(gTrace);
}
/* -------- */
void 
log_processStart(void) {
  _logEvent(CSTR(PROCESS_START));
}
/* -------- */
void 
log_processEnd(void) {
  _logEvent(CSTR(PROCESS_END));
}
/* -------- */
void 
log_pThreadCreate(void) {
  _logEvent(CSTR(PTHREAD_CREATE));
}
/* -------- */
void 
log_pThreadStart(void) {
  _logEvent(CSTR(PTHREAD_START));
}
/* -------- */
void 
log_pThreadEnd(void) {
  _logEvent(CSTR(PTHREAD_END));
}
/* -------- */
void 
log_pThreadLockEnter(void) {
  _logEvent(CSTR(PTHREAD_MUTEX_LOCK_ENTER));
}
/* -------- */
void 
log_pThreadLockLeave(void) {
  _logEvent(CSTR(PTHREAD_MUTEX_LOCK_LEAVE));
}
/* -------- */
void 
log_pThreadUnlock(void) {
  _logEvent(CSTR(PTHREAD_MUTEX_UNLOCK));
}
/* -------- */
void 
log_pThreadCondSignal(void) {
  _logEvent(CSTR(PTHREAD_COND_SIGNAL));
}
/* -------- */
void 
log_pThreadCondBroadcast(void) {
  _logEvent(CSTR(PTHREAD_COND_BROADCAST));
}
/* -------- */
void 
log_pThreadCondWaitEnter(void) {
  _logEvent(CSTR(PTHREAD_COND_WAIT_ENTER));
}
/* -------- */
void 
log_pThreadCondWaitLeave(void) {
  _logEvent(CSTR(PTHREAD_COND_WAIT_LEAVE));
}
/* -------- */
void 
log_pThreadCondWaitTimeout(void) {
  _logEvent(CSTR(PTHREAD_COND_WAIT_TIMEOUT));
}
/* -------- */
static void
_logEvent(const char* pEvtName) {
  tracetime curTime = traceTime_currentTime();
  /*
  fprintf(stdout,
	  "%s %ld %ld:%ld\n", 
	  pEvtName, 
	  syscall(__NR_gettid), 
	  curTime.tv_sec,
	  curTime.tv_nsec);  
  */
  fprintf(gTrace,
	  "%s %ld %ld:%ld\n", 
	  pEvtName, 
	  syscall(__NR_gettid), 
	  curTime.tv_sec,
	  curTime.tv_nsec);
}
