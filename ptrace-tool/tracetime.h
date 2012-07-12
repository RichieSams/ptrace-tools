#ifndef TRACETIME_H
#define TRACETIME_H
/* -------- */
#include <time.h>
/* -------- */
typedef struct timespec tracetime;
/* -------- */
void traceTime_init(void);
void traceTime_destroy(void);
tracetime traceTime_currentTime(void);
/* -------- */
#endif /* #ifndef TRACETIME_H */
