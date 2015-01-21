# -*- coding: cp1250 -*-

"""
/***************************************************************************
 pogoda
                                 A QGIS plugin
 pogoda
                              -------------------
        begin                : 2015-01-21
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Ewelina
        email                : ewelina.j.mielczarek@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QVariant
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from pogoda_dialog import pogodaDialog
import os.path
import qgis.utils
from qgis.gui import QgsMessageBar

import urllib, json
import datetime
from pprint import pprint

class pogoda:
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
            'pogoda_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = pogodaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Prognoza pogody OpenWeatherMap')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'pogoda')
        self.toolbar.setObjectName(u'pogoda')

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
        return QCoreApplication.translate('pogoda', message)


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
        qgis.utils.iface.messageBar().pushMessage('Informacja', 'Wtyczka pokazujaca aktualna mape pogody pobrana z serwisu OpenWeatherMap', level = QgsMessageBar.INFO, duration = 10)
        
        icon_path = ':/plugins/pogoda/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Prognoza pogody'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Prognoza pogody z serwisu OpenWeatherMap'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            

            #wczytywanie wojewodztw
            wojewodztwa= QgsVectorLayer('C:/Users/Ewcia/.qgis2/python/plugins/pogoda/shapefile/admin_region_teryt_woj.shp','wojewodztwa','ogr')
            #QgsMapLayerRegistry.instance().addMapLayer(wojewodztwa)
            #wczytywanie warstwy z informacjami o pogodzie
            wPogoda = QgsVectorLayer('Point', 'pogoda', 'memory')
            wPogoda.LayerData = wPogoda.dataProvider()
            wPogoda.startEditing()
            #wPogoda2.setCrs(QgsCoordinateReferenceSystem(4326))
                    
                        
            #dodawanie nowych pol
            wPogoda.LayerData.addAttributes([QgsField('Miasto', QVariant.String), QgsField('Temp', QVariant.Int), QgsField('TempMin', QVariant.Int), QgsField('TempMax', QVariant.Int), QgsField('Cisnienie', QVariant.Double), QgsField('Wilgotnosc', QVariant.Double), QgsField('PredkoscWiatru', QVariant.Double), QgsField('KierunekWiatru', QVariant.Double), QgsField('Chmury', QVariant.Int)])
            wPogoda.updateFields()
            wPogoda.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(wPogoda)

            if os.path.exists('wroc.json'):
                aktualnyCzas = datetime.datetime.now()
                print aktualnyCzas, 'aktualny czas'
                        
            #sprawdzanie czasu z pliku
                czasPlikuSys = os.path.getmtime('wroc.json')
                print czasPlikuSys, 'czas pliku systemowego'
                czasPliku=datetime.datetime.fromtimestamp(czasPlikuSys)
                print czasPliku, ' czas pliku'

                roznicaCzasow = (aktualnyCzas - czasPliku).seconds
                print roznicaCzasow, 'roznica czasow w sek'
                
                if roznicaCzasow<100:
                    print "Import z pliku"
                    with open ('wroc.json', 'w') as current:
                        plik = json.load(current)
                
                else:
                    print "Pobieranie danych z serwisu OWM"
                    #URL
                    request ='http://api.openweathermap.org/data/2.5/group?units=metric&id=3096053,3081368,3093692,3097257,3102987,3082707,3099828,3084093,3092931,3103096,3090205,3083103,3084404,3080231,3090170,3097367,3099213'
                    #print request

                    #drukuje plik json
                    wroc2 = urllib.urlopen(request)
                    plik = json.load(wroc2)
                    with open("wroc.json", 'w') as update:
                        mf = json.dump(plik, update)
                        #print plik
                        wroc2.close()
                            
                    #pprint(plik)
                        
            else:
                print "Nie znaleziono pliku na dysku. Dane pobrane z OWM"
                #URL
                request ='http://api.openweathermap.org/data/2.5/group?units=metric&id=3096053,3081368,3093692,3097257,3102987,3082707,3099828,3084093,3092931,3103096,3090205,3083103,3084404,3080231,3090170,3097367,3099213'
                #print request

                #drukuje plik json
                wroc2 = urllib.urlopen(request)
                plik = json.load(wroc2)
                with open("wroc.json", 'r') as update:
                    mf = json.dump(plik, update)
                    #print plik
                    wroc2.close()
                            
                #pprint(plik)   
                    
                    
            #tabela informacji o pogodzie
            pogoda = plik["list"]
            # pprint(pogoda)

            #pierwszy obiekt
            wrocek = pogoda[0]
            #print wr

            #zapisywanie danych do tabeli
            prognozaPog = []
            miasta = []
            miastoLat = []
            dict = {}

            for i in range(0, len(pogoda)):
                miasto = pogoda[i]['name']
                wspLat = pogoda[i]['coord']['lat']
                wspLon = pogoda[i]['coord']['lon']
                temp = pogoda[i]['main']['temp']
                tempMax = pogoda[i]['main']['temp_max']
                tempMin = pogoda[i]['main']['temp_min']
                cisnienie = pogoda[i]['main']['pressure']
                wilgotnosc = pogoda[i]['main']['humidity']
                predkoscWiatru = pogoda[i]['wind']['speed']
                kierunekWiatru = pogoda[i]['wind']['deg']
                chmury = pogoda[i]['clouds']['all']
            # opisPogody = pogoda[i]['weather']['desciption']
            #ikonaPogody = pogoda[i]['weather']['main']
                            

                prognozaDict = [miasto,temp,tempMax,tempMin,cisnienie,wilgotnosc,predkoscWiatru,kierunekWiatru,chmury]
                prognozaPog.append(prognozaDict)

                miastaWsp = [wspLon, wspLat]
                        
                miasta.append(miasto)
                miastoLat.append(miastaWsp)
                       
            #wpisywanie wspolrzednych
                dict[miasta[i]] = miastoLat[i]
            #for i in prognozaPog:
            #    print prognozaPog
            #print miasta
            #print miastoLat
            #print dict

                    
            #Dodawanie atrybutow obiektow
            wPogoda.startEditing()
            for i in range(0, len(pogoda)):
                obiekt = QgsFeature()
                obiekt.setGeometry(QgsGeometry.fromPoint(QgsPoint(wspLat, wspLon)))
                obiekt.setAttributes(prognozaPog[i])
                wPogoda.addFeature(obiekt)
            wPogoda.commitChanges()
            wPogoda.updateExtents()
            #QgsMapLayerRegistry.instance().addMapLayer(wPogoda)

