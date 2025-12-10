/**
 * Spotify Player Module
 * 
 * Controls Spotify playback via Web API.
 * Can play music on any Spotify Connect device.
 */

const API_BASE = 'https://api.spotify.com/v1';

export class SpotifyPlayer {
  /**
   * Create a new Spotify player controller
   * @param {string} accessToken - Spotify access token
   */
  constructor(accessToken) {
    this.token = accessToken;
    this.selectedDeviceId = null;
    this.currentTrack = null;
    this.isPlaying = false;
  }

  /**
   * Make an authenticated API request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Response>}
   */
  async apiRequest(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    // Handle common errors
    if (response.status === 401) {
      throw new Error('Token expired. Please log in again.');
    }

    if (response.status === 403) {
      throw new Error('Premium required for playback control.');
    }

    if (response.status === 404) {
      throw new Error('No active device found. Open Spotify on a device first.');
    }

    return response;
  }

  /**
   * Get available playback devices
   * @returns {Promise<Array>} List of available devices
   */
  async getDevices() {
    const response = await this.apiRequest('/me/player/devices');
    
    if (!response.ok) {
      throw new Error('Failed to get devices');
    }

    const data = await response.json();
    return data.devices || [];
  }

  /**
   * Set the target device for playback
   * @param {string} deviceId - Spotify device ID
   */
  setDevice(deviceId) {
    this.selectedDeviceId = deviceId;
  }

  /**
   * Transfer playback to selected device
   * @param {string} deviceId - Device ID to transfer to
   * @param {boolean} play - Whether to start playing immediately
   */
  async transferPlayback(deviceId, play = false) {
    const response = await this.apiRequest('/me/player', {
      method: 'PUT',
      body: JSON.stringify({
        device_ids: [deviceId],
        play: play
      })
    });

    if (!response.ok && response.status !== 204) {
      throw new Error('Failed to transfer playback');
    }

    this.selectedDeviceId = deviceId;
  }

  /**
   * Play a Spotify track
   * @param {string} spotifyUri - Spotify track URI (spotify:track:xxx)
   * @param {string} deviceId - Optional device ID (uses selected device if not provided)
   */
  async play(spotifyUri, deviceId = null) {
    const targetDevice = deviceId || this.selectedDeviceId;
    
    let endpoint = '/me/player/play';
    if (targetDevice) {
      endpoint += `?device_id=${targetDevice}`;
    }

    const response = await this.apiRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify({
        uris: [spotifyUri]
      })
    });

    if (!response.ok && response.status !== 204) {
      const errorText = await response.text();
      console.error('Play error:', response.status, errorText);
      
      if (response.status === 404) {
        throw new Error('No active device. Open Spotify on your device first.');
      }
      throw new Error('Failed to start playback');
    }

    this.isPlaying = true;
    
    // Extract track ID and fetch track info
    const trackId = spotifyUri.split(':')[2];
    this.currentTrack = await this.getTrackInfo(trackId);
    
    return this.currentTrack;
  }

  /**
   * Pause playback
   */
  async pause() {
    let endpoint = '/me/player/pause';
    if (this.selectedDeviceId) {
      endpoint += `?device_id=${this.selectedDeviceId}`;
    }

    const response = await this.apiRequest(endpoint, {
      method: 'PUT'
    });

    if (!response.ok && response.status !== 204) {
      throw new Error('Failed to pause playback');
    }

    this.isPlaying = false;
  }

  /**
   * Resume playback
   */
  async resume() {
    let endpoint = '/me/player/play';
    if (this.selectedDeviceId) {
      endpoint += `?device_id=${this.selectedDeviceId}`;
    }

    const response = await this.apiRequest(endpoint, {
      method: 'PUT'
    });

    if (!response.ok && response.status !== 204) {
      throw new Error('Failed to resume playback');
    }

    this.isPlaying = true;
  }

  /**
   * Toggle play/pause
   * @returns {boolean} New playing state
   */
  async togglePlayback() {
    if (this.isPlaying) {
      await this.pause();
    } else {
      await this.resume();
    }
    return this.isPlaying;
  }

  /**
   * Get current playback state
   * @returns {Promise<Object|null>} Current playback state or null if nothing playing
   */
  async getPlaybackState() {
    const response = await this.apiRequest('/me/player');
    
    if (response.status === 204) {
      return null; // No active playback
    }

    if (!response.ok) {
      throw new Error('Failed to get playback state');
    }

    return response.json();
  }

  /**
   * Get track information
   * @param {string} trackId - Spotify track ID
   * @returns {Promise<Object>} Track information
   */
  async getTrackInfo(trackId) {
    const response = await this.apiRequest(`/tracks/${trackId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get track info');
    }

    const track = await response.json();
    
    // Extract useful info
    return {
      id: track.id,
      uri: track.uri,
      name: track.name,
      artists: track.artists.map(a => a.name),
      artistString: track.artists.map(a => a.name).join(', '),
      album: track.album.name,
      albumArt: track.album.images[0]?.url || null,
      albumArtSmall: track.album.images[2]?.url || track.album.images[0]?.url || null,
      year: this.extractYear(track.album.release_date),
      durationMs: track.duration_ms,
      previewUrl: track.preview_url
    };
  }

  /**
   * Extract year from release date
   * @param {string} releaseDate - Release date in YYYY-MM-DD or YYYY format
   * @returns {number|null}
   */
  extractYear(releaseDate) {
    if (!releaseDate) return null;
    const year = parseInt(releaseDate.substring(0, 4), 10);
    return isNaN(year) ? null : year;
  }

  /**
   * Get the current user's profile
   * @returns {Promise<Object>} User profile
   */
  async getUserProfile() {
    const response = await this.apiRequest('/me');
    
    if (!response.ok) {
      throw new Error('Failed to get user profile');
    }

    return response.json();
  }

  /**
   * Set playback volume
   * @param {number} volumePercent - Volume level (0-100)
   */
  async setVolume(volumePercent) {
    const volume = Math.max(0, Math.min(100, Math.round(volumePercent)));
    
    let endpoint = `/me/player/volume?volume_percent=${volume}`;
    if (this.selectedDeviceId) {
      endpoint += `&device_id=${this.selectedDeviceId}`;
    }

    const response = await this.apiRequest(endpoint, {
      method: 'PUT'
    });

    if (!response.ok && response.status !== 204) {
      throw new Error('Failed to set volume');
    }
  }
}

/**
 * Get device type icon name based on device type
 * @param {string} type - Spotify device type
 * @returns {string} Icon identifier
 */
export function getDeviceIcon(type) {
  const icons = {
    'computer': 'computer',
    'smartphone': 'phone',
    'tablet': 'tablet',
    'speaker': 'speaker',
    'tv': 'tv',
    'avr': 'speaker',
    'stb': 'tv',
    'audio_dongle': 'speaker',
    'game_console': 'gamepad',
    'cast_video': 'cast',
    'cast_audio': 'cast',
    'automobile': 'car',
    'unknown': 'device'
  };
  
  return icons[type?.toLowerCase()] || 'device';
}

