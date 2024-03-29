bl_info = {
	"name": "VF Save Project Version",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 2, 0),
	"blender": (3, 6, 0),
	"location": "Top bar > File > Save Version",
	"description": "Saves a versioned project file to the specified directory",
	"doc_url": "https://github.com/jeinselen/VF-BlenderSaveProjectVersion",
	"tracker_url": "https://github.com/jeinselen/VF-BlenderSaveProjectVersion/issues",
	"category": "Import-Export"}

import bpy
import datetime
import os
from re import findall, search, split, M as multiline

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
		# Define project names
		project_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
		
		# Get preferences
		version_path = bpy.path.abspath(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_path)
		version_type = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_type
		if (bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_auto):
			alphanum = search('(\d+[A-Za-z]{1})$', project_name)
			if alphanum is not None:
				version_type = 'ALPHANUM'
		version_separator = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_separator
		if version_type == 'ALPHANUM':
			version_length = format(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_length - 1, '02')
		else:
			version_length = format(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_length, '02')
		version_compress = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_compress
		version_deletebackup = bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_deletebackup
		
		# Define project paths
		project_path = os.path.dirname(bpy.data.filepath)
		
		# If project hasn't been saved yet, open a save dialogue
		if len(project_path) < 1:
			# Open save dialogue
			bpy.ops.wm.save_mainfile('INVOKE_AREA')
			return {'FINISHED'}
		
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
		
		# Generate file name with numerical identifier
		if version_type == 'NUM': # Generate dynamic serial number
			# Finds all project files that start with project_name in the selected directory
			files = [f for f in os.listdir(version_path) if f.startswith(project_name) and f.lower().endswith(".blend")]
			
			# Searches the file collection and returns the next highest number as a formated string
			def save_number_from_files(files):
				highest = -1
				if files:
					for f in files:
						# find filenames that end with digits
						suffix = findall(r'\d+$', os.path.splitext(f)[0].split(project_name)[-1], multiline)
						if suffix:
							if int(suffix[-1]) > highest:
								highest = int(suffix[-1])
				return format(highest + 1, version_length)
			
			# Create string with serial number
			version_name = project_name + version_separator + save_number_from_files(files)
		
		# Generate file name with date and time
		elif version_type == 'TIME':
			# Create string with date and time
			version_name = project_name + version_separator + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		
		# If set to alphanumeric, separate version elements from project name, increment, recombine
		elif version_type == 'ALPHANUM':
			project_name_parts = split(r'([0-9]{1,})([a-z]{1})$', project_name)
			# If project is already versioned, increment
			if len(project_name_parts) > 3:
				# Increment values (major: "001x" to "002a", minor: "001a" to "001b")
				if self.increment_major:
					project_num = format(int(project_name_parts[1]) + 1, version_length)
					project_chr = "a"
				else:
#					project_num = project_name_parts[1] # This preserve shorter/longer serial number padding if already present
					project_num = format(int(project_name_parts[1]), version_length)
					project_chr = str(chr(ord(project_name_parts[2]) + 1))
				version_name = project_name_parts[0] + project_num + project_chr
			# If project is not yet versioned, create new version
			else:
				project_num = format(1, version_length)
				project_chr = "a"
				version_name = project_name + version_separator + project_num + project_chr
		
		
		
		# Save version
		if version_type != 'ALPHANUM':
			# Save copy of current project with new name in the archive location
			version_file = os.path.join(version_path, version_name) + '.blend'
			bpy.ops.wm.save_as_mainfile(filepath=version_file, compress=version_compress, relative_remap=True, copy=True)
		else:
			# Save current project with new serial number in the current location
			project_file = os.path.join(project_path, version_name) + '.blend'
			bpy.ops.wm.save_as_mainfile(filepath=project_file, compress=version_compress)
			
			# Move previous project file to the archive location
			old_path = os.path.join(project_path, project_name)
			new_path = os.path.join(version_path, project_name)
			os.rename(old_path + '.blend', new_path + '.blend')
			
			# Move or delete backup file
			if os.path.isfile(old_path + '.blend1'):
				if version_deletebackup:
					os.remove(old_path + '.blend1')
				else:
					os.rename(old_path + '.blend1', new_path + '.blend1')
			
			# Also move autosave render folder (if it exists and uses the same name as the project)
			if os.path.exists(old_path):
				os.rename(old_path, new_path)
		
		
		
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
	version_type: bpy.props.EnumProperty(
		name='Type',
		description='Version file naming convention',
		items=[
			('NUM', 'Number', 'Save versions using autogenerated serial numbers'),
			('TIME', 'Timestamp', 'Save versions with the current date and time'),
			('ALPHANUM', 'Alphanumeric', 'Save versions with an incrementing major version number and minor alphabet character')
			],
		default='NUM')
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
	version_length: bpy.props.IntProperty(
		name="Characters",
		description="Total character count, padded with leading zeroes",
		default=4,
		soft_min=1,
		soft_max=8,
		min=1,
		max=8)
	version_compress: bpy.props.BoolProperty(
		name='Compression',
		description='Compresses versioned files, or for Alphanumeric, compresses the main project when saving',
		default=True)
	version_deletebackup: bpy.props.BoolProperty(
		name='Delete .blend1 files',
		description='Keeps the .blend1 backup file alongside the archived project',
		default=False)
	version_confirm: bpy.props.BoolProperty(
		name='Confirmation Popup',
		description='Confirms successful version saving with a popup panel',
		default=False)
	version_auto: bpy.props.BoolProperty(
		name='Autodetect Alphanumeric',
		description='Recognises if the current project file already has an alphanumeric serial number, and uses that versioning type automatically',
		default=True)
	
	# User Interface
	def draw(self, context):
		layout = self.layout
		
		# First group
		col = layout.column(align=True)
		
		# Create info strings
		if self.version_type == 'ALPHANUM':
			info = 'Saves project with new name, archives previous file'
			info_file = 'ProjectName' + self.version_separator
			version_length = format(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_length - 1, '02')
			info_file += format(1, version_length) + "b.blend,    " + self.version_path + '...' + format(1, version_length) + 'a.blend'
		else:
			info = 'Copies project to archive with '
			info_file = os.path.join(self.version_path, 'ProjectName') + self.version_separator
			if self.version_type == 'TIME':
				info += 'date and time'
				info_file += 'YYYY-MM-DD-HH-MM-SS'
			else:
				info += 'automatic serial number'
				version_length = format(bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_length, '02')
				info_file += format(1, version_length)
			info_file += '.blend'
		
		# Display info
		box = col.box()
		col2 = box.column(align=True)
		col2.label(text=info)
		col2.label(text=info_file)
		
		# Display version type buttons
		row = col.row(align=True)
		row.prop(self, 'version_type', expand=True)
		
		# Second group
		col = layout.column(align=True)
		
		# Display path
		col.prop(self, "version_path", text='')
		
		# Display naming options
		row = col.row(align=True)
		row.prop(self, "version_separator", text='')
		if self.version_type != 'TIME':
			row.prop(self, "version_length")
		
		# Display file options
		row = col.row(align=True)
		row.prop(self, "version_compress")
		if self.version_type == 'ALPHANUM':
			row.prop(self, "version_deletebackup")
		
		# Display popup option
		col.prop(self, "version_confirm")
		
		# Display automatic detection option
		col.prop(self, "version_auto")



###########################################################################
# Menu UI
		
def TOPBAR_MT_file_save_version(self, context):
	bl_idname = 'TOPBAR_MT_file_save_version'
	self.layout.separator()
	if bpy.context.preferences.addons['VF_saveProjectVersion'].preferences.version_type == 'ALPHANUM':
		minor = self.layout.operator(VF_OT_SaveProjectVersion.bl_idname, text = "Save Minor Version", icon = "FOLDER_REDIRECT")
		minor.increment_major = False
		major = self.layout.operator(VF_OT_SaveProjectVersion.bl_idname, text = "Save Major Version", icon = "FOLDER_REDIRECT")
		major.increment_major = True
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
		kmi.properties.increment_major = False
		addon_keymaps.append((km, kmi))
		
		## MacOS Increment/Increment Minor
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new(VF_OT_SaveProjectVersion.bl_idname, 'S', 'PRESS', oskey=True, alt=True, shift=True)
		kmi.properties.increment_major = False
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