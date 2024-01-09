bl_info = {
	"name": "VF Save Version",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 0, 2),
	"blender": (3, 6, 0),
	"location": "Top bar > File > Save Version",
	"description": "Saves a versioned file to the specified archive location",
	"warning": "inexperienced developer, use at your own risk",
	"doc_url": "https://github.com/jeinselen/VF-BlenderSaveVersion",
	"tracker_url": "https://github.com/jeinselen/VF-BlenderSaveVersion/issues",
	"category": "Import-Export"}

import bpy
import datetime
import os
from re import match, findall, M as multiline
#from pathlib import Path
#import platform
#from re import findall, search, sub, M as multiline
#import time

###########################################################################
# Save new file version

class VF_OT_SaveVersion(bpy.types.Operator):
	bl_idname = "wm.saveversion"
	bl_label = "Save Version"
	bl_description = "Save a versioned file in the defined directory"
	bl_space_type = "TOPBAR"
	bl_region_type = 'UI'
	
	def invoke(self, context, event):
		# Get current project path
		project_path = os.path.dirname(bpy.data.filepath)
		
		if len(project_path) < 1:
			# Open save dialogue
			bpy.ops.wm.save_mainfile('INVOKE_AREA')
			return {'FINISHED'}
		
		# Get project name
		project_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
		
		# Get defined version path
		version_path = bpy.path.abspath(bpy.context.preferences.addons['VF_saveVersion'].preferences.version_path)
		
		if len(version_path) <= 1:
			# Replace one or fewer characters with the project path
			version_path = os.path.join(os.path.dirname(bpy.data.filepath), projectname)
		
		# Convert relative path into absolute path for Python compatibility
		project_path = bpy.path.abspath(project_path)
		version_path = bpy.path.abspath(version_path)
		
		# Create directory if it doesn't exist yet
		if not os.path.exists(version_path):
			os.makedirs(version_path)
		
		# Get defined version naming pattern
		version_type = bpy.path.abspath(bpy.context.preferences.addons['VF_saveVersion'].preferences.version_type)
		
		# Generate file name with identifier
		if version_type == 'SERIAL': # Generate dynamic serial number
			# Finds all of the image files that start with projectname in the selected directory
			files = [f for f in os.listdir(version_path) if f.startswith(project_name) and f.lower().endswith(".blend")]
			
			# Searches the file collection and returns the next highest number as a 4 digit string
			def save_number_from_files(files):
				highest = -1
				if files:
					for f in files:
						# find filenames that end with four or more digits
						suffix = findall(r'\d{4,}$', os.path.splitext(f)[0].split(project_name)[-1], multiline)
						if suffix:
							if int(suffix[-1]) > highest:
								highest = int(suffix[-1])
				return format(highest+1, '04')
		
			# Create string with serial number
			version_name = '{project} version-' + save_number_from_files(files)
		
		elif version_type == 'DATETIME':
			# Create string with date and time
			version_name = '{project} {date} {time}'
		
		# Combine file path and file name using system separator
		version_path = os.path.join(version_path, version_name)
		
		# Convert variables (this allows for greater flexibility in the future)
		version_path = version_path.replace("{project}", project_name)
		version_path = version_path.replace("{date}", datetime.datetime.now().strftime('%Y-%m-%d'))
		version_path = version_path.replace("{time}", datetime.datetime.now().strftime('%H-%M-%S'))
		
		# Add project extension
		version_path += '.blend'
		
		# Save version
		bpy.ops.wm.save_as_mainfile(filepath=version_path, compress=True, copy=True)
#		bpy.ops.wm.save_as_mainfile(filepath=version_path, compress=True, relative_remap=True, copy=True)
		
		# Done
		return {'FINISHED'}

###########################################################################
# Global user preferences and UI rendering class

class VfSaveVersionPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	
	# Version location
	version_path: bpy.props.StringProperty(
		name="Version Path",
		description="Leave a single forward slash to auto generate folders alongside project files",
		default="//Versions",
		maxlen=4096,
		subtype="DIR_PATH")
	version_type: bpy.props.EnumProperty(
		name='Version Type',
		description='Version file naming convention',
		items=[
			('SERIAL', 'Serial Number', 'Save versions using autogenerated serial numbers'),
#			('DATE', 'Current Date', 'Save versions using the date (same day versions will overwrite)'),
#			('TIME', 'Current Time', 'Save versions using the time (same time versions will overwrite)'),
			('DATETIME', 'Date and Time', 'Save versions with the current date and time')
			],
		default='SERIAL')
	
	# User Interface
	def draw(self, context):
		layout = self.layout
		
		layout.prop(self, "version_path")
		layout.prop(self, "version_type")

###########################################################################
# Menu UI
		
def TOPBAR_MT_file_save_version(self, context):
	bl_idname = 'TOPBAR_MT_file_save_version'
	self.layout.separator()
	self.layout.operator(VF_OT_SaveVersion.bl_idname, text = "Save Version", icon = "FOLDER_REDIRECT")
	# FILE_NEW FILE_TICK FILE_BLEND FOLDER_REDIRECT

###########################################################################
# Addon registration functions

classes = (VF_OT_SaveVersion, VfSaveVersionPreferences)

addon_keymaps = []

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
#	bpy.types.Scene.vf_save_version_settings = bpy.props.PointerProperty(type=VfSaveVersionPreferences)
	bpy.types.TOPBAR_MT_file.append(TOPBAR_MT_file_save_version)
	
	# Add keyboard shortcuts
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	if kc:
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new(VF_OT_SaveVersion.bl_idname, 'S', 'PRESS', ctrl=True, alt=True, shift=True)
		addon_keymaps.append((km, kmi))
	if kc:
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new(VF_OT_SaveVersion.bl_idname, 'S', 'PRESS', oskey=True, alt=True, shift=True)
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