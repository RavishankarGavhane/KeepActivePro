Dim objShell, lngMinutes, boolValid
Set objShell = CreateObject("WScript.Shell")

' Prompt the user to enter the duration in minutes
lngMinutes = InputBox("KeepActivePro! How long do you want to keep your system awake?" & _
                      Replace(Space(5), " ", vbNewLine) & _
                      "Enter minutes:", "Awake Duration") ' Replace 5 spaces with new lines

If lngMinutes = vbEmpty Then
    ' If the user cancels the input, do nothing
Else
    On Error Resume Next
    Err.Clear
    boolValid = False
    lngMinutes = CLng(lngMinutes) ' Convert input to Long (numeric)

    If Err.Number = 0 Then ' Check if input is numeric
        If lngMinutes > 0 Then ' Check if input is greater than zero
            For i = 1 To lngMinutes
                WScript.Sleep 60000 ' 60 seconds
                objShell.SendKeys "{SCROLLLOCK 2}" ' Simulate Scroll Lock key press
            Next
            boolValid = True
            MsgBox "Forced awake time over. Back to normal routine.", vbOKOnly + vbInformation, "Task Completed"
        End If
    End If

    On Error GoTo 0
    If boolValid = False Then
        MsgBox "Incorrect input, script won't run" & vbNewLine & _
               "You can only enter a numeric value greater than zero.", vbOKOnly + vbCritical, "Task Failed"
    End If
End If

Set objShell = Nothing
WScript.Quit 0