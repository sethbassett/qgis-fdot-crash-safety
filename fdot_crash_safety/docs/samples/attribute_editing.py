new_fields = source.fields()
new_fields.append(QgsField('overlap', QVariant.Double))
(sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            new_fields,
            source.wkbType(),
            source.sourceCrs()
)

Create a new feature and output

 new_feat = QgsFeature()
 new_feat.setGeometry(feature.geometry())
 new_feat.setFields(new_fields)
 new_feat['overlap'] = overlap
 sink.addFeature(new_feat, QgsFeatureSink.FastInsert)





    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        fields = QgsFields()
        fields.append(QgsField("Distance", QVariant.Int))
        fields.append(QgsField("Label", QVariant.String))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context, fields, source.wkbType(), source.sourceCrs())


        # Create a dictionary to hold the unique values from the 
        # dissolve_field and the sum of the values from the sum_field

        selection = source.getFeatures()
        for select in selection:
            geom = select.geometry()
            start_x = geom.asPoint().x()
            start_y = geom.asPoint().y()
            sides = 64
            radius = 6378137.0 # meters
            distance = [250, 500, 1000, 2000, 3000, 4000, 5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000]
            feedback.pushInfo('Creating layer and adding fields.')
            # Create new layer.
            vl = QgsVectorLayer("Polygon", "Distance Buffers", "memory")
            # Add fields.
            pr = vl.dataProvider()
            pr.addAttributes(fields)
            vl.updateFields()
            vl.startEditing()
            for i in range(len(distance)):
                feedback.pushInfo('Creating feature.')
                points = []
                dist = distance[i]
                degrees = 0
                while degrees <= 360:
                    degrees = degrees + 360 / sides
                    start_lon = start_x * pi / 180
                    start_lat = start_y * pi / 180
                    bearing = degrees * pi / 180
                    end_lat = asin((sin(start_lat) * cos(dist / radius)) + (cos(start_lat) * sin(dist / radius) * cos(bearing)))
                    end_lon = start_lon + atan2(sin(bearing) * sin(dist / radius) * cos(start_lat),
                                                cos(dist / radius) - (sin(start_lat) * sin(end_lat)))
                    points.append(QgsPointXY(end_lon * 180 / pi, end_lat * 180 / pi))
                    feat_name = str(distance[i])
                    if distance[i] < 1000:
                        label = str(distance[i]) + "m"
                    else:
                        label = str(distance[i]/1000) + "km"
                feedback.pushInfo('Adding feature to layer.')
                # Add calculated features.
                feat = QgsFeature()
                geometry = QgsGeometry.fromPolygonXY([points])
                feat.setGeometry(geometry)
                feat.setAttributes([feat_name,label])
                sink.addFeature(feat, QgsFeatureSink.FastInsert)
            vl.commitChanges()
            vl.updateExtents()
            #QgsProject.instance().addMapLayer(vl)

        return {self.OUTPUT: dest_id}