const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const WebSocket = require('ws');

// Bridge communication
let bridgeWindow = null;
let wss = null;
let wsClients = [];

// Avatar state
let avatarState = {
  isTalking: false,
  currentAnimation: 'idle',
  position: { x: 0, y: 0 },
  mood: 'neutral'
};

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  
  // Avatar window - transparent, always on top
  const win = new BrowserWindow({
    width: 400,
    height: 600,
    x: width - 420,
    y: height - 620,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    skipTaskbar: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    },
    backgroundColor: '#00000000' // Fully transparent
  });

  win.loadFile(path.join(__dirname, 'renderer.html'));
  
  // Click-through when not interacting
  win.setIgnoreMouseEvents(false);
  
  // Dev tools in dev mode
  if (process.argv.includes('--dev')) {
    win.webContents.openDevTools();
  }

  bridgeWindow = win;
  return win;
}

// WebSocket Bridge Server
function createBridge() {
  wss = new WebSocket.Server({ port: 8765 });
  
  console.log('Bridge server running on ws://localhost:8765');
  
  wss.on('connection', (ws) => {
    console.log('AI connected to avatar bridge');
    wsClients.push(ws);
    
    // Send current state
    ws.send(JSON.stringify({
      type: 'state',
      data: avatarState
    }));
    
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        handleBridgeMessage(data);
      } catch (e) {
        console.error('Bridge message error:', e);
      }
    });
    
    ws.on('close', () => {
      wsClients = wsClients.filter(client => client !== ws);
      console.log('AI disconnected from bridge');
    });
  });
}

// Handle messages from AI
function handleBridgeMessage(data) {
  switch(data.type) {
    case 'animation':
      playAnimation(data.animation);
      break;
    case 'talk':
      startTalking(data.duration);
      break;
    case 'move':
      moveAvatar(data.x, data.y);
      break;
    case 'expression':
      setExpression(data.expression);
      break;
    case 'skeleton':
      updateSkeleton(data.bones);
      break;
    case 'load-avatar':
      loadAvatar(data.path);
      break;
  }
  
  // Broadcast to all clients
  broadcast(data);
}

function broadcast(data) {
  wsClients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(data));
    }
  });
  
  // Also send to renderer
  if (bridgeWindow && !bridgeWindow.isDestroyed()) {
    bridgeWindow.webContents.send('bridge-message', data);
  }
}

function playAnimation(animName) {
  avatarState.currentAnimation = animName;
  broadcast({ type: 'animation', animation: animName });
}

function startTalking(duration = 3000) {
  avatarState.isTalking = true;
  broadcast({ type: 'talk', isTalking: true, duration });
  
  setTimeout(() => {
    avatarState.isTalking = false;
    broadcast({ type: 'talk', isTalking: false });
  }, duration);
}

function moveAvatar(x, y) {
  avatarState.position = { x, y };
  if (bridgeWindow) {
    bridgeWindow.setPosition(x, y);
  }
}

function setExpression(expr) {
  avatarState.mood = expr;
  broadcast({ type: 'expression', expression: expr });
}

function updateSkeleton(bones) {
  broadcast({ type: 'skeleton', bones });
}

function loadAvatar(path) {
  broadcast({ type: 'load-avatar', path });
}

// IPC handlers for renderer
ipcMain.handle('get-avatar-state', () => avatarState);

ipcMain.on('avatar-ready', () => {
  console.log('Avatar renderer ready');
  broadcast({ type: 'ready' });
});

ipcMain.on('animation-complete', (event, animName) => {
  broadcast({ type: 'animation-complete', animation: animName });
});

app.whenReady().then(() => {
  createWindow();
  createBridge();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle certificate errors
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  event.preventDefault();
  callback(true);
});