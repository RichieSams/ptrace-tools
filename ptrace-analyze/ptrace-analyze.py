#!/usr/bin/python

import sys
from threaddb import *

def reportProcInfo(threadDb):
    totalns = long(threadDb.threadRange()[1] - threadDb.threadRange()[0])
    totalSec = float(totalns) / float(1000000000)
    print 'Process execution time: %.04f seconds' % (totalSec)
    print 'Number of threads: %d' % (threadDb.numThreads())


def reportThreadInfo(threadDb):
    for tId in threadDb.threadIds():
        tRange = threadDb.threadRange(tId)
        stats = threadDb.threadWaitStats(tId)
        totaluSec = long(tRange[1] - tRange[0])
        print '---- Thread Stats for Thread ID: %s ----' % (tId)
        print 'Total run time of thread: %dns' % (totaluSec)
        print 'Average wait time: %dns' % (stats[0])
        print 'Max wait time: %dns' % (stats[1])
        print 'Thread waited %d percent of run time' % (stats[2])
        print 'Total thread wait time: %dns' % (stats[3])
        print ''

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file = open(sys.argv[1], mode="r")
        threaddb =  ThreadDB(file)
        file.close()
        print '--- process information ---'
        reportProcInfo(threaddb)
        print ''
        reportThreadInfo(threaddb)
        print ''
    else:
        print 'ptrace-analyze (c)2012 Ardavon Falls'
        print 'usage...'
        print 'ptrace-analyze <log file>'

        
