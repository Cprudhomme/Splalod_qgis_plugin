# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SPAQLunicornDialog
                                 A QGIS plugin
 This plugin adds a GeoJSON layer from a Wikidata SPARQL query.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-10-28
        git sha              : $Format:%H$
        copyright            : (C) 2019 by SPARQL Unicorn
        email                : rse@fthiery.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import re
import json
import sys
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtCore
from qgis.core import QgsProject,QgsMessageLog, Qgis
from qgis.PyQt.QtCore import QRegExp, QSortFilterProxyModel, Qt, QUrl
from qgis.PyQt.QtGui import QRegExpValidator, QStandardItemModel, QDesktopServices
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from qgis.PyQt.QtWidgets import QComboBox, QCompleter, QTableWidgetItem, QHBoxLayout, QPushButton, QWidget, \
    QAbstractItemView, QListView, QMessageBox, QApplication, QMenu, QAction
from rdflib.plugins.sparql import prepareQuery
from ..dialogs.whattoenrichdialog import EnrichmentDialog
from ..dialogs.convertcrsdialog import ConvertCRSDialog
from ..util.tooltipplaintext import ToolTipPlainText
from ..enrichmenttab import EnrichmentTab
from ..interlinkingtab import InterlinkingTab
from ..dialogs.triplestoredialog import TripleStoreDialog
from ..dialogs.triplestorequickadddialog import TripleStoreQuickAddDialog
from ..dialogs.searchdialog import SearchDialog
from ..util.sparqlhighlighter import SPARQLHighlighter
from ..dialogs.valuemappingdialog import ValueMappingDialog
from ..dialogs.bboxdialog import BBOXDialog
from ..dialogs.loadgraphdialog import LoadGraphDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/sparql_unicorn_dialog_base.ui'))

MESSAGE_CATEGORY = 'SPARQLUnicornDialog'
##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
class SPARQLunicornDialog(QtWidgets.QMainWindow, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None

    enrichtab = None

    interlinktab = None

    conceptList = None

    completerClassList = None

    columnvars = {}

    # menubar = None
    #
    # fileMenu = {}



    def __init__(self, triplestoreconf={}, prefixes=[], addVocabConf={}, autocomplete={},
                 prefixstore={"normal": {}, "reversed": {}}, savedQueriesJSON={}, maindlg=None, parent=None ):
        """Constructor."""
        super(SPARQLunicornDialog, self).__init__(parent)
        self.setupUi(self)

        # self.menuBar = menuBar
        self.prefixes = prefixes
        self.maindlg = maindlg
        self.savedQueriesJSON = savedQueriesJSON
        # self.enrichtab = EnrichmentTab(self)
        # self.interlinktab = InterlinkingTab(self)
        self.addVocabConf = addVocabConf
        self.autocomplete = autocomplete
        self.prefixstore = prefixstore
        self.triplestoreconf = triplestoreconf
        # self.searchTripleStoreDialog = TripleStoreDialog(self.triplestoreconf, self.prefixes, self.prefixstore,
        #                                                  self.comboBox)
        # self.geoTreeView.setHeaderHidden(True)
        # self.geoTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.geoTreeView.setAlternatingRowColors(True)
        # self.geoTreeView.setWordWrap(True)
        # self.geoTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.geoTreeView.customContextMenuRequested.connect(self.onContext)
        # self.geoTreeViewModel = QStandardItemModel()
        # self.geoTreeView.setModel(self.geoTreeViewModel)
        # self.featureCollectionClassListModel = QStandardItemModel()
        # self.geometryCollectionClassListModel = QStandardItemModel()
        # self.proxyModel = QSortFilterProxyModel(self)
        # self.proxyModel.sort(0)
        # self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        # self.proxyModel.setSourceModel(self.geoTreeViewModel)
        # self.featureCollectionProxyModel = QSortFilterProxyModel(self)
        # self.featureCollectionProxyModel.sort(0)
        # self.featureCollectionProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        # self.featureCollectionProxyModel.setSourceModel(self.featureCollectionClassListModel)
        # self.geometryCollectionProxyModel = QSortFilterProxyModel(self)
        # self.geometryCollectionProxyModel.sort(0)
        # self.geometryCollectionProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        # self.geometryCollectionProxyModel.setSourceModel(self.geometryCollectionClassListModel)
        # self.geoTreeView.setModel(self.proxyModel)
        # self.geoTreeViewModel.clear()
        # self.rootNode = self.geoTreeViewModel.invisibleRootItem()
        # self.featureCollectionClassList.setModel(self.featureCollectionProxyModel)
        # self.featureCollectionClassList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.featureCollectionClassList.setAlternatingRowColors(True)
        # self.featureCollectionClassList.setWordWrap(True)
        # self.featureCollectionClassList.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.featureCollectionClassList.customContextMenuRequested.connect(self.onContext)
        # self.featureCollectionClassListModel.clear()
        # self.geometryCollectionClassList.setModel(self.geometryCollectionProxyModel)
        # self.geometryCollectionClassList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.geometryCollectionClassList.setAlternatingRowColors(True)
        # self.geometryCollectionClassList.setWordWrap(True)
        # self.geometryCollectionClassList.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.geometryCollectionClassList.customContextMenuRequested.connect(self.onContext)
        # self.geometryCollectionClassListModel.clear()
        # self.queryLimit.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        # self.filterConcepts.textChanged.connect(self.setFilterFromText)
        # self.inp_sparql2 = ToolTipPlainText(self.tab, self.triplestoreconf, self.comboBox, self.columnvars,
        #                                     self.prefixes, self.autocomplete)
        # self.inp_sparql2.move(10, 130)
        # self.inp_sparql2.setMinimumSize(780, 431)
        # self.inp_sparql2.document().defaultFont().setPointSize(16)
        # self.inp_sparql2.setPlainText(
        #     "SELECT ?item ?lat ?lon WHERE {\n ?item ?b ?c .\n ?item <http://www.wikidata.org/prop:P123> ?def .\n}")
        # self.inp_sparql2.columnvars = {}
        # self.inp_sparql2.textChanged.connect(self.validateSPARQL)
        # self.sparqlhighlight = SPARQLHighlighter(self.inp_sparql2)
        # self.areaconcepts.hide()
        # self.areas.hide()
        # self.label_8.hide()
        # self.label_9.hide()
        # self.savedQueries.hide()
        # self.loadQuery.hide()
        # self.saveQueryButton.hide()
        # self.saveQueryName.hide()
        # self.savedQueryLabel.hide()
        # self.saveQueryName_2.hide()
        # self.enrichTableResult.hide()
        # self.queryTemplates.currentIndexChanged.connect(self.viewselectaction)
        # self.bboxButton.clicked.connect(self.getPointFromCanvas)
        # self.interlinkTable.cellClicked.connect(self.createInterlinkSearchDialog)
        # self.enrichTable.cellClicked.connect(self.createEnrichSearchDialog)
        # self.convertTTLCRS.clicked.connect(self.buildConvertCRSDialog)
        # self.chooseLayerInterlink.clear()
        # self.searchClass.clicked.connect(self.createInterlinkSearchDialog)
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        # self.interlinkNameSpace.setValidator(urlvalidator)
        # self.interlinkNameSpace.textChanged.connect(self.check_state3)
        # self.interlinkNameSpace.textChanged.emit(self.interlinkNameSpace.text())
        # self.addEnrichedLayerButton.clicked.connect(self.enrichtab.addEnrichedLayer)
        # self.startEnrichment.clicked.connect(self.enrichtab.enrichLayerProcess)
        # self.exportInterlink.clicked.connect(self.enrichtab.exportEnrichedLayer)
        # self.loadQuery.clicked.connect(self.loadQueryFunc)
        # self.saveQueryButton.clicked.connect(self.saveQueryFunc)
        # self.exportMappingButton.clicked.connect(self.interlinktab.exportMapping)
        # self.importMappingButton.clicked.connect(self.interlinktab.loadMapping)
        # self.loadLayerInterlink.clicked.connect(self.loadLayerForInterlink)
        # self.loadLayerEnrich.clicked.connect(self.loadLayerForEnrichment)
        # self.addEnrichedLayerRowButton.clicked.connect(self.addEnrichRow)
        # self.geoTreeView.selectionModel().currentChanged.connect(self.viewselectaction)
        # self.loadFileButton.clicked.connect(self.buildLoadGraphDialog)
        # self.refreshLayersInterlink.clicked.connect(self.loadUnicornLayers)
        # self.btn_loadunicornlayers.clicked.connect(self.loadUnicornLayers)
        # self.whattoenrich.clicked.connect(self.createWhatToEnrich)
        # self.quickAddTripleStore.clicked.connect(self.buildQuickAddTripleStore)
        # self.loadTripleStoreButton.clicked.connect(self.buildCustomTripleStoreDialog)
        #self.loadUnicornLayers()
        self.actionLoad_Graph.triggered.connect(self.buildLoadGraphDialog)

        ##
        #  @brief Creates a What To Enrich dialog with parameters given.
        #
        #  @param self The object pointer
    def buildLoadGraphDialog(self):
        self.searchTripleStoreDialog = LoadGraphDialog(self.triplestoreconf, self.maindlg, self)
        self.searchTripleStoreDialog.setWindowTitle("Load Graph")
        self.searchTripleStoreDialog.exec_()
# this part of code creates a menubar with an exit and file menu
        # exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        # exitAct.setShortcut('Ctrl+Q')
        # exitAct.setStatusTip('Exit application')
        # exitAct.triggered.connect(qApp.quit)
        #
        # menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAct)
        #
        # self.setGeometry(300, 300, 300, 200)
        # self.setWindowTitle('Simple menu')
        # self.show()
