### Profile Manager for QGIS3 ###

### Plugin for managing your profiles and datasources ###

### Installation ###

To install the plugin just copy the folder in your QGIS-Profile folder under ./python/plugins/

- Windows Directory:
    - C:\Users\{USER}\AppData\Roaming\QGIS\QGIS3\profiles\\{PROFILE}\python\plugins\
- Linux Directory:
    - /home/{USER}/.local/share/QGIS/QGIS3/profiles/{PROFILE}/python/plugins

### Features ###

- General Features:
    - Create a new profile
        - Creates and initiates a new QGIS profile
    - Reomving profile
        - Removes the currently marked profile
    - Copy profile
        - Copies profile into a new one with a name provided by the user
    - Rename profile
        - Renames the profile with a name provided by the user
    - Importing Datasources from one profile to another
        (Datasources are chosen by checking them in a TreeView where each source is displayed)
    - Removing Datasources from a profile
        - Removes the datasources from the chosen SOURCE profile
    - Importing bookmarks
    - Importing favourites
    - Importing plugins
    - Importing functions
    - Importing models & scripts
    - Importing style & label settings
    - Importing QGIS UI settings (f.e. hidden toolbar items)
    
On all removal operations the user is being asked if he is certain that he wants to delete given source/profile.
Additionally before every deletion a backup of the profiles folder is created under the follwing directory:
- Windows Directory:
    - C:\Users\\{USER}\QGISBackup\
- Linux Directory:
    - /home/{USER}/QGISBackup/
