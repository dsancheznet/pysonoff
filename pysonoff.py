#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pySONOFF, a ewelink substitute for Linux by D.Sánchez
# This program is published under the EU-GPL, get your copy at
# https://joinup.ec.europa.eu/sites/default/files/custom-page/attachment/eupl_v1.2_en.pdf
# Based on the GTK3 Library in pyGObject for python and driven by the magnificent sonoff-python
# library by Lucien2K - https://github.com/lucien2k/sonoff-python
# You may have to install the dependencies from github. Please read the README file.

import gi, os, sonoff, configobj
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject

#Define a version number to be able to change it just in one place
global VERSION_NUMBER, WEB_PAGE
VERSION_NUMBER = "1.1"
WEB_PAGE="https://www.dsanchez.net/"

class MainWindow(Gtk.Window):
    """
        This class defines the main window of the application
    """
    def __init__(self):
        #Instantiate config file parser
        self.cConfig = configobj.ConfigObj( os.path.expanduser("~")+'/.config/sonoff/default.config')
        #-----------------------------------------------------------Construct UI
        #Configure Main Window
        Gtk.Window.__init__(self, title="pysonoff")
        self.set_border_width( 5 )
        self.set_default_size( int(self.cConfig['Width']), int(self.cConfig['Height']) )

        #---------- Header Bar
        #Configure a Headerbar
        cHeaderBar = Gtk.HeaderBar()
        cHeaderBar.set_show_close_button(True)
        cHeaderBar.props.title = "pySONOFF " + VERSION_NUMBER
        cHeaderBar.props.subtitle = "Your eWeLink replacement on Linux"
        self.set_titlebar(cHeaderBar)

        #Buttons for Headerbar
        myConfigButton = Gtk.Button()
        myConfigButton.props.relief = Gtk.ReliefStyle.NONE
        myConfigButton.add( Gtk.Image.new_from_gicon( Gio.ThemedIcon( name="emblem-system-symbolic" ), Gtk.IconSize.BUTTON ) )
        myConfigButton.connect( "clicked", self.onConfigButtonClicked )

        myUpdateButton = Gtk.Button()
        myUpdateButton.props.relief = Gtk.ReliefStyle.NONE
        myUpdateButton.add( Gtk.Image.new_from_gicon( Gio.ThemedIcon( name="emblem-synchronizing-symbolic" ), Gtk.IconSize.BUTTON ) )
        myUpdateButton.connect( "clicked", self.onUpdateButtonClicked )

        #Create a switch for the headerbar
        self.onoffSwitch = Gtk.Switch()
        self.onoffSwitch.props.valign = Gtk.Align.CENTER
        self.onoffSwitch.connect( "state-set", self.onSwitchChanged )

        #Pack everything
        cHeaderBar.pack_start( myConfigButton )
        cHeaderBar.pack_end( self.onoffSwitch )
        cHeaderBar.pack_end( myUpdateButton )
        #----------Header Bar ***END***

        #----------Scroller
        #Create a scrollable container for the TextView
        myScroller = Gtk.ScrolledWindow()
        myScroller.set_border_width( 2 )
        myScroller.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC )

        #Setup treeview an it's data source
        self.cTreeStore = Gtk.TreeStore( str, str, str, str, str, bool, int )
        self.cTreeView = Gtk.TreeView( model= self.cTreeStore )

        #First column
        tmpRenderer = Gtk.CellRendererText()
        tmpFirstColumn = Gtk.TreeViewColumn( "Name", tmpRenderer, text=0 )
        self.cTreeView.append_column( tmpFirstColumn )

        #Second column
        tmpRenderer = Gtk.CellRendererText()
        tmpSecondColumn = Gtk.TreeViewColumn( "ID", tmpRenderer, text=1 )
        self.cTreeView.append_column( tmpSecondColumn )

        #Third column
        tmpRenderer = Gtk.CellRendererText()
        tmpThirdColumn = Gtk.TreeViewColumn( "Mfr.", tmpRenderer, text=2 )
        self.cTreeView.append_column( tmpThirdColumn )

        #Fourth column
        tmpRenderer = Gtk.CellRendererText()
        tmpFourthColumn = Gtk.TreeViewColumn( "Model", tmpRenderer, text=3 )
        self.cTreeView.append_column( tmpFourthColumn )

        #Fifth column
        tmpRenderer = Gtk.CellRendererText()
        tmpFifthColumn = Gtk.TreeViewColumn( "FW", tmpRenderer, text=4 )
        self.cTreeView.append_column( tmpFifthColumn )

        #Sixth column
        tmpRenderer = Gtk.CellRendererToggle()
        tmpRenderer.connect("toggled", self.onSwitchToggled )
        tmpSixthColumn = Gtk.TreeViewColumn( "State", tmpRenderer, active=5 )
        self.cTreeView.append_column( tmpSixthColumn )

        #Last column
        tmpRenderer = Gtk.CellRendererProgress()
        tmpRenderer.props.text = " "
        tmpLastColumn = Gtk.TreeViewColumn( "RSSI", tmpRenderer, value=6, )
        self.cTreeView.append_column( tmpLastColumn )

        #Add treeview to scroller
        myScroller.add( self.cTreeView )
        #Add scroller to window
        self.add( myScroller )
        #---------- Scroller ***END***

        #---------- Popover
        #Define popover items
        self.cEntryUsername = Gtk.Entry()
        self.cEntryPassword = Gtk.Entry()
        self.cEntryPassword.set_visibility( False )
        self.cEntryApiKey = Gtk.Entry()
        self.cEntryApiKey.set_editable( False )
        self.cEntryToken = Gtk.Entry()
        self.cEntryToken.set_editable( False )
        self.cEntryRegion = Gtk.ComboBoxText()
        self.cEntryRegion.append_text( "eu" )
        self.cEntryRegion.append_text( "us" )
        self.cEntryRegion.append_text( "cn" )
        self.cEntryRegion.set_active(0)
        self.cPopover = Gtk.Popover()
        self.cPopover.set_border_width( 10 )

        #Pack popover
        tmpVerticalBox = Gtk.Box( orientation= Gtk.Orientation.VERTICAL )
        tmpHorizontalBox = Gtk.Box( orientation= Gtk.Orientation.HORIZONTAL)
        tmpHorizontalBox.pack_start( Gtk.Label("Username"), False, False, 2)
        tmpVerticalBox.pack_start(tmpHorizontalBox, True, False, 2)
        tmpVerticalBox.pack_start( self.cEntryUsername, True, False, 10 )
        tmpHorizontalBox = Gtk.Box( orientation= Gtk.Orientation.HORIZONTAL)
        tmpHorizontalBox.pack_start( Gtk.Label("Password"), False, False, 2)
        tmpVerticalBox.pack_start(tmpHorizontalBox, True, False, 2)
        tmpVerticalBox.pack_start( self.cEntryPassword, True, False, 10 )
        tmpHorizontalBox = Gtk.Box( orientation= Gtk.Orientation.HORIZONTAL)
        tmpHorizontalBox.pack_start( Gtk.Label("Region"), False, False, 2)
        tmpVerticalBox.pack_start(tmpHorizontalBox, True, False, 2)
        tmpVerticalBox.pack_start( self.cEntryRegion, True, False, 10 )
        tmpHorizontalBox = Gtk.Box( orientation= Gtk.Orientation.HORIZONTAL)
        tmpHorizontalBox.pack_start( Gtk.Label("Apikey"), False, False, 2)
        tmpVerticalBox.pack_start(tmpHorizontalBox, True, False, 2)
        tmpVerticalBox.pack_start( self.cEntryApiKey, True, False, 10 )
        tmpHorizontalBox = Gtk.Box( orientation= Gtk.Orientation.HORIZONTAL)
        tmpHorizontalBox.pack_start( Gtk.Label("Token"), False, False, 2)
        tmpVerticalBox.pack_start(tmpHorizontalBox, True, False, 2)
        tmpVerticalBox.pack_start( self.cEntryToken, True, False, 10 )
        self.cPopover.add( tmpVerticalBox )

        #Connect popover
        self.cPopover.connect( "closed", self.onPopoverClosed )
        self.cPopover.set_position(Gtk.PositionType.BOTTOM)
        #---------- Popover ***END***
        #--------------------------------------------------Contruct UI ***END***

        #Load config into popover fields
        self.cLoadConfig()

        #Save Window data before closing
        self.connect( "delete-event", self.mainWindowDelete )

        #Connect the destroy signal to the main loop quit function
        self.connect("destroy", Gtk.main_quit )

        #Recover old Position
        self.move( int(self.cConfig['Pos_X']), int(self.cConfig['Pos_Y']) )


    def mainWindowDelete( self, widget, data=None ):
        self.cConfig['Width'] = self.get_size()[0]
        self.cConfig['Height'] = self.get_size()[1]
        self.cConfig['Pos_X'] = self.get_position()[0]
        self.cConfig['Pos_Y'] = self.get_position()[1]
        self.cConfig.write()

    def onSwitchToggled( self, widget, path ):
        #Establish the necessary state strings as it turns out that the switches do not accept True or False
        tmpOnOff = [ 'off', 'on' ]
        #Get position in list (iterator)
        tmpIter = self.cTreeStore.get_iter(path)
        #Invert checkbox
        self.cTreeStore[path][5] = not self.cTreeStore[path][5]
        #Do we have childs?
        if self.cTreeStore.iter_has_child( tmpIter ):
            #YES - Iterate over them
            for tmpCount in range( self.cTreeStore.iter_n_children( tmpIter ) ):
                #Set child checkbox to parent value
                self.cTreeStore.set_value(
                            self.cTreeStore.iter_nth_child( tmpIter, tmpCount ),
                            5,
                            self.cTreeStore[path][5])
                #Set switch to checkbox value
                self.cHome.switch(
                            tmpOnOff[int( self.cTreeStore.get_value( self.cTreeStore.iter_nth_child( tmpIter, tmpCount ), 5 ) )],
                            self.cTreeStore.get_value( self.cTreeStore.iter_nth_child( tmpIter, tmpCount ), 1 ),
                            int( tmpCount ))
        else:
            #NO - Set the item to the inverted value
            # Does this item hace childs (thus it is not a root item)?
            if self.cTreeStore[path][0][0:6]=='Outlet':
                #YES - Flick the switch
                self.cHome.switch(
                            tmpOnOff[int( self.cTreeStore[path][5] )],
                            self.cTreeStore[path][1],
                            int( self.cTreeStore[path][0][-1:] ))
                #Get the root node pointer
                tmpRootIter = self.cTreeStore.iter_parent( tmpIter )
                #Set a check variable
                tmpCheck = True
                #Check if all nodes are set
                for tmpCount in range( self.cTreeStore.iter_n_children( tmpRootIter ) ):
                    if self.cTreeStore.get_value( self.cTreeStore.iter_nth_child( tmpRootIter, tmpCount ), 5) == False:
                        tmpCheck = False
                        break
                if tmpCheck == False:
                    self.cTreeStore.set_value( self.cTreeStore.iter_parent( tmpIter ), 5, False )
                else:
                    self.cTreeStore.set_value( self.cTreeStore.iter_parent( tmpIter ), 5, True )
            else:
                #NO - Flick the switch
                self.cHome.switch(
                            tmpOnOff[int( self.cTreeStore[path][5] )],
                            self.cTreeStore[path][1])

    def cLoadConfig( self ):
        #Get config file parser
        self.cConfig = configobj.ConfigObj( os.path.expanduser("~")+'/.config/sonoff/default.config')
        #Read username
        self.cEntryUsername.set_text( self.cConfig['Username'] )
        #Read password
        self.cEntryPassword.set_text( self.cConfig['Password'] )
        #Read region
        if self.cConfig['Region'] == 'eu':
            self.cEntryRegion.set_active(0)
        elif self.cConfig['Region'] == 'us':
            self.cEntryRegion.set_active(1)
        else:
            self.cEntryRegion.set_active(2)
        #Read API key
        self.cEntryApiKey.set_text( self.cConfig['Apikey'] )
        #Read Token
        self.cEntryToken.set_text( self.cConfig['Token'] )

    def onPopoverClosed( self, widget ):
        #Are we connected?
        if self.onoffSwitch.get_state() == False:
            #NO - Write config
            self.cConfig.write()
        else:
            #YES - Print out en error and do nothing (TODO: MessageDialog)
            print("Cannot write config while connected (for security reasons)")

    def onConfigButtonClicked( self, widget ):
        #Position the popover
        self.cPopover.set_relative_to( widget )
        #Show it...
        self.cPopover.show_all()
        #Do your thing
        self.cPopover.popup()

    def onSwitchChanged( self, widget, state ):
        if state == True :
            #Clear old data
            self.cTreeStore.clear()
            #Instantiate sonoff with access data
            self.cHome = sonoff.Sonoff(
                self.cEntryUsername.get_text(),
                self.cEntryPassword.get_text(),
                self.cEntryRegion.get_active_text(),
                self.cEntryApiKey.get_text()
                #self.cEntryToken.get_text()
                )
            self.updateTreeView()
        else:
            #NO - The slider was turned off.
            #Clear the TextView
            self.cTreeStore.clear()

    def onUpdateButtonClicked( self, widget ):
        self.cHome.update_devices()
        self.updateTreeView()

    def updateTreeView( self ):
        #Define hardware models
        tmpModel = {
            'Basic'               : 1 ,
            'Sonoff Touch EUC1'   : 1 ,
            'Touch EU'            : 1 ,
            'T1 2C'               : 2 }
        tmpTrueFalse = {
            'on'        : True,
            'off'       : False }
        #Remove old data
        self.cTreeStore.clear()
        #Iterate over devices
        for tmpDevice in self.cHome.get_devices():
            #Is yhe model known?
            if tmpDevice['productModel'] not in tmpModel:
                print('The current product is not found in my device list. Please open an issue at ' + WEB_PAGE )
                tmpModel.update( { 'Unknown' : 4} )
            #Is the device a multiswitch?
            if 'switches' in tmpDevice['params']:
                #YES - Check if all childs are on or off
                #Presume they are on
                tmpChildsPosition = True
                #Iterate over them
                for tmpOutlet in tmpDevice['params']['switches']:
                    #Are the switches relevant? (Sometimes there are more outlets in the configuration then on the physical device)
                    if tmpOutlet['outlet'] < tmpModel[tmpDevice['productModel']]:
                        #YES - Construct a logical AND -> true + true = true; true + false = false. A false value will always be false.
                        tmpChildsPosition = tmpChildsPosition and tmpTrueFalse[tmpOutlet['switch']]
                    else:
                        #NO - Stop the loop
                        break
                #Insert a parent with the result of the childs and save it's iter
                tmpParent = self.cTreeStore.append(
                            None,
                            [
                                tmpDevice['name'],
                                tmpDevice['deviceid'],
                                tmpDevice['brandName'],
                                tmpDevice['productModel'],
                                tmpDevice['params']['fwVersion'],
                                tmpChildsPosition,
                                int( 130+tmpDevice['params']['rssi'] ) ] )
                #Iterate over outlets
                for tmpOutlet in tmpDevice['params']['switches']:
                    tmpArray = [
                                "Outlet "+str( tmpOutlet['outlet'] ),
                                tmpDevice['deviceid'],
                                "",
                                "",
                                "",
                                tmpTrueFalse[tmpOutlet['switch']],
                                int( 130+tmpDevice['params']['rssi'] ) ]
                    #Is the outlet relevant?
                    if tmpOutlet['outlet'] < tmpModel[tmpDevice['productModel']]:
                        #YES - Add the array to our treeview
                        self.cTreeStore.append( tmpParent, tmpArray )
            else:
                #NO - Only one outlet available
                tmpArray = [
                            tmpDevice['name'],
                            tmpDevice['deviceid'],
                            tmpDevice['brandName'],
                            tmpDevice['productModel'],
                            tmpDevice['params']['fwVersion'],
                            tmpTrueFalse[tmpDevice['params']['switch']],
                            int( 130+tmpDevice['params']['rssi'] ) ]
                # Add the array to the treeview
                self.cTreeStore.append( None, tmpArray )
                self.cTreeView.expand_all()

#Create Main Window
myWindow = MainWindow()

#Connect the destroy signal to the main loop quit function
myWindow.connect("destroy", Gtk.main_quit)

#Show Windows on screen
myWindow.show_all()

#Main Loop
Gtk.main()
