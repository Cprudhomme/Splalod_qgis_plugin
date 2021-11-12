class StyleObject():

    pointStyle={}

    pointImage={}

    lineStringStyle={"stroke":{}}

    lineStringImage={}

    polygonStyle={"stroke":{},"fill":{}}

    polygonImage={}

    hatch={}

    lineStringImageStyle={}

    rasterStyle={}

    rasterColorMap={}

    styleName={}

    styleId={}

    styleDescription={}

    popupStyle={}

    textStyle={}

    conditions={}

    svgToCSS={"fill":"fillColor","stroke":"color","stroke-width":"weight","stroke-linejoin":"lineJoin"}

    cssToSVG={"fillColor":"fill","color":"stroke","weight":"stroke-width","lineJoin":"stroke-linejoin"}

    def toString(self):
        builder=""
        builder+="StyleObject [styleId=" + str(self.styleId) + ",\n styleName=\"" + str(self.styleName) + "\",\n"
        if self.pointStyle is not None:
            builder+=" pointStyle=" + str(self.pointStyle) + "\n"
        if self.pointImage is not None:
            builder+=" pointImage=" + str(self.pointImage)+"\n"
        if self.lineStringStyle is not None:
            builder+=" lineStringStyle=" + str(self.lineStringStyle)+"\n"
        if self.lineStringImage is not None:
            builder+=" lineStringImage=" + str(self.lineStringImage)+"\n"
        if self.polygonStyle is not None:
            builder+=" polygonStyle=" + str(self.polygonStyle)+"\n"
        if self.polygonImage is not None:
            builder+=" polygonImage=" + str(self.polygonImage)+"\n"
        if self.hatch is not None:
            builder+=" hatch=" + str(self.hatch)+"\n"
        if self.popupStyle is not None:
            builder+=" popupStyle=" + str(self.popupStyle)+"\n"
        if self.rasterColorMap is not None:
            builder+=" rasterColorMap=" + str(self.rasterColorMap)+"\n"
        builder+=" conditions: "+str(self.conditions)+"]"
        return builder

    def cssLiteralToXML(self,result,cssString):
        treemap={"Fill":{},"Stroke":{}}
        if ";" in cssString:
            for statement in cssString.split(";"):
                split = statement.split(":")
                if "stroke" in split[0]:
                    treemap["Stroke"][split[0]]=split[1]
                elif "fill" in split[0]:
                    treemap["Fill"][split[0]]=split[1]
            for key in treemap:
                try:
                    result+="<sld:"+key+">\n"
                    for keyy in treemap[key]:
                        result+="<sld:CssParameter name=\""+keyy+"\">\n"
                        result+="<ogc:Literal>"+treemap[key][keyy]+"</ogc:Literal>\n"
                        result+="</sld:CssParameter>\n"
                    result+="</sld:"+key+">\n"
                except:
                    print("exception")
        return result

    def toSLD(self,layername):
        builder="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        builder+="<sld:StyledLayerDescriptor xmlns=\"http://www.opengis.net/sld\" xmlns:ogc=\"http://www.opengis.net/ogc\" version=\"1.1.0\" xsi:schemaLocation=\"http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd\" xmlns:se=\"http://www.opengis.net/se\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
        builder+="<sld:NamedLayer>\n"
        builder+="<se:Name>"+str(layername)+"</se:Name>\n"
        builder+="<se:Description></se:Description>\n"
        builder+="<sld:UserStyle>\n"
        builder+="<sld:FeatureTypeStyle>\n"
        builder+="<sld:Rule>\n"
        if self.pointStyle:
            builder+="<sld:PointSymbolizer>\n"
            builder = self.cssLiteralToXML(builder, self.pointStyle)
            builder+="</sld:PointSymbolizer>\n"
        if self.polygonStyle:
            builder+="<sld:PolygonSymbolizer>\n"
            builder = self.cssLiteralToXML(builder, self.polygonStyle)
            builder+="</sld:PolygonSymbolizer>\n"
        builder += "</sld:Rule>\n"
        builder += "</sld:FeatureTypeStyle>\n"
        builder += "</sld:UserStyle>\n"
        builder += "</sld:NamedLayer>\n"
        builder += "</sld:StyledLayerDescriptor>"
        return builder
