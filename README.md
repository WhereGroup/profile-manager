### Profile Manager for QGIS ###
A QGIS plugin for managing your profiles and data source connections.

https://plugins.qgis.org/plugins/profile-manager/

<a href="https://github.com/WhereGroup/profile-manager/assets/7661092/a64ea854-bff3-48a0-b1ff-83f3d4eaa5b7"><img src="https://github.com/WhereGroup/profile-manager/assets/7661092/a64ea854-bff3-48a0-b1ff-83f3d4eaa5b7" width="200"></a>
<a href="https://github.com/WhereGroup/profile-manager/assets/7661092/711faa86-c36c-40bc-92ab-7b73016996ae"><img src="https://github.com/WhereGroup/profile-manager/assets/7661092/711faa86-c36c-40bc-92ab-7b73016996ae" width="200"></a>
<a href="https://github.com/WhereGroup/profile-manager/assets/7661092/0c646930-88d8-45fe-81c8-4a5bf4501152"><img src="https://github.com/WhereGroup/profile-manager/assets/7661092/0c646930-88d8-45fe-81c8-4a5bf4501152" width="200"></a>
<a href="https://github.com/WhereGroup/profile-manager/assets/7661092/079665d6-e0ff-45fb-a65c-3b49cd9229de"><img src="https://github.com/WhereGroup/profile-manager/assets/7661092/079665d6-e0ff-45fb-a65c-3b49cd9229de" width="200"></a>

### Installation ###
To install the plugin manually just copy the folder into your QGIS profile directory under ./python/plugins/

- Windows directory:
    - `C:\Users\{USER}\AppData\Roaming\QGIS\QGIS3\profiles\{PROFILE}\python\plugins\`
- Linux directory:
    - `~/.local/share/QGIS/QGIS3/profiles/{PROFILE}/python/plugins`
- MacOS directory:
    - `~/Library/Application Support/QGIS/QGIS3/profiles`

### Features ###
- Create a new profile
    - Creates and initiates a new profile
- Removing profile
    - Removes a selected profile
- Copy profile
    - Creates a copy of a selected profile with a new name
- Rename profile
    - Renames the profile with a name provided by the user
- Importing data source connections from one profile to another
- Removing data source connections from a profile
    - Removes the data source connection from the chosen SOURCE profile
- Importing (spatial) bookmarks
- Importing (data source) favourites
- Importing plugins
- Importing expressions
- Importing models
- Importing scripts
- Importing some symbology types & label settings
- Importing QGIS UI settings (e.g. hidden toolbar items)

On all removal operations the user is being asked if they are certain
that he wants to delete given source/profile.
Additionally before every deletion a backup of the complete profiles
folder is created under the following directory:
- Windows directory:
    - `C:\Users\{USER}\QGIS Profile Manager Backup\`
- Linux and MacOS directory:
    - `~/QGIS Profile Manager Backup/`

### Known (current) limitations ###
- Not all data source connections might be recognized and imported/removed
- Not all data source connection types are supported
- Python expression functions are not supported
- Not all style things are supported, e.g. not 3D symbols, color ramps,
  tags, etc.
- Errors might not always be communicated clearly so please TEST your
  migrated configurations before discarding originals!

### Funding development ###
If you consider this plugin useful and would like to see it improved, e.g.
with support for more profile settings, becoming more stable, being more
thoroughly documented, leave the "experimental" plugin status or whatever
you desire, you can fund development. Contact us at info@wheregroup.com
