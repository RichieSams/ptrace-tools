class ThreadDB:
    startEvt = [
        'PROCESS_START', 
        'PTHREAD_START', 
        'PTHREAD_MUTEX_LOCK_LEAVE', 
        'PTHREAD_COND_WAIT_LEAVE',
        'PTHREAD_COND_WAIT_TIMEOUT']
    endEvt = [
        'PROCESS_END',
        'PTHREAD_END',
        'PTHREAD_MUTEX_LOCK_ENTER',
        'PTHREAD_COND_WAIT_ENTER']
    markEvt = [
        'PTHREAD_CREATE',
        'PTHREAD_JOIN',
        'PTHRAD_CANCEL',
        'PTHREAD_MUTEX_UNLOCK',
        'PTHREAD_COND_SIGNAL',
        'PTHREAD_COND_BROADCAST']
    
    def __init__(self, strm = None):
        self.tDB = {}
        if strm:
            for line in strm:
                record = line.strip("\n").split(" ")
                self._addEvent(record[1], record[0], record[2])
    
    def _addEvent(self, tid, event, time):
        # add tid if it does not exist
        if tid not in self.tDB:
            self.tDB[tid] = []
        # convert time string to a usec value
        uSec = self._calcUSec(time)
        # add record to thread db
        thread = self.tDB[tid]
        if event in ThreadDB.startEvt:   
            thread.append(("START", uSec, event))
        elif event in ThreadDB.endEvt:
            thread.append(("END", uSec, event))
        elif event in ThreadDB.markEvt:
            thread.append(("MARK", uSec, event))
        return

    def _calcUSec(self, time):
        sec_usec = time.split(':')
        return (long(sec_usec[0]) * 1000000000L) + long(sec_usec[1])

    def threadRange(self, tId=None):
        startTime = 0
        endTime = 0
        # if no thread id was selected, then use the process's tID
        if not tId:
            tId = self.procId()
        # find first and last events
        if tId in self.tDB:
            timeline = self.tDB[tId]
            startTime = timeline[0][1]
            endTime = timeline[-1][1]
        return (startTime, endTime)

    def threadIds(self):
        return tuple([tId for tId in self.tDB])

    def procId(self):
        for tid, timeline in self.tDB.items():
            if timeline[0][2] == ThreadDB.startEvt[0]:
                return tid
        return None

    def threadEvts(self, tId):
        return self.tDB[tId]
                        
    def numThreads(self):
        return len(self.tDB)

    def threadWaitStats(self, tId):
        tEvents = self.tDB[tId]
        # calculate average, max and number of waits
        nWaits = totalWait = maxWait = 0
        sTime = eTime = None
        maxSTime = maxETime = None
        for evt in tEvents:
            if not eTime:
                if evt[0] == "END":
                    eTime = evt
            else:
                if evt[0] == "START":                    
                    sTime = evt
                    waitTime = (sTime[1] - eTime[1])
                    if maxWait < waitTime:
                        maxWait = waitTime
                        maxSTime = sTime
                        maxETime = eTime
                    totalWait += waitTime
                    nWaits += 1
                    eTime = None
                    sTime = None
        avgWaitTime = (totalWait / nWaits)
        # calculate wait time as a percentage of thread time
        tRange = self.threadRange(tId)
        waitPct= float(totalWait * 100.0) / float(tRange[1] - tRange[0])
        return (avgWaitTime, maxWait, waitPct, totalWait)
    
                    
