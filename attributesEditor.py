# -*- coding: utf-8 -*-
"""
/***************************************************************************
 attributesEditor
                                 A QGIS plugin
 Show simple property view of selected feature.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-08-17
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Kanahiro Iguchi
        email                : kanahiro.iguchi@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QSortFilterProxyModel, QModelIndex
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QTableView
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayer
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .attributesEditor_dockwidget import AttributesEditorDockWidget
import os.path

from .attributeModel import AttributeModel
from .currentLayer import CurrentLayer

class AttributesEditor:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AttributesEditor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Attributes Editor')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Attributes Editor')
        self.toolbar.setObjectName(u'Attributes Editor')

        #print "** INITIALIZING attributesEditor"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Attributes Editor', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/attributesEditor/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Attributes Editor'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING attributesEditor"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD attributesEditor"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Attributes Editor'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING attributesEditor"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = AttributesEditorDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            #init table
            currentLayer = CurrentLayer(self.iface)
            currentLayerFeatures = currentLayer.getFeatures()

            tableView = self.dockwidget.tableView
            self.initTableView(tableView, currentLayerFeatures)
            
            #signal
            self.iface.currentLayerChanged.connect(self.currentLayerChanged)
            #self.iface.mapCanvas().currentLayer().selectionChanged.connect(self.featureSelectionChanged)



    def initTableView(self, tableView, features):
        #currentLayerからすべての地物の属性、ID、ヘッダを取得してtableViewに渡す
        attributesList = []
        headers = []
        ids = []

        #1つめ（属性、ID、ヘッダ）
        for feature in features:
            attributesList.append(feature.attributes())
            ids.append(feature.id())
            headers = feature.fields().names()
            break

        #2つめ以降（属性、ID）
        for feature in features:
            attributesList.append(feature.attributes())
            ids.append(feature.id())
        
        attributeModel = AttributeModel(attributesList, headers, ids)
        attributeModel.dataChanged.connect(self.tableDataChanged)
        proxyModel = self.makeProxyModel(attributeModel)
        tableView.setModel(proxyModel)
        tableView.setCornerButtonEnabled(True)
        tableView.setSortingEnabled(True)

        verticalHeader = tableView.verticalHeader()
        tableView.pressed.connect(self.verticalHeaderClicked)
        verticalHeader.sectionClicked.connect(self.verticalHeaderClicked)
        verticalHeader.sectionDoubleClicked.connect(self.verticalHeaderDoubleClicked)

    #ソート機能のためのproxyModel
    def makeProxyModel(self, model):
        proxyModel = QSortFilterProxyModel()
        proxyModel.setDynamicSortFilter(True)
        proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
        proxyModel.setSourceModel(model)
        return proxyModel

    def verticalHeaderClicked(self, section):
        tableView = self.dockwidget.tableView
        selectedIndexes = tableView.selectedIndexes()

        currentLayer = CurrentLayer(self.iface)
        currentLayer.removeSelection()

        model = tableView.model()
        selectIds = []
        for index in selectedIndexes:
            featureId = model.headerData(index.row(), Qt.Vertical)
            selectIds.append(featureId)

        currentLayer.selectByIds(selectIds)
        

    def verticalHeaderDoubleClicked(self, section):
        tableView = self.dockwidget.tableView
        model = tableView.model()

        featureId = model.headerData(section, Qt.Vertical)
        currentLayer = CurrentLayer(self.iface)
        currentLayer.focusFeatureOnMap(featureId)

    def currentLayerChanged(self):
        tableView = self.dockwidget.tableView
        currentLayer = CurrentLayer(self.iface)
        features = currentLayer.getFeatures()
        self.initTableView(tableView, features)

    def tableDataChanged(self, index):
        featureId = index.row()
        fieldNum = index.column()
        value = index.data()

        currentLayer = CurrentLayer(self.iface)
        isSuccess = currentLayer.changeAttributeValues(featureId, {fieldNum:value})
        if not isSuccess:
            #失敗した時の処理
            print("falure")

    #unconnected
    def featureSelectionChanged(self):
        currentLayer = CurrentLayer(self.iface)
        selectedFeatureIds = currentLayer.selectedFeatureIds()
        
        tableView = self.dockwidget.tableView
        for id in selectedFeatureIds:
            tableView.selectRow(id)


    '''
    def featureSelected(self):
        currentLayer = CurrentLayer(self.iface)
        featureIds = currentLayer.getSelectedFeatureIds()
        selections = []

        tableView = self.dockwidget.tableView
        model = tableView.model()
        headerCount = model.rowCount()

        for featureId in featureIds:
            for i in range(headerCount):
                headerData = model.headerData(i, Qt.Vertical)
                if featureId == headerData:
                    selections.append(i)
        for selection in selections:
            tableView.selectRow(selection)
    '''