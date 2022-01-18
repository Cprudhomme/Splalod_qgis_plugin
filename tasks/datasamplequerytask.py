from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QLabel

MESSAGE_CATEGORY = 'DataSampleQueryTask'

class DataSampleQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,relation,column,row,triplestoreconf,tableWidget):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.column=column
        self.triplestoreconf=triplestoreconf
        self.row=row
        self.tableWidget=tableWidget
        self.concept=concept
        self.relation=relation
        self.queryresult={}
        self.encounteredtypes=set()

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.concept+" "+self.relation),MESSAGE_CATEGORY, Qgis.Info)
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        results = SPARQLUtils.executeQuery(self.triplestoreurl,"SELECT DISTINCT (COUNT(?val) as ?amount) ?val WHERE { ?con <"+typeproperty+"> <" + str(self.concept) + "> . ?con <"+str(self.relation)+"> ?val } GROUP BY ?val LIMIT 100",self.triplestoreconf)
        for result in results["results"]["bindings"]:
            #QgsMessageLog.logMessage('Started task "{}"'.format(result), MESSAGE_CATEGORY, Qgis.Info)
            self.queryresult[result["val"]["value"]]={}
            self.queryresult[result["val"]["value"]]["label"]=SPARQLUtils.labelFromURI(result["val"]["value"])
            self.queryresult[result["val"]["value"]]["amount"]=result["amount"]["value"]
            if "datatype" in result["val"]:
                self.queryresult[result["val"]["value"]]["datatype"]=result["val"]["datatype"]
                self.encounteredtypes.add(self.queryresult[result["val"]["value"]]["datatype"])
            else:
                self.encounteredtypes.add("http://www.w3.org/2001/XMLSchema#anyURI")
        return True

    def finished(self,result):
        resstring=""
        counter=1
        for res in self.queryresult:
            if "http" in res:
                resstring+="<a href=\""+str(res)+"\"><b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b></a> "
            elif "datatype" in self.queryresult[res]:
                resstring+="<a href=\""+str(self.queryresult[res]["datatype"])+"\"><b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b></a> "
            else:
                resstring+="<b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b> "
            if counter%5==0:
                resstring+="<br/>"
            counter+=1
        item = QLabel()
        item.setOpenExternalLinks(True)
        item.setText(resstring)
        self.tableWidget.takeItem(self.row,self.column)
        self.tableWidget.setCellWidget(self.row,self.column,item)
