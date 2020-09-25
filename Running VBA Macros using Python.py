
import win32com.client


xl = win32com.client.Dispatch('Excel.Application')
xl.Visible = 1
wb = xl.Workbooks.Open("C:\\Users\\akmarmu\\Desktop\\FLCP.xlsm") 
xl.Run('first')

xl.Workbooks(1).Close(SaveChanges=0)
xl.Application.Quit()
xl=0


