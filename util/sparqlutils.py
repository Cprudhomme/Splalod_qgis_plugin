from SPARQLWrapper import SPARQLWrapper, JSON, GET, POST, DIGEST
import urllib
import requests
import sys
from urllib.request import urlopen
import json
from qgis.core import Qgis, QgsGeometry
from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QSettings
from rdflib import Graph

MESSAGE_CATEGORY = "SPARQLUtils"


class SPARQLUtils:
    supportedLiteralTypes = {"http://www.opengis.net/ont/geosparql#wktLiteral": "wkt",
                             "http://www.opengis.net/ont/geosparql#gmlLiteral": "gml",
                             "http://www.opengis.net/ont/geosparql#wkbLiteral": "wkb",
                             "http://www.opengis.net/ont/geosparql#geoJSONLiteral": "geojson",
                             "http://www.opengis.net/ont/geosparql#kmlLiteral": "kml",
                             "http://www.opengis.net/ont/geosparql#dggsLiteral": "dggs"}

    classicon=QIcon(":/icons/resources/icons/class.png")
    geoclassicon=QIcon(":/icons/resources/icons/geoclass.png")
    instanceicon=QIcon(":/icons/resources/icons/instance.png")
    earthinstanceicon=QIcon(":/icons/resources/icons/earthinstance.png")

    @staticmethod
    def executeQuery(triplestoreurl, query,triplestoreconf=None):
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled")
        proxyType = s.value("proxy/proxyType")
        proxyHost = s.value("proxy/proxyHost")
        proxyPort = s.value("proxy/proxyPort")
        proxyUser = s.value("proxy/proxyUser")
        proxyPassword = s.value("proxy/proxyPassword")
        if proxyHost != None and proxyHost != "" and proxyPort != None and proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        QgsMessageLog.logMessage('Started task "{}"'.format(query), MESSAGE_CATEGORY, Qgis.Info)
        sparql = SPARQLWrapper(triplestoreurl)
        if triplestoreconf!=None and "userCredential" in triplestoreconf and triplestoreconf["userCredential"]!="" and "userPassword" in triplestoreconf and triplestoreconf["userPassword"] != None:
            sparql.setHTTPAuth(DIGEST)
            sparql.setCredentials(triplestoreconf["userCredential"], triplestoreconf["userPassword"])
        sparql.setQuery(query)
        QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
        sparql.setMethod(GET)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.queryAndConvert()
            if "status_code" in results:
                raise Exception
        except Exception as e:
            try:
                sparql = SPARQLWrapper(triplestoreurl,
                                       agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                sparql.setQuery(query)
                if triplestoreconf != None and "userCredential" in triplestoreconf and triplestoreconf["userCredential"] != "" and "userPassword" in triplestoreconf and triplestoreconf["userPassword"] != None:
                    sparql.setHTTPAuth(DIGEST)
                    sparql.setCredentials(triplestoreconf["userCredential"], triplestoreconf["userPassword"])
                sparql.setMethod(POST)
                sparql.setReturnFormat(JSON)
                results = sparql.queryAndConvert()
                if "status_code" in results:
                    raise Exception
            except:
                QgsMessageLog.logMessage("Exception: " + str(e), MESSAGE_CATEGORY, Qgis.Info)
                return False
        return results

    @staticmethod
    def invertPrefixes(prefixes):
        QgsMessageLog.logMessage("Invert Prefixes: " + str(prefixes), MESSAGE_CATEGORY, Qgis.Info)
        inv_map = {v: k for k, v in prefixes.items()}
        return inv_map

    @staticmethod
    def labelFromURI(uri,prefixlist=None):
        if "#" in uri:
            prefix=uri[:uri.rfind("#")+1]
            if prefixlist!=None and prefix in prefixlist:
                return str(prefixlist[prefix])+":"+str(uri[uri.rfind("#") + 1:])
            return uri[uri.rfind("#") + 1:]
        if "/" in uri:
            prefix=uri[:uri.rfind("/")+1]
            if prefixlist!=None and prefix in prefixlist:
                return str(prefixlist[prefix])+":"+str(uri[uri.rfind("/") + 1:])
            return uri[uri.rfind("/") + 1:]
        return uri

    @staticmethod
    def loadGraph(graphuri):
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled")
        proxyType = s.value("proxy/proxyType")
        proxyHost = s.value("proxy/proxyHost")
        proxyPort = s.value("proxy/proxyPort")
        proxyUser = s.value("proxy/proxyUser")
        proxyPassword = s.value("proxy/proxyPassword")
        if proxyHost != None and proxyHost != "" and proxyPort != None and proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        QgsMessageLog.logMessage('Started task "{}"'.format("Load Graph"), MESSAGE_CATEGORY, Qgis.Info)
        graph = Graph()
        try:
            if graphuri.startswith("http"):
                graph.load(graphuri)
            else:
                filepath = graphuri.split(".")
                result = graph.parse(graphuri, format=filepath[len(filepath) - 1])
        except Exception as e:
            QgsMessageLog.logMessage('Failed "{}"'.format(str(e)), MESSAGE_CATEGORY, Qgis.Info)
            # self.exception = str(e)
            return None
        return graph

    @staticmethod
    def detectLiteralType(literal):
        try:
            geom = QgsGeometry.fromWkt(literal)
            return "wkt"
        except:
            print("no wkt")
        try:
            geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
            return "wkb"
        except:
            print("no wkb")
        try:
            json.loads(literal)
            return "geojson"
        except:
            print("no geojson")
        return ""

    @staticmethod
    def handleURILiteral(uri):
        result = []
        if uri.startswith("http") and uri.endswith(".map"):
            try:
                f = urlopen(uri)
                myjson = json.loads(f.read())
                if "data" in myjson and "type" in myjson["data"] and myjson["data"]["type"] == "FeatureCollection":
                    features = myjson["data"]["features"]
                    for feat in features:
                        result.append(feat["geometry"])
                return result
            except:
                QgsMessageLog.logMessage("Error getting geoshape " + str(uri) + " - " + str(sys.exc_info()[0]))
        return None

    ## Executes a SPARQL endpoint specific query to find labels for given classes. The query may be configured in the configuration file.
    #  @param self The object pointer.
    #  @param classes array of classes to find labels for
    #  @param query the class label query
    @staticmethod
    def getLabelsForClasses(classes, query, triplestoreconf, triplestoreurl):
        result = {}
        # url="https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids="
        if "SELECT" in query:
            vals = "VALUES ?class { "
            for qid in classes:
                vals += qid + " "
            vals += "}\n"
            query = query.replace("%%concepts%%", vals)
            results = SPARQLUtils.executeQuery(triplestoreurl, query)
            if results == False:
                return result
            for res in results["results"]["bindings"]:
                result[res["class"]["value"]] = res["label"]["value"]
        else:
            url = triplestoreconf["classlabelquery"]
            i = 0
            qidquery = ""
            for qid in classes:
                if "Q" in qid:
                    qidquery += "Q" + qid.split("Q")[1]
                if (i % 50) == 0:
                    print(url.replace("%%concepts%%", qidquery))
                    myResponse = json.loads(requests.get(url.replace("%%concepts%%", qidquery)).text)
                    print(myResponse)
                    for ent in myResponse["entities"]:
                        print(ent)
                        if "en" in myResponse["entities"][ent]["labels"]:
                            result[ent] = myResponse["entities"][ent]["labels"]["en"]["value"]
                    qidquery = ""
                else:
                    qidquery += "|"
                i = i + 1
        return result
