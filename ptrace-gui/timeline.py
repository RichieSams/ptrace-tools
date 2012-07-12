import sys
import random
import time
import math
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from threaddb import *


class TimelineView(QWidget):
    BORDER_FACTOR = 0.03
    PEN_THICKNESS = 0.04
    THREAD_SPACE_FACTOR = 0.07
    NUM_GRIDMARKS = 10
    TCOLOR_LST = [
        QColor('green'), 
        QColor('darkRed'), 
        QColor('darkGreen'), 
        QColor('gray'),
        QColor('darkCyan'),
        QColor('darkGray')]
    
    def __init__(self, threadDb, parent = None):
        QWidget.__init__(self, parent)
        self._reset(threadDb)
        self._drawEvents = False
        self._tEventId = 0

    @pyqtSlot('unsigned long long', 'unsigned long long')
    def updateRange(self, startTime, endTime):
        self._startTime = startTime
        self._endTime = endTime
        self.repaint()

    def setThreadDB(self, threadDb):
        self._reset(threadDb)

    def showThreadEvents(self, enable, threadID=0):
        self._drawEvents = enable
        self._tEventId = threadID
        self.repaint()

    def _reset(self, threadDb):
        self._tDB = threadDb  
        self._calcScale(self.width(), self.height())
        self._colors = {}
        for tid in threadDb.threadIds():
            self._colors[tid] = random.choice(TimelineView.TCOLOR_LST)
        self._startTime = self._getRange()[0]
        self._endTime = self._getRange()[1]        

    def _calcScale(self, width, height):
        self._border = width * TimelineView.BORDER_FACTOR;
        self._penThick = height * TimelineView.PEN_THICKNESS
        self._threadSpace = height * TimelineView.THREAD_SPACE_FACTOR
    
    def _getRange(self):
        return self._tDB.threadRange(self._tDB.procId())    

    def _getDeltaTime(self):
        return self._endTime - self._startTime

    def _calcXFromUSec(self, usec):
        usecOffset = usec - self._startTime
        dblBorder = self._border * 2
        dsplWidth = (self.width() - dblBorder)
        deltaTime = self._getDeltaTime()
        return int(((usecOffset * dsplWidth) / deltaTime) + self._border)

    def _calcUSecFromX(self, x):
        dblBorder = self._border * 2
        dsplWidth = long((self.width() - dblBorder))
        deltaTime = long(self._getDeltaTime())
        return ((deltaTime * (x - self._border)) / dsplWidth) + self._startTime

    def _calcViewHeight(self):
        return self.height() - 20    
        
    def _getThreadViewRect(self):
        dblBorder = self._border * 2
        dsplWidth = long((self.width() - dblBorder))        
        return QRect(self._border, 0, dsplWidth, self._calcViewHeight()) 

    def _convertNanoSecToSec(self, ns, fracSz=2):
        sec = float(ns) / 1000000000.0
        rem = (ns - (sec * 1000000000)) / int(math.pow(10, 9 - fracSz))
        return '%.2f' % (sec)

    def _calcThreadRect(self, startEvt, endEvt, y):
        x1 = self._calcXFromUSec(startEvt[1])
        x2 = self._calcXFromUSec(endEvt[1])
        width = x2 - x1 if (x2-x1) > 0 else 1
        return QRect(x1, y - (self._penThick / 2), width, self._penThick)
        
    def _drawBackground(self, qpainter):
        # draw background color
        qpainter.setBrush(QBrush(QColor(240,240,240)))
        qpainter.drawRect(0,0, self.width(), self.height())
        # draw grid marks
        startTime = self._startTime
        endTime = self._endTime
        deltaTime = self._getDeltaTime()        
        yBottom = self._calcViewHeight()
        qpainter.setPen(QPen(QColor(150,150,150)))
        for t in range(startTime, endTime, deltaTime / 
                       TimelineView.NUM_GRIDMARKS):
            time = self._convertNanoSecToSec(t)
            xPos = self._calcXFromUSec(t)
            qpainter.drawLine(xPos, 0, xPos, yBottom)
            qpainter.drawText(xPos - 10, yBottom + 10, time)

    def _drawThreads(self, qpainter):
        nThreads = self._tDB.numThreads()
        viewHeight = self._calcViewHeight()
        y = (viewHeight - (nThreads * self._threadSpace)) / 2
        startTime = self._startTime
        endTime = self._endTime
        qpainter.setClipRect(self._getThreadViewRect())
        for tid in self._tDB.threadIds():
            threadlst = self._tDB.threadEvts(tid)            
            # draw thread run blocks
            qpainter.setPen(QPen(self._colors[tid], 1))
            qpainter.setBrush(self._colors[tid])
            startEvt = endEvt = None
            for evt in threadlst:
                if not startEvt:
                    if evt[0] == "START":
                        startEvt = evt
                else:
                    if evt[0] == "END":
                        endEvt = evt
                        rect = self._calcThreadRect(startEvt, endEvt, y)
                        #qpainter.drawRect(rect) 
                        qpainter.fillRect(rect, self._colors[tid])
                        startEvt = endEvt = None
            y += self._threadSpace
        qpainter.setClipRect(self.geometry())
        
    def _drawThreadLabels(self, qpainter):
        nThreads = self._tDB.numThreads()
        viewHeight = self._calcViewHeight()
        y = (viewHeight - (nThreads * self._threadSpace)) / 2
        for tid in self._tDB.threadIds():
            # draw thread ID text
            qpainter.setPen(QPen())
            qpainter.setFont(QFont('san-serif', 10))
            qpainter.drawText(self._border + 2, y + (self._penThick/3), 
                              'thread(%s)' %(tid))
            y += self._threadSpace
            
    def _drawThreadEvents(self, qpainter):
        hOffsetTbl= [0.14, 0.19, 0.24, 0.29]
        nThreads = self._tDB.numThreads()
        viewHeight = self._calcViewHeight()
        qpainter.setRenderHint(QPainter.Antialiasing, True)
        qpainter.setFont(QFont('san-serif', 7))
        qpainter.setClipRect(self._getThreadViewRect())
        if self._drawEvents:
            # find thread index
            tIndex = 0
            for tid in self._tDB.threadIds():
                if tid == self._tEventId:
                    break
                tIndex += 1
            # calculate y position
            y = (viewHeight - (nThreads * self._threadSpace)) / 2
            y += (self._threadSpace * tIndex)
            qpainter.setPen(QPen())
            threadlst = self._tDB.threadEvts(self._tEventId)  
            tIndex = 0
            for evt in threadlst:
                x = self._calcXFromUSec(evt[1])
                if ((tIndex & 0x8) == 8):
                    y2 = y + (viewHeight * hOffsetTbl[(tIndex & 0x3)])
                    qpainter.drawLine(x, y, x, y2)
                    qpainter.drawLine(x, y2, x + 10, y2 + 10)
                    qpainter.drawText(x + 10, y2 + 15, evt[2])
                else:
                    y2 = y - (viewHeight * hOffsetTbl[(tIndex & 0x3)])
                    qpainter.drawLine(x, y, x, y2)
                    qpainter.drawLine(x, y2, x + 10, y2 - 10)
                    qpainter.drawText(x + 10, y2 - 5, evt[2])
                tIndex += 1
        qpainter.setRenderHint(QPainter.Antialiasing, False)
        qpainter.setClipRect(self.geometry())                

    def paintEvent(self, evt):
        # don't draw if the range is 0
        if self._getRange()[1] == 0:
            return
        qpaint = QPainter()
        qpaint.begin(self)
        self._drawBackground(qpaint)
        self._drawThreads(qpaint)
        self._drawThreadLabels(qpaint)
        self._drawThreadEvents(qpaint)
        qpaint.end()

    def resizeEvent(self, event):
        size = event.size();
        self._calcScale(size.width(), size.height())
        self.repaint()
    
    def getThreadColors(self):
        return self._colors

    def setThreadColors(self, colors):
        self._colors = colors
                           

class TimelineSlider(TimelineView):
    #define signals
    selRangeChanged = pyqtSignal(['unsigned long long', 'unsigned long long'], name='selRangeChanged')

    def __init__(self, threadDb, parent = None):
        TimelineView.__init__(self, threadDb, parent)
        self._reset(threadDb)

    def _reset(self, threadDb):
        TimelineView._reset(self, threadDb)
        self._mouseGrab = None
        self._leftSlider = long(self._getRange()[0])
        self._rightSlider = long(self._getRange()[1])        
        
    def _calcSliderRect(self, x):
        yCenter = self._calcViewHeight() / 2
        return QRect(x - 3, yCenter - 12, 6, 24)

    def _calcLeftSliderRect(self):
        return self._calcSliderRect(self._calcXFromUSec(self._leftSlider))
    
    def _calcRightSliderRect(self):
        return self._calcSliderRect(self._calcXFromUSec(self._rightSlider))
    
    def _calcCoverRect(self):
        yBottom = self._calcViewHeight()
        x1 = self._calcXFromUSec(self._leftSlider)
        x2 = self._calcXFromUSec(self._rightSlider)
        return QRect(x1, 0, x2 - x1, yBottom)
        
    def _drawThreadLabels(self, qpainter):
        # we don't want thread labels on slider
        return

    def _drawSliderKnobs(self, qpainter):
        coverRect = self._calcCoverRect()
        yCenter = coverRect.height() / 2 
        qpainter.fillRect(coverRect, QColor(200, 200, 200, 140))
        # draw left knob
        knobRect = self._calcLeftSliderRect()
        knobPen = QPen(QColor(100,100,100), 1)
        knobGrad = QLinearGradient(
            QPointF(knobRect.topLeft()), 
            QPointF(knobRect.bottomRight()))
        knobGrad.setColorAt(0, QColor(220, 220, 220))
        knobGrad.setColorAt(1, QColor(130, 130, 130))
        knobBrush = QBrush(knobGrad)
        qpainter.setPen(knobPen)
        qpainter.setBrush(knobBrush)
        qpainter.drawRect(knobRect)
        qpainter.setPen(QPen(QColor(70,70,70)))
        qpainter.setBrush(QBrush(QColor(70,70,70)))
        qpainter.drawPolygon(
            QPoint(knobRect.left() + 1, yCenter), 
            QPoint(knobRect.right() - 2, yCenter - 3),
            QPoint(knobRect.right() - 2, yCenter + 3))
        # draw right knob
        knobRect = self._calcRightSliderRect()
        knobGrad = QLinearGradient(
            QPointF(knobRect.topLeft()), 
            QPointF(knobRect.bottomRight()))
        knobGrad.setColorAt(0, QColor(220, 220, 220))
        knobGrad.setColorAt(1, QColor(130, 130, 130))
        knobBrush = QBrush(knobGrad)
        qpainter.setPen(knobPen)
        qpainter.setBrush(knobBrush)
        qpainter.drawRect(knobRect)
        qpainter.setPen(QPen(QColor(70,70,70)))
        qpainter.setBrush(QBrush(QColor(70,70,70)))
        qpainter.drawPolygon(
            QPoint(knobRect.left() + 2, yCenter - 3), 
            QPoint(knobRect.left() + 2, yCenter + 3),
            QPoint(knobRect.right() - 1, yCenter))

    def paintEvent(self, evt):
        # don't draw if the range is 0
        if self._getRange()[1] == 0:
            return
        TimelineView.paintEvent(self, evt)
        qpaint = QPainter()
        qpaint.begin(self)
        self._drawSliderKnobs(qpaint)
        qpaint.end()
    
    def mousePressEvent(self, evt):
        lftKnobRect = self._calcLeftSliderRect()
        rhtKnobRect = self._calcRightSliderRect()
        viewRect = self._calcCoverRect()
        if lftKnobRect.contains(evt.pos()):
            self._mouseGrab = 'leftSlider'
        elif rhtKnobRect.contains(evt.pos()):
            self._mouseGrab = 'rightSlider'
        elif viewRect.contains(evt.pos()):
           self._mouseGrab = 'selectionView'
           self._lastMouseLoc = self._calcUSecFromX(evt.x())
    
    def mouseMoveEvent(self, evt):
        tRange = self._getRange()
        if self._mouseGrab == 'leftSlider':
            nleft = self._calcUSecFromX(evt.x())
            if nleft < self._rightSlider and tRange[0] <= nleft:
                self._leftSlider = long(nleft)
                self.repaint()
                self.selRangeChanged.emit(
                    long(self._leftSlider), 
                    long(self._rightSlider))
        elif self._mouseGrab == 'rightSlider':
            nright = self._calcUSecFromX(evt.x())
            if nright > self._leftSlider and tRange[1] >= nright:
                self._rightSlider = long(nright)
                self.repaint()
                self.selRangeChanged.emit(
                    long(self._leftSlider), 
                    long(self._rightSlider))
        elif self._mouseGrab == 'selectionView':
            diff = self._calcUSecFromX(evt.x()) - self._lastMouseLoc
            self._lastMouseLoc = self._calcUSecFromX(evt.x())
            nright = self._rightSlider + diff
            nleft = self._leftSlider + diff
            if tRange[0] <= nleft and tRange[1] >= nright:
                self._leftSlider = nleft
                self._rightSlider = nright
                self.repaint()
                self.selRangeChanged.emit(
                    long(self._leftSlider), 
                    long(self._rightSlider))
                

    def mouseReleaseEvent(self, evt):
        self._mouseGrab = None

    def SelRange(self):
        return (self._leftSlider, self._rightSlider)
        
if __name__ == "__main__":
    file = open(sys.argv[1], mode="r")
    tdb = ThreadDB(file)
    file.close()
    process = tdb.threadEvts(tdb.procId())
    app = QApplication(sys.argv)    
    tls = TimelineSlider(tdb)
    tlv = TimelineView(tdb)
    tlv.setThreadColors(tls.getThreadColors())

    tls.selRangeChanged.connect(tlv.updateRange)

    tls.show()
    tlv.show()

    sys.exit(app.exec_())
    
    
