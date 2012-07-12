import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Piechart(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self._percent = 70
        self._border = 20
        self._pieHeight = 0.04
        self._sliceXOffset = 0.03
        self._sliceYOffset = 0.03

    def _calcRect(self, xoffset=0, yoffset=0):
        x = self._border + xoffset
        y = self._border + yoffset
        wdgWidth = self.width()
        if wdgWidth > 400:
            wdgWidth = 400
        width = (wdgWidth / 2 )- (self._border * 2)
        height = width *.4            
        return QRect(x, y, width, height)

    def _calcPercentRange(self):
        rng = int((5760.0 * (100.0 - self._percent)) / 100.0)
        return (rng, 5760 - rng)

    def _calcPieHeight(self):
        pH = int(self.width() * self._pieHeight)
        if pH > 16:
            pH = 16
        return pH

    def _createGradient(self, baseColor):
        pieRect = self._calcRect()
        marginx = pieRect.width() * 0.1
        marginy = pieRect.height() * 0.1
        endX = pieRect.x() + (pieRect.width() - marginx)
        p1 = QPointF(pieRect.x() + marginx, marginy)
        p2 = QPointF(endX, marginy)
        gradient = QLinearGradient()
        gradient.setStart(p1)
        gradient.setFinalStop(p2)
        gradient.setColorAt(0, baseColor.lighter(30))
        gradient.setColorAt(1, baseColor.lighter(120))
        return gradient
    
    def _calcKeyRect(self, yoffset=0):
        rect = self._calcRect()
        x = rect.x() + rect.width() + 25
        y = rect.y() + 10 + yoffset
        return QRect(x, y, 15, 15)
    def paintEvent(self, evt):
        color1 = QColor('green')
        color1Edge = QColor('darkGreen')
        color2 = QColor('red')
        color2Edge = QColor('darkRed')
        qpaint = QPainter()
        qpaint.begin(self)        
        qpaint.setPen(QPen(Qt.NoPen))
        qpaint.setRenderHint(QPainter.Antialiasing, True)
        # draw 3d pie
        fillRng = self._calcPercentRange();        
        grad1Edge = self._createGradient(color1Edge)
        grad2Edge = self._createGradient(color2Edge)
        for y in range(self._calcPieHeight(), 0, -1):  
            qpaint.setBrush(QBrush(grad1Edge))
            qpaint.drawPie(self._calcRect(0,y),0, fillRng[0])
            qpaint.setBrush(QBrush(grad2Edge))
            qpaint.drawPie(self._calcRect(0,y),fillRng[0], fillRng[1])
        grad1 = self._createGradient(color1)
        grad2 = self._createGradient(color2)
        qpaint.setBrush(QBrush(grad1))
        qpaint.drawPie(self._calcRect(),0, fillRng[0])
        qpaint.setBrush(QBrush(grad2))
        xOffset= self.width() * self._sliceXOffset
        yOffset= self.height() * self._sliceYOffset
        qpaint.drawPie(self._calcRect(),fillRng[0], fillRng[1]) 
        #draw key
        qpaint.setBrush(color1)
        qpaint.setPen(QPen())
        item1 = self._calcKeyRect()
        qpaint.drawRect(item1)
        qpaint.drawText(item1.x() + 25, item1.y()+ 10, "percent running")
        qpaint.setBrush(color2)
        item2 = self._calcKeyRect(30)
        qpaint.drawRect(item2)
        qpaint.drawText(item2.x() + 25, item2.y()+ 10, "percent blocked")
        # draw stat
        pieRect = self._calcRect(0, self._calcPieHeight())
        qpaint.drawText(pieRect.x() + (pieRect.width() / 2) - 60, pieRect.y() + pieRect.height() + 30, "thread blocked %0.2f percent" % (self._percent))
        qpaint.end()

    def setPercent(self, percent):
        self._percent = percent
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)    
    chrt = Piechart()
    chrt.show()

    sys.exit(app.exec_())
