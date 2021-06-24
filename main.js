const {app, BrowserWindow} = require('electron')
const path = require('path');

let mainWindow

function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 900,
    height: 650,
    frame: false,
    resizable: false
  });
  //mainWindow.removeMenu()
  mainWindow.loadURL('http://localhost:8000/templates/main_menu.html');
}



app.on('ready', createWindow)
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})

