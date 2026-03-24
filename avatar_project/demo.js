#!/usr/bin/env node
/**
 * Demo script - Shows Lux controlling the avatar
 */

const { playAnimation, startTalking, setExpression } = require('./bridge/lux_bridge');
const WebSocket = require('ws');

const WS_URL = 'ws://localhost:8765';

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
  console.log('🎭 Connecting to avatar...');
  
  const ws = new WebSocket(WS_URL);
  
  await new Promise((resolve, reject) => {
    ws.on('open', resolve);
    ws.on('error', reject);
    setTimeout(() => reject(new Error('Timeout')), 5000);
  });
  
  console.log('✅ Connected! Starting demo...\n');
  
  function send(type, data) {
    ws.send(JSON.stringify({ type, ...data }));
  }
  
  // Demo sequence
  console.log('1. 👋 Waving hello...');
  send('animation', { animation: 'wave' });
  await wait(2000);
  
  console.log('2. 😊 Happy expression...');
  send('expression', { expression: 'happy' });
  send('animation', { animation: 'idle' });
  await wait(1500);
  
  console.log('3. 🗣️  Starting to talk...');
  send('talk', { isTalking: true, duration: 4000 });
  send('animation', { animation: 'talk' });
  await wait(4000);
  
  console.log('4. 🚶 Walking...');
  send('animation', { animation: 'walk' });
  await wait(2000);
  
  console.log('5. 🪑 Sitting down...');
  send('animation', { animation: 'sit' });
  await wait(2000);
  
  console.log('6. 😢 Sad expression...');
  send('expression', { expression: 'sad' });
  await wait(1500);
  
  console.log('7. 💃 Dancing!');
  send('expression', { expression: 'happy' });
  send('animation', { animation: 'dance' });
  await wait(3000);
  
  console.log('8. 😐 Back to neutral...');
  send('expression', { expression: 'neutral' });
  send('animation', { animation: 'idle' });
  
  console.log('\n✨ Demo complete!');
  console.log('The avatar is now ready for your commands.');
  
  ws.close();
  process.exit(0);
}

demo().catch(err => {
  console.error('❌ Demo failed:', err.message);
  console.log('Make sure the avatar app is running: npm start');
  process.exit(1);
});