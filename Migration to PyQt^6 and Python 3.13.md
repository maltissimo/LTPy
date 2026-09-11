 # Migration Plan: PyQt5 & Python 3.9 -> PyQt6 & Python 3.13 #
 ____________________________
This plan is structured to tackle one major change at a time, making debugging much easier. 
The recommended order  is:
1. Migrate from PyQt5 to PyQt6 while still on Python 3.9.
2. Once the application is stable on PyQt6, migrate from Python 3.9 to Python 3.13.
[GUI_base.ui](GUI_base.ui)
## Phase 0: Preparation (Essential First Steps)##
1. Backup Your Project: Before starting, ensure your current working code is saved.
The best way is to commit all your changes to your Git repository:
``
git add .
git commit -m "Pre-migration snapshot"
``
2. Create a requirements.txt file: This will help you reinstall your project's dependencies in 
the new environment. From your current working environment:
``
pip freeze > requirements.txt
``
3. Create a New Virtual Environment: Do not perform the migration in your existing environment. 
This keeps your current setup safe.

``
# Create a venv using your current Python 3.9
python3.9 -m venv venv_pyqt6
# Activate it
source venv_pyqt6/bin/activate
``

# Phase 1: Migrate from PyQt5 to PyQt6 (on Python 3.9) #
In this phase, you will get the application running with PyQt6. All work should be done inside
the new venv_pyqt6 environment.
1. Install PyQt6 and Tools:
``
pip install PyQt6 pyqt6-tools
``
2. Update Imports: This is the most common change. Go through all your Python files and replace
PyQt5 with PyQt6.
- Change: from PyQt5.QtWidgets import ...
- To: from PyQt6.QtWidgets import ...

- Change: from PyQt5.QtCore import ...
- To: from PyQt6.QtCore import ...

- Change: from PyQt5.QtGui import ...
- To: from PyQt6.QtGui import ...
## 3.Update Enum Namespacing: ##
PyQt6 moved many enums from the global Qt namespace into their own specific classes. 
This is the second most common breaking change.
- *Alignment*:
  - Change: Qt.AlignCenter
  - To: Qt.AlignmentFlag.AlignCenter
- *Aspect Ratio & Transformation*:
  - Change: Qt.KeepAspectRatio
  - To: Qt.AspectRatioMode.KeepAspectRatio
  - Change: Qt.SmoothTransformation
  - To: Qt.TransformationMode.SmoothTransformation
- *QTextCursor:*
  - Change: QTextCursor.End
  - To: QTextCursor.MoveOperation.End
  - QMessageBox Buttons: The bitwise OR | still works, so QMessageBox.Yes | QMessageBox.No
  does not need to change.
  - QFrame Shapes/Shadows: These were already in classes (QFrame.Shape.Box), so they should
  not need changing.
## 4.Update exec_() to exec():## 
The trailing underscore on the exec method has been removed.
- *File: ControlCenter/LTPYapp.py*
  - Change: sys.exit(app.exec_())
  - To: sys.exit(app.exec())
## 5.Re-generate .ui files: ## 
Your CameraViewer_GUI2.py and other GUI files were generated with pyuic5. 
You must regenerate them with pyuic6.
- Find the original .ui files (e.g., CameraViewer_UI2.ui).
- Run the pyuic6 command for each one.
- *Command*: pyuic6 -x YourFile.ui -o YourFile_GUI_PyQt6.py

- *Example*:
``pyuic6 -x Graphics/PyQt_files/Measurements_UI2.ui -o Graphics/Base_Classes_graphics/Measurements_GUI2.py``
- *Note*: After regenerating, you may need to re-apply any manual fixes you made to the generated 
Python files (like the FWHM label width). It is better to fix these in Qt Designer and 
then regenerate.

## 6.Install Other Dependencies:## 
Install the other libraries from your requirements.txt file.
pip install numpy scipy pypylon numba # and any others

## 7.Test Thoroughly: ## 
At this point, run the application and test all functionality. Fix any errors that appear. 
The most common ones will be related to the changes listed above.

# Phase 2: Migrate from Python 3.9 to Python 3.13 #

Once your application is stable with PyQt6 on Python 3.9, you can upgrade the Python 
interpreter.
## 1. Create a New Python 3.13 Virtual Environment: ##
``
# Assuming python3.13 is now available on your system
    python3.13 -m venv venv_py313
``
# Activate it
source venv_py313/bin/activate
## 2.Install All Dependencies: ## 
Use your requirements.txt file, but be prepared for potential issues
``
pip install PyQt6 pyqt6-tools
pip install -r requirements.txt
``
**CRITICAL:** 
The biggest risk in a major Python version jump is dependencies that have not been updated. 
distutils was removed in Python 3.12, and any package that still relies on it for 
installation will fail. You may need to find newer versions of those packages or alternatives.

## 3.Review Deprecation Warnings:## 
Python 3.10, 3.11, and 3.12 introduced new features and deprecated old ones. 
Run your application and pay close attention to any DeprecationWarning messages in the 
console.
- *datetime*: While your code uses datetime.now(), be aware that functions like utcnow() are deprecated. 
It's a good time to ensure all your datetime objects are timezone-aware if needed.
- *Type Hinting*: You can modernize your type hints from Union[int, float] to the cleaner 
int | float. This is optional and won't break your code.

## 4.Test Again: ##
Thoroughly test the application on Python 3.13. The changes are usually less about your direct
code and more about the underlying behavior of libraries and dependencies.
By following this two-phase approach, you isolate the sources of potential errors, making t
he entire migration process much more manageable.