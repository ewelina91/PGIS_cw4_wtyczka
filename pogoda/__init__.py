# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pogoda
                                 A QGIS plugin
 pogoda
                             -------------------
        begin                : 2015-01-21
        copyright            : (C) 2015 by Ewelina
        email                : ewelina.j.mielczarek@gmail.com
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
    """Load pogoda class from file pogoda.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pogoda import pogoda
    return pogoda(iface)
