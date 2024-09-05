FORMS = ../profile_manager_dialog_base.ui

SOURCES = \
	../utils.py \
	../profiles/profile_copier.py \
	../profiles/profile_editor.py \
	../profiles/profile_remover.py \
	../profiles/profile_creator.py \
	../profiles/profile_action_handler.py \
	../profile_manager_dialog.py \
	../userInterface/interface_handler.py \
	../userInterface/name_profile_dialog.py \
	../profile_manager.py \
	../datasources/Functions/function_handler.py \
	../datasources/Dataservices/datasource_distributor.py \
	../datasources/Dataservices/datasource_provider.py \
	../datasources/Dataservices/datasource_handler.py \
	../datasources/Bookmarks/bookmark_handler.py \
	../datasources/Favourites/favourites_handler.py \
	../datasources/Models/script_handler.py \
	../datasources/Models/model_handler.py \
	../datasources/Plugins/plugin_remover.py \
	../datasources/Plugins/plugin_handler.py \
	../datasources/Plugins/plugin_displayer.py \
	../datasources/Plugins/plugin_importer.py \
	../datasources/Customizations/customization_handler.py \
	../datasources/Styles/style_handler.py

TRANSLATIONS = \
	ProfileManager_de.ts \
	ProfileManager_it.ts
