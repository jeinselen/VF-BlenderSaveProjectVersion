# VF Save Version

Saves the current Blender project in a subfolder or other directory path with a serial number or date and time using compression and linked asset remapping. Helps keep the root project directory clean even an artist is obsessive about saving progress as separate versions.

![screenshot of the successfully saved new version popup window in the Blender user interface](images/banner.jpg)







## Installation and Usage

- Download [VF_saveVersion.py](https://raw.githubusercontent.com/jeinselen/VF-BlenderSaveVersion/main/VF_saveVersion.py)
- Open Blender Preferences and navigate to the "Add-ons" tab
- Install and enable the add-on
- Adjust the versioning preferences as needed

The default settings will work as-is; saving the current project to an "_Archive" folder alongside the project file, with a new version number appended each time the save version command is used. The versioned files use compression to reduce `.blend` file size and have linked asset remapping enabled.

Default keyboard shortcuts are included for MacOS, Linux, and Windows systems:

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
  - `Alphanumeric` = major/minor versioning using number + character format (by default, `001a`, `001b`, `001c` ... `002a` etcetera)
- `Digits` adjusts the zero padding for both `Serial Number` and `Alphanumeric` formats
- `Confirmation Popup` enables a small confirmation panel with the version output path when the script completes (it will always display success in the status bar)

The `Alphanumeric` type is unique; instead of saving a compressed copy with incremented version number, it saves the current project with a new alphanumeric serial and then moves the previous project file into the specified location. It will not automatically compress anything, instead relying on whatever compression setting the project file is currently using.

It also has two options when saving a new version. When starting from `001c`, a minor version would be `001d` whereas a major version would be `002a`

The keyboard shortcut for a minor version increment is the same as other version types. The keyboard shortcut for a major version increment is tested in MacOS, but Linux and Windows systems may require manual customisation:

- Command + Option + Control + Shift + S








## Notes

- This add-on is provided as-is with no warranty or guarantee regarding suitability, security, safety, or otherwise. Use at your own risk.
