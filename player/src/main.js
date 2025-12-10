/**
 * Hitster Player - Main Application
 * 
 * Ties together authentication, QR scanning, and Spotify playback.
 */

import { login, handleCallback, getStoredToken, clearToken } from './auth.js';
import { QRScanner } from './scanner.js';
import { SpotifyPlayer } from './player.js';
import { 
  showToast, 
  showScreen, 
  createDeviceItem, 
  updateNowPlaying,
  updatePlayButton,
  updateRevealButton,
  setDeviceName,
  revealSongInfo
} from './ui.js';

// Storage keys
const DEVICE_KEY = 'hitster_selected_device';

// Application state
let player = null;
let scanner = null;
let selectedDevice = null;
let isYearRevealed = false;

/**
 * Save selected device to localStorage
 */
function saveDevice(device) {
  if (device) {
    localStorage.setItem(DEVICE_KEY, JSON.stringify({
      id: device.id,
      name: device.name,
      type: device.type
    }));
  }
}

/**
 * Get saved device from localStorage
 */
function getSavedDevice() {
  try {
    const saved = localStorage.getItem(DEVICE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

/**
 * Clear saved device from localStorage
 */
function clearSavedDevice() {
  localStorage.removeItem(DEVICE_KEY);
}

/**
 * Initialize the application
 */
async function init() {
  console.log('Hitster Player initializing...');

  // Check for OAuth callback (async for PKCE token exchange)
  try {
    const callbackResult = await handleCallback();
    
    if (callbackResult?.error) {
      console.error('Callback error:', callbackResult.error);
      showToast('Login failed: ' + callbackResult.error, 'error');
      showScreen('login-screen');
      setupLoginHandlers();
      return;
    }

    // If we just got a token from callback, use it
    if (callbackResult?.accessToken) {
      console.log('Got token from callback, initializing player...');
      await initializePlayer(callbackResult.accessToken);
      return;
    }
  } catch (err) {
    console.error('Callback handling error:', err);
    showToast('Authentication error: ' + err.message, 'error');
  }

  // Check for existing stored token
  const token = getStoredToken();
  
  if (token) {
    console.log('Found existing token');
    await initializePlayer(token);
  } else {
    console.log('No token found, showing login screen');
    showScreen('login-screen');
    setupLoginHandlers();
  }
}

/**
 * Set up login screen event handlers
 */
function setupLoginHandlers() {
  const loginBtn = document.getElementById('login-btn');
  if (loginBtn) {
    loginBtn.addEventListener('click', async () => {
      await login();
    });
  }
}

/**
 * Initialize the Spotify player with a token
 * @param {string} token - Spotify access token
 */
async function initializePlayer(token) {
  try {
    player = new SpotifyPlayer(token);
    
    // Verify token by getting user profile
    const user = await player.getUserProfile();
    console.log('Logged in as:', user.display_name);
    
    // Check for saved device - try to restore previous session
    const savedDevice = getSavedDevice();
    if (savedDevice) {
      console.log('Found saved device:', savedDevice.name);
      
      // Verify the device is still available
      const devices = await player.getDevices();
      const deviceStillAvailable = devices.find(d => d.id === savedDevice.id);
      
      if (deviceStillAvailable) {
        // Device is available - go straight to scanning!
        console.log('Saved device still available, resuming session');
        selectedDevice = deviceStillAvailable;
        player.setDevice(savedDevice.id);
        showToast(`Resuming on ${savedDevice.name}`, 'success', 2000);
        await startScanning();
        return;
      } else {
        // Device no longer available
        console.log('Saved device no longer available');
        clearSavedDevice();
        showToast('Previous device unavailable. Please select a new one.', 'warning');
      }
    }
    
    // No saved device or device unavailable - show device selection
    showToast(`Welcome, ${user.display_name}!`, 'success');
    await showDeviceSelection();
    
  } catch (error) {
    console.error('Failed to initialize player:', error);
    
    if (error.message.includes('expired') || error.message.includes('401')) {
      clearToken();
      clearSavedDevice();
      showToast('Session expired. Please log in again.', 'warning');
      showScreen('login-screen');
      setupLoginHandlers();
    } else {
      showToast(error.message, 'error');
    }
  }
}

/**
 * Show device selection screen and load devices
 */
async function showDeviceSelection() {
  showScreen('setup-screen');
  setupDeviceHandlers();
  await refreshDevices();
}

/**
 * Set up device selection screen handlers
 */
function setupDeviceHandlers() {
  const refreshBtn = document.getElementById('refresh-devices-btn');
  const startBtn = document.getElementById('start-scanning-btn');
  const devicesList = document.getElementById('devices-list');

  // Remove old listeners by cloning elements
  if (refreshBtn) {
    const newRefreshBtn = refreshBtn.cloneNode(true);
    refreshBtn.parentNode.replaceChild(newRefreshBtn, refreshBtn);
    newRefreshBtn.addEventListener('click', refreshDevices);
  }

  if (startBtn) {
    const newStartBtn = startBtn.cloneNode(true);
    startBtn.parentNode.replaceChild(newStartBtn, startBtn);
    newStartBtn.addEventListener('click', startScanning);
  }

  if (devicesList) {
    const newDevicesList = devicesList.cloneNode(true);
    devicesList.parentNode.replaceChild(newDevicesList, devicesList);
    newDevicesList.addEventListener('click', (e) => {
      const deviceItem = e.target.closest('.device-item');
      if (deviceItem) {
        selectDevice(deviceItem.dataset.deviceId);
      }
    });
  }
}

/**
 * Refresh the list of available Spotify devices
 */
async function refreshDevices() {
  const devicesList = document.getElementById('devices-list');
  const startBtn = document.getElementById('start-scanning-btn');
  
  if (!player) return;

  try {
    devicesList.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">Loading devices...</p>';
    
    const devices = await player.getDevices();
    
    if (devices.length === 0) {
      devicesList.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
          <p>No devices found</p>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
            Open Spotify on a device to make it available
          </p>
        </div>
      `;
      startBtn.disabled = true;
      return;
    }

    // Render devices
    devicesList.innerHTML = devices.map(device => 
      createDeviceItem(device, device.id === selectedDevice?.id)
    ).join('');

    // Auto-select active device if none selected
    if (!selectedDevice) {
      const activeDevice = devices.find(d => d.is_active);
      if (activeDevice) {
        selectDevice(activeDevice.id, devices);
      }
    } else {
      // Re-enable start button if we have a selected device
      startBtn.disabled = false;
    }

  } catch (error) {
    console.error('Failed to get devices:', error);
    devicesList.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--error);">
        <p>Failed to load devices</p>
        <p style="font-size: 0.85rem; margin-top: 0.5rem;">${error.message}</p>
      </div>
    `;
    startBtn.disabled = true;
  }
}

/**
 * Select a device for playback
 * @param {string} deviceId - Device ID to select
 * @param {Array} devices - Optional devices array (to avoid re-fetching)
 */
async function selectDevice(deviceId, devices = null) {
  const startBtn = document.getElementById('start-scanning-btn');
  
  // Get devices if not provided
  if (!devices) {
    devices = await player.getDevices();
  }

  const device = devices.find(d => d.id === deviceId);
  if (!device) return;

  selectedDevice = device;
  player.setDevice(deviceId);
  
  // Save to localStorage for session persistence
  saveDevice(device);

  // Update UI
  document.querySelectorAll('.device-item').forEach(item => {
    item.classList.toggle('selected', item.dataset.deviceId === deviceId);
  });

  startBtn.disabled = false;
  showToast(`Selected: ${device.name}`, 'info', 2000);
}

/**
 * Start the scanning interface
 */
async function startScanning() {
  if (!selectedDevice) {
    showToast('Please select a device first', 'warning');
    return;
  }

  showScreen('player-screen');
  setDeviceName(selectedDevice.name);
  setupPlayerHandlers();
  
  // Initialize scanner
  try {
    scanner = new QRScanner('scanner', {
      onScan: handleScan,
      onError: (message) => showToast(message, 'error'),
      cooldownMs: 3000
    });
    
    await scanner.start();
    showToast('Scanner ready!', 'success', 2000);
    
  } catch (error) {
    console.error('Failed to start scanner:', error);
    showToast('Failed to start camera: ' + error.message, 'error');
  }
}

/**
 * Set up player screen handlers
 */
function setupPlayerHandlers() {
  const pauseBtn = document.getElementById('pause-btn');
  const revealBtn = document.getElementById('reveal-btn');
  const changeDeviceBtn = document.getElementById('change-device-btn');

  // Remove old listeners by cloning elements
  if (pauseBtn) {
    const newPauseBtn = pauseBtn.cloneNode(true);
    pauseBtn.parentNode.replaceChild(newPauseBtn, pauseBtn);
    newPauseBtn.addEventListener('click', togglePlayback);
  }

  if (revealBtn) {
    const newRevealBtn = revealBtn.cloneNode(true);
    revealBtn.parentNode.replaceChild(newRevealBtn, revealBtn);
    newRevealBtn.addEventListener('click', handleReveal);
  }

  if (changeDeviceBtn) {
    const newChangeDeviceBtn = changeDeviceBtn.cloneNode(true);
    changeDeviceBtn.parentNode.replaceChild(newChangeDeviceBtn, changeDeviceBtn);
    newChangeDeviceBtn.addEventListener('click', async () => {
      if (scanner) {
        await scanner.stop();
      }
      clearSavedDevice(); // Clear saved device when manually changing
      await showDeviceSelection();
    });
  }
}

/**
 * Handle a successful QR scan
 * @param {string} spotifyUri - Spotify track URI
 */
async function handleScan(spotifyUri) {
  console.log('Playing:', spotifyUri);
  
  // Reset reveal state
  isYearRevealed = false;
  
  try {
    // Show loading state
    updateNowPlaying(null);
    showToast('Loading track...', 'info', 1500);
    
    // Play the track
    const track = await player.play(spotifyUri);
    
    // Update UI
    updateNowPlaying(track, false);
    updatePlayButton(true);
    updateRevealButton(true, false);
    
    showToast('Now playing!', 'success', 2000);
    
  } catch (error) {
    console.error('Playback error:', error);
    showToast(error.message, 'error');
    
    // If device issue, try to help the user
    if (error.message.includes('device') || error.message.includes('No active')) {
      showToast('Device unavailable - tap to refresh', 'warning', 5000);
      
      // Check if device is still available
      try {
        const devices = await player.getDevices();
        const stillAvailable = devices.find(d => d.id === selectedDevice?.id);
        
        if (!stillAvailable) {
          showToast('Device went offline. Open Spotify and try again.', 'error', 5000);
        }
      } catch (e) {
        console.error('Failed to check devices:', e);
      }
    }
  }
}

/**
 * Toggle play/pause
 */
async function togglePlayback() {
  if (!player) return;
  
  try {
    const isPlaying = await player.togglePlayback();
    updatePlayButton(isPlaying);
  } catch (error) {
    console.error('Toggle playback error:', error);
    showToast(error.message, 'error');
  }
}

/**
 * Reveal all song info (album art, title, artist, year)
 */
function handleReveal() {
  isYearRevealed = true;
  revealSongInfo();
  updateRevealButton(true, true);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Handle visibility changes (pause scanning when tab hidden)
document.addEventListener('visibilitychange', () => {
  if (document.hidden && scanner?.running) {
    console.log('Tab hidden, scanner continues in background');
  }
});

// Export for debugging
window.hitsterDebug = {
  getPlayer: () => player,
  getScanner: () => scanner,
  getSelectedDevice: () => selectedDevice,
  getSavedDevice,
  clearSavedDevice,
  clearToken,
  login
};
