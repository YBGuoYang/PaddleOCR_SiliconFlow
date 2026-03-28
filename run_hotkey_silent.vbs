Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

BaseDir = FSO.GetParentFolderName(WScript.ScriptFullName)
PythonwPath = FSO.BuildPath(BaseDir, ".venv\Scripts\pythonw.exe")
ScriptPath = FSO.BuildPath(BaseDir, "scripts\screenshot_ocr_hotkey.py")

If FSO.FileExists(PythonwPath) Then
    Command = """" & PythonwPath & """ """ & ScriptPath & """"
Else
    Command = "pythonw """ & ScriptPath & """"
End If

WshShell.CurrentDirectory = BaseDir
WshShell.Run Command, 0, False
