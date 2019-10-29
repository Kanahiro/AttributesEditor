from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayer

class CurrentLayer:
    def __init__(self, iface):
        self.iface = iface
        self.layer = iface.mapCanvas().currentLayer()

    def getFeature(self, id):
        return self.layer.getFeature(id)

    def getFeatures(self):
        if self.layer.type() != QgsMapLayer.VectorLayer:
            return []
        features = self.layer.getFeatures()
        return features

    def selectedFeatureIds(self):
        return self.layer.selectedFeatureIds()

    def focusFeatureOnMap(self, featureId):
        self.iface.mapCanvas().zoomToFeatureIds(self.layer, [featureId])

    def changeAttributeValues(self, featureId, changeValueDict):
        self.layer.startEditing()
        isSuccess = self.layer.changeAttributeValues(featureId, changeValueDict)
        self.layer.commitChanges()
        return isSuccess

    def removeSelection(self):
        self.layer.removeSelection()

    def selectByIds(self, ids):
        self.layer.selectByIds(ids)