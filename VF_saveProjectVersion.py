bl_info = {
	"name": "VF Save Project Version",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 1, 2),
	"blender": (3, 6, 0),
	"location": "Top bar > File > Save Version",
	"description": "Saves a versioned project file to the specified directory",
	"doc_url": "https://github.com/jeinselen/VF-BlenderSaveProjectVersion",
	"tracker_url": "https://github.com/jeinselen/VF-BlenderSaveProjectVersion/issues",
	"category": "Import-Export"}

import bpy
import datetime
import os
from re import match, findall, split, M as multiline
#from pathlib import Path
#import platform
#from re import findall, search, sub, M as multiline
#import time

###########################################################################
# Save new file version

class VF_OT_SaveProjectVersion(bpy.types.Operator):
	bl_idname = "wm.saveprojectversion"
	bl_label = "Save Project Version"
	bl_description = "Save a versioned project file in the specified directory"
	bl_space_type = "TOPBAR"
	bl_region_type = 'UI'
	
	increment_major: bpy.props.BoolProperty(default=False)
	
	def invoke(self, context, event):
		# Get preferences
		version_type = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_type
		version_format = format(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_format, '02')
		version_separator = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_separator
		
		# Get current project path
		project_path = os.path.dirname(bpy.data.filepath)
		
		# If project hasn't been saved yet, open a save dialogue
		if len(project_path) < 1:
			# Open save dialogue
			bpy.ops.wm.save_mainfile('INVOKE_AREA')
			return {'FINISHED'}
		
		# Get project name
		project_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
		
		# If set to alphanumeric, separate version elements from project name
		if version_type == "ALPHANUM":
			project_name_parts = split(r'([0-9]{3})([a-z]{1})$', project_name)
			if len(project_name_parts) > 3:
				project_name = project_name_parts[0]
				# Increment values (major: "001x" to "002a", minor: "001a" to "001b")
				if self.increment_major:
					project_num = format(int(project_name_parts[1]) + 1, version_format)
					project_chr = "a"
				else:
					project_num = project_name_parts[1]
					project_chr = str(chr(ord(project_name_parts[2]) + 1))
			else:
				project_name = "{project}{separator}"
				project_num = format(1, version_format)
				project_chr = "a"
		else:
			project_num = False
			project_chr = False
		
		# Get defined version path
		version_path = bpy.path.abspath(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_path)
		
		# If empty or single character, use a folder with the same name as the project file
		if len(version_path) <= 1:
			# Replace one or fewer characters with the project path
			version_path = os.path.join(os.path.dirname(bpy.data.filepath), project_name)
		
		# Convert relative paths into absolute paths for Python compatibility
		project_path = bpy.path.abspath(project_path)
		version_path = bpy.path.abspath(version_path)
		
		# Create version directory if it doesn't exist yet
		if not os.path.exists(version_path):
			os.makedirs(version_path)
		
		# Generate file name with identifier
		if version_type == 'SERIAL': # Generate dynamic serial number
			# Finds all project files that start with project_name in the selected directory
			files = [f for f in os.listdir(version_path) if f.startswith(project_name) and f.lower().endswith(".blend")]
			
			# Searches the file collection and returns the next highest number as a formated string
			def save_number_from_files(files):
				highest = -1
				if files:
					for f in files:
						# find filenames that end with four or more digits
						suffix = findall(r'\d{4,}$', os.path.splitext(f)[0].split(project_name)[-1], multiline)
						if suffix:
							if int(suffix[-1]) > highest:
								highest = int(suffix[-1])
				return format(highest + 1, version_format)
		
			# Create string with serial number
			version_name = '{project}{separator}' + save_number_from_files(files)
		
		elif version_type == 'DATETIME':
			# Create string with date and time
			version_name = '{project}{separator}{date}-{time}'
		
		elif version_type == 'ALPHANUM':
			# Create string with alphanumeric major/minor serial code
			version_name = '{project}{num}{chr}'
		
		# Convert variables (allows for greater flexibility in the future and potential reduction of redundant code)
		def convert_variables(string):
			string = string.replace("{project}", project_name)
			string = string.replace("{separator}", version_separator)
			string = string.replace("{date}", datetime.datetime.now().strftime('%Y-%m-%d'))
			string = string.replace("{time}", datetime.datetime.now().strftime('%H-%M-%S'))
			if project_num:
				string = string.replace("{num}", project_num)
			if project_chr:
				string = string.replace("{chr}", project_chr)
			return string
		
		# Save version
		if version_type == 'ALPHANUM':
			# Save current file with new serial number
			project_path = os.path.join(project_path, version_name) + '.blend'
			project_path = convert_variables(project_path)
			bpy.ops.wm.save_as_mainfile(filepath=project_path, relative_remap=True)
			
			# Move previous project file(s) to version directory
			old_path = os.path.join(project_path, project_name) + '.blend'
			old_path = convert_variables(old_path)
			new_path = os.path.join(version_path, project_name) + '.blend'
			new_path = convert_variables(new_path)
			os.rename(old_path, new_path)
			if os.path.isfile(old_path + '1'):
				os.rename(old_path + '1', new_path + '1')
			
			# An alternative approach:
			# save the current file as a copy into the version directory with current (old) name
			# save the current project file with new file name in the project directory
			# then remove the old project in the project directory
			# ...downside is that removing a file could fail disastrously if the copy fails to save but the script continues to process, leaving the user with only their current project (or worse, the new project gets deleted and they close Blender!)
		else:
			# Combine file path and file name using system separator, add project extension
			version_path = os.path.join(version_path, version_name) + '.blend'
			version_path = convert_variables(version_path)
			bpy.ops.wm.save_as_mainfile(filepath=version_path, compress=True, relative_remap=True, copy=True)
		
		# Build display path to display success feedback
		display_path = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_path
		if len(display_path) <= 1:
			display_path = project_name
		display_path = os.path.join(display_path, version_name + '.blend')
		
		# Provide success feedback
		self.report ({'INFO'}, "Version saved successfully: " + display_path)
		if bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_confirm:
			def draw(self, context):
				self.layout.label(text=display_path)
			bpy.context.window_manager.popup_menu(draw, title="Version Saved Successfully", icon='FOLDER_REDIRECT') # Alt: INFO
		
		# Done
		return {'FINISHED'}



###########################################################################
# Global user preferences and UI rendering class

class VfSaveProjectVersionPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	
	# Version location
	version_path: bpy.props.StringProperty(
		name="Path",
		description="Leave a single forward slash to auto generate folders alongside project files",
		default="//_Archive",
		maxlen=4096,
		subtype="DIR_PATH")
	version_separator: bpy.props.StringProperty(
		name="Separator",
		description="separator between the project name and the version number",
		default="-",
		maxlen=16)
	version_type: bpy.props.EnumProperty(
		name='Type',
		description='Version file naming convention',
		items=[
			('SERIAL', 'Serial Number', 'Save versions using autogenerated serial numbers'),
			('DATETIME', 'Date and Time', 'Save versions with the current date and time'),
			('ALPHANUM', 'Alphanumeric', 'Save versions with an incrementing version number and alphabetical indicator')
			],
		default='SERIAL')
	version_format: bpy.props.IntProperty(
		name="Digits",
		description="Number of serial number digits, padded with leading zeroes",
		default=3)
	version_confirm: bpy.props.BoolProperty(
		name='Confirmation Popup',
		description='Confirms successful version saving with a popup panel',
		default=False)
	
	# User Interface
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		
		col = layout.column(align=True)
		col.prop(self, "version_path")
		col.prop(self, "version_separator")
		col.prop(self, "version_type")
		if self.version_type != 'DATETIME':
			col.prop(self, "version_format")
		col.prop(self, "version_confirm")



###########################################################################
# Menu UI
		
def TOPBAR_MT_file_save_version(self, context):
	bl_idname = 'TOPBAR_MT_file_save_version'
	self.layout.separator()
	if bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_type == 'ALPHANUM':
		self.layout.operator(VF_OT_SaveProjectVersion.bl_idname, text = "Save Minor Version", icon = "FOLDER_REDIRECT")
		self.layout.operator(VF_OT_SaveProjectVersion.bl_idname, text = "Save Major Version", icon = "FOLDER_REDIRECT")
	else:
		self.layout.operator(VF_OT_SaveProjectVersion.bl_idname, text = "Save Version", icon = "FOLDER_REDIRECT")
	# FILE_NEW FILE_TICK FILE_BLEND FOLDER_REDIRECT



###########################################################################
# Addon registration functions

classes = (VF_OT_SaveProjectVersion, VfSaveProjectVersionPreferences)

addon_keymaps = []

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
#	bpy.types.Scene.vf_save_version_settings = bpy.props.PointerProperty(type=VfSaveProjectVersionPreferences)
	bpy.types.TOPBAR_MT_file.append(TOPBAR_MT_file_save_version)
	
	# Add keyboard shortcuts
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	if kc:
		# Linux/Windows Increment/Increment Minor
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new(VF_OT_SaveProjectVersion.bl_idname, 'S', 'PRESS', ctrl=True, alt=True, shift=True)
		addon_keymaps.append((km, kmi))
		
		## MacOS Increment/Increment Minor
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new(VF_OT_SaveProjectVersion.bl_idname, 'S', 'PRESS', oskey=True, alt=True, shift=True)
		addon_keymaps.append((km, kmi))
		
		## MacOS Increment Major
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new(VF_OT_SaveProjectVersion.bl_idname, 'S', 'PRESS', oskey=True, ctrl=True, alt=True, shift=True)
		kmi.properties.increment_major = True
		addon_keymaps.append((km, kmi))

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
#	del bpy.types.Scene.vf_save_version_settings
	bpy.types.TOPBAR_MT_file.remove(TOPBAR_MT_file_save_version)
	
	# Remove keyboard shortcuts
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == "__main__":
	register()