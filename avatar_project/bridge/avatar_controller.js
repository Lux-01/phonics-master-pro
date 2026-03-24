// Avatar Controller Bridge - Connects OpenClaw to DeskMate Avatar
// Run this alongside the Electron app: node bridge/avatar_controller.js

const WebSocket = require('ws');
const EventEmitter = require('events');

class AvatarController extends EventEmitter {
  constructor() {
    super();
    this.ws = null;
    this.connected = false;
    this.currentAvatar = null;
    this.isTalking = false;
    this.reconnectInterval = 5000;
    this.reconnectAttempts = 0;
    this.maxReconnects = 10;
  }

  async connect() {
    return new Promise((resolve, reject) => {
      console.log('[Avatar] Connecting to ws://localhost:8765...');
      
      this.ws = new WebSocket('ws://localhost:8765');
      
      this.ws.on('open', () => {
        console.log('[Avatar] ✅ Connected to avatar bridge');
        this.connected = true;
        this.reconnectAttempts = 0;
        this.emit('connected');
        
        // Auto-load warrior on connect
        setTimeout(() => {
          this.loadAvatar('/home/skux/.openclaw/workspace/avatar_project/assets/warrior.glb');
        }, 500);
        
        resolve();
      });
      
      this.ws.on('message', (data) => {
        try {
          const msg = JSON.parse(data);
          this.handleMessage(msg);
        } catch(e) {
          console.log('[Avatar] Raw message:', data.toString());
        }
      });
      
      this.ws.on('close', () => {
        console.log('[Avatar] ❌ Disconnected');
        this.connected = false;
        this.emit('disconnected');
        this.attemptReconnect();
      });
      
      this.ws.on('error', (err) => {
        console.log('[Avatar] Error:', err.message);
        if (!this.connected) {
          reject(err);
        }
      });
    });
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnects) {
      console.log('[Avatar] Max reconnects reached. Stopping.');
      return;
    }
    
    this.reconnectAttempts++;
    console.log(`[Avatar] Reconnecting in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts}/${this.maxReconnects})...`);
    
    setTimeout(() => {
      this.connect().catch(() => {});
    }, this.reconnectInterval);
  }

  handleMessage(msg) {
    switch(msg.type) {
      case 'state':
        console.log('[Avatar] State:', msg.data);
        break;
      case 'ready':
        console.log('[Avatar] Renderer ready');
        break;
      case 'animation-complete':
        console.log('[Avatar] Animation complete:', msg.animation);
        if (msg.animation === 'talk') {
          this.isTalking = false;
        }
        break;
      default:
        //console.log('[Avatar] Message:', msg.type);
    }
  }

  send(data) {
    if (this.connected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.log('[Avatar] Not connected, command queued');
    }
  }

  // Core commands
  loadAvatar(path) {
    console.log('[Avatar] Loading:', path);
    this.send({ type: 'load-avatar', path });
    this.currentAvatar = path;
  }

  playAnimation(name) {
    console.log('[Avatar] Animation:', name);
    this.send({ type: 'animation', animation: name });
  }

  talk(duration = 3000) {
    if (this.isTalking) return; // Don't interrupt
    this.isTalking = true;
    console.log('[Avatar] Talking for', duration, 'ms');
    this.send({ type: 'talk', isTalking: true, duration });
    
    setTimeout(() => {
      this.isTalking = false;
    }, duration);
  }

  setExpression(expr) {
    console.log('[Avatar] Expression:', expr);
    this.send({ type: 'expression', expression: expr });
  }

  // Smart animation based on message content
  animateForMessage(message, context = {}) {
    const msg = message.toLowerCase();
    
    // Greetings
    if (/^(hey|hi|hello|yo|sup|greetings|what'?s up)/.test(msg)) {
      this.playAnimation('wave');
      return;
    }
    
    // Thinking/Processing
    if (msg.includes('thinking') || msg.includes('let me') || msg.includes('checking')) {
      this.playAnimation('idle');
      return;
    }
    
    // Success/Positive
    if (msg.includes('✅') || msg.includes('success') || msg.includes('complete') || msg.includes('done')) {
      this.setExpression('happy');
      this.playAnimation('wave');
      return;
    }
    
    // Error/Warning
    if (msg.includes('❌') || msg.includes('error') || msg.includes('failed')) {
      this.setExpression('sad');
      this.playAnimation('idle');
      return;
    }
    
    // Excitement/Discovery
    if (msg.includes('🎉') || msg.includes('found') || msg.includes('amazing') || msg.includes('great')) {
      this.setExpression('happy');
      this.playAnimation('wave');
      return;
    }
    
    // Default: idle with occasional head movement
    this.playAnimation('idle');
  }

  // Response animation - talk while sending message
  async respond(message) {
    // Calculate duration based on message length (slower for longer messages)
    const words = message.split(/\s+/).length;
    const duration = Math.min(5000, Math.max(2000, words * 300));
    
    this.talk(duration);
    
    // Wait for talk to finish before idling
    setTimeout(() => {
      this.playAnimation('idle');
    }, duration + 200);
    
    return duration;
  }
}

// Singleton instance
const avatar = new AvatarController();

// Export for use in other modules
module.exports = { AvatarController, avatar };

// Auto-connect if run directly
if (require.main === module) {
  console.log('=== Avatar Controller ===');
  console.log('Connecting to avatar bridge...');
  console.log('Make sure Electron app is running: npm start');
  console.log('');
  
  avatar.connect()
    .then(() => {
      console.log('\n✅ Ready! Avatar will respond to:');
      console.log('  - Greetings (wave)');
      console.log('  - Responses (talk animation)');
      console.log('  - Success states (wave + happy)');
      console.log('  - Errors (idle + sad)');
      console.log('');
      console.log('Import this module in your OpenClaw scripts to control the avatar programmatically.');
      console.log('');
      console.log('Example:');
      console.log('  const { avatar } = require("./bridge/avatar_controller");');
      console.log('  await avatar.connect();');
      console.log('  await avatar.respond("Hello! I am Lux.");');
      console.log('  avatar.playAnimation("wave");');
    })
    .catch(err => {
      console.log('\n❌ Connection failed:', err.message);
      console.log('Is the Electron app running?');
      console.log('Run: cd avatar_project && npm start');
      process.exit(1);
    });
}
