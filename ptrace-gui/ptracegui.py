#!/usr/bin/python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_ptracegui import *
from timeline import *
from threaddb import *
from piechart import *

class PTraceGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(PTraceGui, self).__init__(parent)
        self.setupUi(self)
        # add additional widgets
        self.threadDb = ThreadDB()
        self.timelineSlider = TimelineSlider(self.threadDb)
        self.timelineSliderLayout.addWidget(self.timelineSlider)
        self.timelineView = TimelineView(self.threadDb)
        self.timelineViewLayout.addWidget(self.timelineView)
        self.timelineView.setThreadColors(self.timelineSlider.getThreadColors())
        self.pieChart = Piechart();
        self.piechartLayout.addWidget(self.pieChart)
        # connect signals
        self.timelineSlider.selRangeChanged.connect(self.timelineView.updateRange)
        self.tIDComboBox.currentIndexChanged[str].connect(self.updateThreadStats)
        self.showEventsCheckBox.clicked.connect(self.threadEventsClicked)
        # object variables
        self._selectedThreadId = 0
        
    @pyqtSignature("")
    def on_actionOpen_triggered(self):
        filename = QFileDialog.getOpenFileName(
            self, "FileDialog",".log", "ptraces (*.log)")
        self.loadMap(filename)    
        
    @pyqtSignature("")
    def on_actionExit_triggered(self):
        self.close()
    
    def loadMap(self, filename):
        file = open(filename, mode="r")        
        self.threadDb = ThreadDB(file)
        file.close()
        self.timelineView.setThreadDB(self.threadDb)
        self.timelineSlider.setThreadDB(self.threadDb)
        self.timelineView.setThreadColors(self.timelineSlider.getThreadColors())
        # add all the thread ids to the combo box
        self.tIDComboBox.clear()
        for tid in self.threadDb.threadIds():            
            self.tIDComboBox.addItem(tid)
        
    @pyqtSlot('QString')
    def updateThreadStats(self, threadId):
        stats = self.threadDb.threadWaitStats(str(threadId))
        self.avgWaitTimeLabel.setText('%d ns' % (stats[0]))
        self.maxWaitTimeLabel.setText('%d ns' % (stats[1]))
        self.totalWaitTimeLabel.setText('%d ns' % (stats[3]))
        self.pieChart.setPercent(stats[2])
        self._selectedThreadId = str(threadId)
        self.timelineView.showThreadEvents(
            self.showEventsCheckBox.isChecked(), 
            str(threadId))

    @pyqtSlot('bool')
    def threadEventsClicked(self, checked):        
        self.timelineView.showThreadEvents(checked, self._selectedThreadId)
        
        
if __name__ == '__main__':            
    app = QApplication(sys.argv)
    mainWindow = PTraceGui()
    # load file if passed in as a command line argument
    if len(sys.argv) > 1:
        mainWindow.loadMap(sys.argv[1])
    # show windows and run app
    mainWindow.show()
    sys.exit(sys.exit(app.exec_()))

