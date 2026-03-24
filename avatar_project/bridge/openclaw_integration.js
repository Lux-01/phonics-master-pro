// OpenClaw Avatar Integration
// Add this to OpenClaw to enable avatar animation during conversations

const { avatar } = require('./avatar_controller');

// Animation patterns for different message types
const ANIMATION_PATTERNS = {
  // Greetings trigger wave
  greeting: {
    patterns: [/^(hey|hi|hello|yo|sup|greetings|what'?s up|howdy)/i],
    animation: 'wave',
    duration: 1500
  },
  
  // Thinking/process indicators
  thinking: {
    patterns: [/(thinking|let me check|processing|analyzing|searching)/i],
    animation: 'idle',
    expression: 'neutral'
  },
  
  // Success states
  success: {
    patterns: [/(✅|success|complete|done|loaded|found|ready)/i],
    animation: 'wave',
    expression: 'happy'
  },
  
  // Errors
  error: {
    patterns: [/(❌|error|failed|cannot|unable|sorry)/i],
    animation: 'idle',
    expression: 'sad'
  },
  
  // Goodbye
  goodbye: {
    patterns: [/(bye|goodbye|see ya|later|talk soon)/i],
    animation: 'wave',
    duration: 2000
  },
  
  // Questions
  question: {
    patterns: [/(\?$|what|how|why|when|where|who|can you)/],
    animation: 'idle',
    headTilt: true
  }
};

/**
 * Analyze message and trigger appropriate animation
 * Call this before/after sending a message
 */
function animateForMessage(message, isResponse = true) {
  if (!avatar.connected) {
    // Silently skip if avatar not connected
    return;
  }
  
  const msg = message.toLowerCase();
  let matched = false;
  
  // Check each pattern
  for (const [type, config] of Object.entries(ANIMATION_PATTERNS)) {
    for (const pattern of config.patterns) {
      if (pattern.test(msg)) {
        console.log(`[Avatar] Pattern matched: ${type}`);
        
        if (isResponse && type === 'greeting') {
          // Short wave for greetings
          avatar.playAnimation('wave');
        } else if (isResponse) {
          // Full talk animation for responses
          const words = message.split(/\s+/).length;
          const duration = Math.min(5000, Math.max(2000, words * 250));
          avatar.talk(duration);
        } else {
          // Incoming message - just idle with expression
          if (config.expression) {
            avatar.setExpression(config.expression);
          }
          if (config.animation) {
            avatar.playAnimation(config.animation);
          }
        }
        
        matched = true;
        break;
      }
    }
    if (matched) break;
  }
  
  // Default: talk for any response
  if (!matched && isResponse) {
    const words = message.split(/\s+/).length;
    const duration = Math.min(5000, Math.max(1500, words * 200));
    avatar.talk(duration);
  }
}

/**
 * Wrap a function to animate during execution
 */
function withAnimation(fn, loadingMsg = 'Processing...') {
  return async function(...args) {
    // Connect if not already
    if (!avatar.connected) {
      try {
        await avatar.connect();
      } catch(e) {
        // Continue without avatar
        return await fn(...args);
      }
    }
    
    // Show thinking state
    avatar.setExpression('neutral');
    avatar.playAnimation('idle');
    console.log(`[Avatar] ${loadingMsg}`);
    
    // Execute the function
    const startTime = Date.now();
    const result = await fn(...args);
    const duration = Date.now() - startTime;
    
    // Brief pause then respond
    setTimeout(() => {
      if (typeof result === 'string') {
        animateForMessage(result, true);
      } else {
        avatar.playAnimation('idle');
      }
    }, 300);
    
    return result;
  };
}

/**
 * Send a message with avatar animation
 */
async function sendWithAvatar(message, channel = null) {
  // Connect if needed
  if (!avatar.connected) {
    try {
      await avatar.connect();
    } catch(e) {
      console.log('[Avatar] Not connected, sending message without animation');
    }
  }
  
  // Trigger animation
  animateForMessage(message, true);
  
  // Send actual message (implement based on your OpenClaw setup)
  console.log('[Avatar] Sending:', message.substring(0, 50) + '...');
  
  return message;
}

// Start the avatar bridge
async function startAvatarBridge() {
  console.log('[Avatar] Starting bridge...');
  
  try {
    await avatar.connect();
    
    // Welcome animation
    setTimeout(() => {
      avatar.playAnimation('wave');
      setTimeout(() => {
        avatar.playAnimation('idle');
      }, 1500);
    }, 1000);
    
    console.log('[Avatar] Bridge ready - Lux will animate during conversations');
    
  } catch(e) {
    console.log('[Avatar] Bridge not started:', e.message);
    console.log('[Avatar] Avatar will not animate (Electron app not running)');
  }
}

// Export
module.exports = {
  avatar,
  animateForMessage,
  withAnimation,
  sendWithAvatar,
  startAvatarBridge,
  ANIMATION_PATTERNS
};

// Auto-start if run directly
if (require.main === module) {
  startAvatarBridge();
}