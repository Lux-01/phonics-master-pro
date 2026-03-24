#!/usr/bin/env node
/**
 * LUX BRIDGE - AI to Avatar Control
 * 
 * This connects me (Lux) to the DesktopMate avatar
 * I can send commands to control animations, expressions, etc.
 */

const WebSocket = require('ws');
const readline = require('readline');

const WS_URL = 'ws://localhost:8765';
let ws = null;
let connected = false;

// Available animations
const ANIMATIONS = ['idle', 'walk', 'sit', 'talk', 'wave', 'dance', 'jump'];
const EXPRESSIONS = ['happy', 'sad', 'angry', 'surprised', 'neutral'];

function connect() {
  console.log('🦞 Connecting to DeskMate avatar...');
  
  ws = new WebSocket(WS_URL);
  
  ws.on('open', () => {
    console.log('✅ Connected to avatar!');
    connected = true;
    showMenu();
  });
  
  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    handleMessage(msg);
  });
  
  ws.on('error', (err) => {
    console.log('❌ Connection error:', err.message);
    console.log('   Is the avatar app running?');
  });
  
  ws.on('close', () => {
    console.log('🔌 Disconnected');
    connected = false;
    setTimeout(connect, 3000);
  });
}

function handleMessage(msg) {
  switch(msg.type) {
    case 'state':
      console.log('📊 Avatar state:', msg.data);
      break;
    case 'animation-complete':
      console.log(`✨ Animation complete: ${msg.animation}`);
      break;
    case 'ready':
      console.log('🎉 Avatar is ready!');
      break;
  }
}

function sendCommand(type, data) {
  if (!connected || !ws) {
    console.log('❌ Not connected to avatar');
    return;
  }
  
  ws.send(JSON.stringify({ type, ...data }));
}

// Animation commands
function playAnimation(name) {
  sendCommand('animation', { animation: name });
  console.log(`🎭 Playing animation: ${name}`);
}

function startTalking(duration = 3000) {
  sendCommand('talk', { isTalking: true, duration });
  console.log('🗣️  Starting talking animation');
}

function setExpression(expression) {
  sendCommand('expression', { expression });
  console.log(`😊 Setting expression: ${expression}`);
}

function updateSkeleton(boneData) {
  sendCommand('skeleton', { bones: boneData });
}

function loadAvatar(path) {
  sendCommand('load-avatar', { path });
  console.log(`📦 Loading avatar from: ${path}`);
}

// Interactive menu
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function showMenu() {
  console.log('\n' + '='.repeat(50));
  console.log('🚀 LUX BRIDGE - Avatar Control');
  console.log('='.repeat(50));
  console.log('Commands:');
  console.log('  1. ANIM <animation>  - Play animation');
  console.log('  2. TALK <seconds>   - Start talking');
  console.log('  3. EXPRESS <mood>   - Set expression');
  console.log('  4. LOAD <path>      - Load GLB file');
  console.log('  5. SKEL <bones>      - Control skeleton');
  console.log('  6. STATUS            - Show connection status');
  console.log('  7. QUIT             - Exit');
  console.log('\nAnimations:', ANIMATIONS.join(', '));
  console.log('Expressions:', EXPRESSIONS.join(', '));
  console.log('='.repeat(50));
  prompt();
}

function prompt() {
  rl.question('\n🦞 Lux> ', (input) => {
    const args = input.trim().split(' ');
    const cmd = args[0].toUpperCase();
    
    switch(cmd) {
      case '1':
      case 'ANIM':
        if (args[1]) playAnimation(args[1].toLowerCase());
        else console.log('Usage: ANIM <animation>');
        break;
      
      case '2':
      case 'TALK':
        const duration = parseInt(args[1]) * 1000 || 3000;
        startTalking(duration);
        break;
      
      case '3':
      case 'EXPRESS':
        if (args[1]) setExpression(args[1].toLowerCase());
        else console.log('Usage: EXPRESS <happy|sad|angry|neutral>');
        break;
      
      case '4':
      case 'LOAD':
        if (args[1]) loadAvatar(args[1]);
        else console.log('Usage: LOAD /path/to/model.glb');
        break;
      
      case '5':
      case 'SKEL':
        // Example: SKEL head 0.5 0 0 0.1 0.2 0.3
        const boneName = args[1] || 'head';
        const boneData = [{
          name: boneName,
          x: parseFloat(args[2]) || 0,
          y: parseFloat(args[3]) || 0,
          z: parseFloat(args[4]) || 0,
          rx: parseFloat(args[5]) || 0,
          ry: parseFloat(args[6]) || 0,
          rz: parseFloat(args[7]) || 0
        }];
        updateSkeleton(boneData);
        console.log(`🦴 Moving ${boneName}`);
        break;
      
      case '6':
      case 'STATUS':
        console.log(`Status: ${connected ? '✅ Connected' : '❌ Disconnected'}`);
        break;
      
      case '7':
      case 'QUIT':
      case 'EXIT':
        console.log('👋 Disconnecting...');
        ws.close();
        rl.close();
        process.exit(0);
        break;
      
      default:
        console.log('❓ Unknown command. Type a number or command name.');
    }
    
    prompt();
  });
}

// Export for programmatic use
module.exports = {
  playAnimation,
  startTalking,
  setExpression,
  loadAvatar,
  updateSkeleton,

  ANIMATIONS,
  EXPRESSIONS
};

// Start if run directly
if (require.main === module) {
  connect();
}