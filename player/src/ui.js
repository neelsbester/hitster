/**
 * UI Helper Module
 * 
 * Toast notifications and UI state management.
 */

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type: 'info', 'success', 'error', 'warning'
 * @param {number} duration - Duration in ms (default: 3000)
 */
export function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  // Auto-remove after duration
  setTimeout(() => {
    toast.classList.add('toast-out');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, duration);
}

/**
 * Show a specific screen and hide others
 * @param {string} screenId - ID of the screen to show
 */
export function showScreen(screenId) {
  const screens = document.querySelectorAll('.screen');
  screens.forEach(screen => {
    screen.hidden = screen.id !== screenId;
  });
}

/**
 * Create device list item HTML
 * @param {Object} device - Spotify device object
 * @param {boolean} isSelected - Whether this device is currently selected
 * @returns {string} HTML string
 */
export function createDeviceItem(device, isSelected = false) {
  const iconSvg = getDeviceIconSvg(device.type);
  const activeClass = device.is_active ? 'active' : '';
  const selectedClass = isSelected ? 'selected' : '';
  
  return `
    <div class="device-item ${activeClass} ${selectedClass}" data-device-id="${device.id}">
      ${device.is_active ? '' : ''}
      <div class="device-icon">${iconSvg}</div>
      <div class="device-info">
        <div class="device-item-name">${escapeHtml(device.name)}</div>
        <div class="device-item-type">${device.type}${device.is_active ? ' • Active' : ''}</div>
      </div>
    </div>
  `;
}

/**
 * Get SVG icon for device type
 * @param {string} type - Device type
 * @returns {string} SVG HTML
 */
function getDeviceIconSvg(type) {
  const icons = {
    computer: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
      <line x1="8" y1="21" x2="16" y2="21"/>
      <line x1="12" y1="17" x2="12" y2="21"/>
    </svg>`,
    smartphone: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
      <line x1="12" y1="18" x2="12.01" y2="18"/>
    </svg>`,
    speaker: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
      <circle cx="12" cy="14" r="4"/>
      <line x1="12" y1="6" x2="12.01" y2="6"/>
    </svg>`,
    tv: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="2" y="7" width="20" height="15" rx="2" ry="2"/>
      <polyline points="17 2 12 7 7 2"/>
    </svg>`,
    tablet: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
      <line x1="12" y1="18" x2="12.01" y2="18"/>
    </svg>`,
    default: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <polygon points="10 8 16 12 10 16 10 8"/>
    </svg>`
  };
  
  return icons[type?.toLowerCase()] || icons.default;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Update the now playing display
 * @param {Object} track - Track info from SpotifyPlayer
 * @param {boolean} revealed - Whether to reveal all song info (album art, title, artist, year)
 */
export function updateNowPlaying(track, revealed = false) {
  const placeholder = document.querySelector('.now-playing-placeholder');
  const content = document.querySelector('.now-playing-content');
  
  if (!track) {
    placeholder.hidden = false;
    content.hidden = true;
    return;
  }

  placeholder.hidden = true;
  content.hidden = false;

  // Reset revealed state when showing new track
  content.classList.toggle('revealed', revealed);

  document.getElementById('album-art').src = track.albumArt || '';
  document.getElementById('track-name').textContent = track.name;
  document.getElementById('artist-name').textContent = track.artistString;
  
  const yearEl = document.getElementById('track-year');
  yearEl.textContent = track.year || '???';
}

/**
 * Reveal all song info (album art, title, artist, year)
 */
export function revealSongInfo() {
  const content = document.querySelector('.now-playing-content');
  if (content) {
    content.classList.add('revealed');
  }
}

/**
 * Update play/pause button state
 * @param {boolean} isPlaying - Current playback state
 */
export function updatePlayButton(isPlaying) {
  const pauseIcon = document.getElementById('pause-icon');
  const playIcon = document.getElementById('play-icon');
  const pauseBtn = document.getElementById('pause-btn');
  
  if (pauseIcon && playIcon) {
    pauseIcon.hidden = !isPlaying;
    playIcon.hidden = isPlaying;
  }
  
  if (pauseBtn) {
    pauseBtn.disabled = false;
  }
}

/**
 * Update reveal button visibility
 * @param {boolean} hasTrack - Whether a track is loaded
 * @param {boolean} isRevealed - Whether the year is already revealed
 */
export function updateRevealButton(hasTrack, isRevealed) {
  const revealBtn = document.getElementById('reveal-btn');
  if (revealBtn) {
    revealBtn.hidden = !hasTrack || isRevealed;
  }
}

/**
 * Set the current device name in header
 * @param {string} name - Device name
 */
export function setDeviceName(name) {
  const deviceNameEl = document.getElementById('device-name');
  if (deviceNameEl) {
    deviceNameEl.textContent = name || '---';
  }
}

/**
 * Add loading state to element
 * @param {HTMLElement} element - Element to add loading state to
 */
export function setLoading(element, isLoading) {
  if (isLoading) {
    element.classList.add('loading');
    element.disabled = true;
  } else {
    element.classList.remove('loading');
    element.disabled = false;
  }
}

