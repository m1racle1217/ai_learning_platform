Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
shell.CurrentDirectory = root

command = "cmd /c pyw -3 scripts\start_app.py || pythonw scripts\start_app.py || py -3 scripts\start_app.py || python scripts\start_app.py"
shell.Run command, 0, False
