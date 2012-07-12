#ifndef LOG_H
#define LOG_H
/* -------- */
void log_init(const char* pLogFile);
void log_destroy(void);
void log_processStart(void);
void log_processEnd(void);
void log_pThreadCreate(void);
void log_pThreadStart(void);
void log_pThreadEnd(void);
void log_pThreadLockEnter(void);
void log_pThreadLockLeave(void);
void log_pThreadUnlock(void);
void log_pThreadCondSignal(void);
void log_pThreadCondBroadcast(void);
void log_pThreadCondWaitEnter(void);
void log_pThreadCondWaitLeave(void);
void log_pThreadCondWaitTimeout(void);
/* -------- */
#endif /* #ifndef LOG_H */
