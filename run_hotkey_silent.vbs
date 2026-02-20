' 静默启动 Screenshot OCR Tool (Hotkey Version)
' 双击此文件将在后台启动程序，不显示终端窗口

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "pythonw scripts\screenshot_ocr_hotkey.py", 0, False
