# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SPAQLunicorn
                                 A QGIS plugin
 This plugin adds a GeoJSON layer from a Wikidata SPARQL query.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-10-28
        copyright            : (C) 2019 by SPARQL Unicorn
        email                : rse@fthiery.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SPAQLunicorn class from file SPAQLunicorn.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .sparql_unicorn import SPARQLunicorn
    return SPARQLunicorn(iface)
