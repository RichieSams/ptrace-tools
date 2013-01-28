#include "tracetime.h"

#if __APPLE__
#include <mach/mach_time.h>
#define CLOCK_MONOTONIC 0
int isInited = 0;
double conversion_factor = 0.0;
void clock_gettime(int bogus, tracetime* time)
{
    if (0 == isInited)
    {
        mach_timebase_info_data_t timebase;
        mach_timebase_info(&timebase);
        conversion_factor = (double)timebase.numer / (double)timebase.denom;
        isInited = 1;
    }

    double t = ((double)mach_absolute_time() * conversion_factor);

    time->tv_sec = (uint64_t)(((uint64_t)t) / 1000000000ULL);
    time->tv_nsec = (uint64_t)(((uint64_t)t) % 1000000000ULL);
}
#endif

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
