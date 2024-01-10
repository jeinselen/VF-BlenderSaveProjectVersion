# VF Save Version

Saves the current Blender project in a subfolder or other directory path with a serial number or date and time using compression and linked asset remapping. Helps keep the root project directory clean even an artist is obsessive about saving progress as separate versions.

![screenshot of the successfully saved new version popup window in the Blender user interface](images/banner.jpg)







## Installation and Usage

- Download [VF_saveVersion.py](https://raw.githubusercontent.com/jeinselen/VF-BlenderSaveVersion/main/VF_saveVersion.py)
- Open Blender Preferences and navigate to the "Add-ons" tab
- Install and enable the add-on
- Adjust the versioning preferences as needed

The default settings will work as-is; saving the current project to an "_Archive" folder alongside the project file, with a new version number appended each time the save version command is used. The versioned files use compression to minimise `.blend` file size and have linked asset remapping enabled.

Default keyboard shortcuts are added for MacOS, Linux, and Windows systems:

- Command + Option + Shift + S
- Control + Option + Shift + S

These can be customised in the Blender Keymap preferences or by right-clicking on the entry at the bottom of the `File` menu.







## Preferences

- `Path` sets the location for versioned files
	- `/` = a folder alongside the project using the project name
	- Relative and absolute paths can also be used, the default is `//_Archive`

- `Separator` allows for custom text between the original project name and the serial number or date and time stamp
	- The default is simply a dash `-`, which will result in `ProjectName-XXXX`

- `Type ` switches between the available number options
	- `Serial Number` = automatically incrementing version number based on previously saved versions in the specified path, starting at 0000
	- `Date and Time` = current date and time using YYYY-MM-DD-HH-MM-SS format








## Notes

- This add-on is provided as-is with no warranty or guarantee regarding suitability, security, safety, or otherwise. Use at your own risk.
