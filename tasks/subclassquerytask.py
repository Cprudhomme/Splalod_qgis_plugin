import json
import requests
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel,QColor
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'SubClassQueryTask'

class SubClassQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, progress,dlg,treeNode,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.dlg=dlg
        self.graph=graph
        self.treeNode=treeNode
        self.amountoflabels = -1
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
        self.resultlist = []
        self.viewlist = []

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query)
        else:
            results=self.graph.query(self.query)
        if results==False:
            return False
        QgsMessageLog.logMessage('Started task "{}"'.format(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            self.viewlist.append(str(result["subclass"]["value"]))
        print(self.viewlist)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.viewlist), MESSAGE_CATEGORY, Qgis.Info)
        # self.layercount.setText("["+str(len(viewlist))+"]")
        if "classlabelquery" in self.dlg.triplestoreconf and self.dlg.triplestoreconf[
            "classlabelquery"] != "":
            labels = SPARQLUtils.getLabelsForClasses(self.viewlist, self.dlg.triplestoreconf["classlabelquery"],self.dlg.triplestoreconf,self.triplestoreurl)
            print(labels)
            self.amountoflabels = len(labels)
            i = 0
            sorted_labels = sorted(labels.items(), key=lambda x: x[1])
            for lab in sorted_labels:
                self.resultlist.append(labels[lab[0]] + " (" + lab[0] + ")")
                i = i + 1
        return True

    def finished(self, result):
        if len(self.resultlist) > 0:
            first = True
            for concept in self.resultlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(self.dlg.style().standardIcon(getattr(QStyle, "SP_ToolBarHorizontalExtensionButton")))
                self.treeNode.appendRow(item)
        elif len(self.viewlist) > 0:
            for concept in self.viewlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(self.dlg.style().standardIcon(getattr(QStyle, "SP_ToolBarHorizontalExtensionButton")))
                self.treeNode.appendRow(item)
        if self.amountoflabels != -1:
            self.layercount.setText("[" + str(self.amountoflabels) + "]")
