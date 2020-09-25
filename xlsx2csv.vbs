Dim fso: set fso = CreateObject("Scripting.FileSystemObject")
' directory in which this script is currently running
CurrentDirectory = fso.GetAbsolutePathName(".")

Set folder = fso.GetFolder(CurrentDirectory)

For each file In folder.Files

If fso.GetExtensionName(file) = "xlsx" Then

		pathOut = fso.BuildPath(CurrentDirectory, fso.GetBaseName(file)+".csv")

		Dim oExcel
		Set oExcel = CreateObject("Excel.Application")
		Dim oBook
		Set oBook = oExcel.Workbooks.Open(file)
		oBook.SaveAs pathOut, 6
		oBook.Close False
		oExcel.Quit
End If
Next