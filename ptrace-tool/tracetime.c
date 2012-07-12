#include "tracetime.h"
/* -------- */
static tracetime gsEpoch;
/* -------- */
void traceTime_init(void) {
  clock_gettime(CLOCK_MONOTONIC, &gsEpoch);
}
/* -------- */
void traceTime_destroy(void) {
  /* DOES NOTHING */
}
/* -------- */
tracetime traceTime_currentTime(void) {
  tracetime delta, curTime;
  clock_gettime(CLOCK_MONOTONIC, &curTime);	
  if (curTime.tv_nsec < gsEpoch.tv_nsec) {
    delta.tv_sec = curTime.tv_sec - gsEpoch.tv_sec - 1;
    delta.tv_nsec = 1000000000 + curTime.tv_nsec - gsEpoch.tv_nsec;
  } else {
    delta.tv_sec = curTime.tv_sec - gsEpoch.tv_sec;
    delta.tv_nsec = curTime.tv_nsec - gsEpoch.tv_nsec;
  }
  return delta;
}
