# Test

`python -m pytest .`

Or verbosely

`python -m pytest -s .`

Or

`python -m pytest -v .`

You can do specific files and tests:

`python -m pytest -v test_plugins.py -k "test_plugin_editor" -p no:faulthandler`

Note that `-p no:faulthandler` is included to avoid errors when GUIs are opened.

The Coldpiano render test runs when `COLDPIANO_VST3_PATH` points to a built
Coldpiano VST3 bundle. It skips when the variable is unset and fails if a
configured path does not exist. The Windows build workflow builds and validates
the plugin before running this test against the installed DawDreamer wheel.
That workflow pins the Coldpiano source revision and applies
`.github/patches/coldpiano-juce.patch`; update the pin and patch together when
the upstream plugin is fixed.
