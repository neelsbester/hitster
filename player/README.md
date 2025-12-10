# Hitster Player 🎵

A web-based QR code scanner that plays Spotify tracks from your Hitster cards.

## Features

- 📷 **QR Code Scanning** - Uses your device camera to scan cards
- 🎵 **Spotify Playback** - Controls any Spotify Connect device
- 📱 **PWA Ready** - Install on your phone for a native app experience
- 🔊 **Multi-device** - Play music on any speaker connected to Spotify

## Requirements

- **Spotify Premium** - Required for playback control via API
- **Modern Browser** - Chrome, Safari, Firefox, or Edge
- **Camera Access** - For QR code scanning

## Setup

### 1. Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create app"
3. Fill in the details:
   - App name: `Hitster Player`
   - App description: `QR code scanner for Hitster game`
   - Redirect URI: `http://localhost:5173/callback`
4. Click "Save"
5. Copy your **Client ID**

### 2. Configure the Player

Open `src/auth.js` and replace `YOUR_SPOTIFY_CLIENT_ID` with your Client ID:

```javascript
const CLIENT_ID = 'your_actual_client_id_here';
```

### 3. Install Dependencies

```bash
cd player
npm install
```

### 4. Run the Development Server

```bash
npm run dev
```

The player will be available at `http://localhost:5173`

### 5. Connect from Mobile (Optional)

To test on your phone:

1. Find your computer's local IP address
2. Add `http://YOUR_IP:5173/callback` to your Spotify app's redirect URIs
3. Open `http://YOUR_IP:5173` on your phone

## Usage

1. **Login** - Click "Connect with Spotify" and authorize the app
2. **Select Device** - Choose where you want the music to play (speaker, phone, etc.)
3. **Scan Cards** - Point your camera at a Hitster QR code
4. **Play!** - The song starts playing automatically

### Game Flow

1. Player draws a card
2. Host scans the QR code with this app
3. Music plays - players guess the year
4. Tap "Reveal Song Info" to see the answer

## Deployment

For production use, build and deploy:

```bash
npm run build
```

Deploy the `dist` folder to any static hosting:
- [Vercel](https://vercel.com)
- [Netlify](https://netlify.com)
- [GitHub Pages](https://pages.github.com)
- [Cloudflare Pages](https://pages.cloudflare.com)

**Important**: Update the redirect URI in your Spotify app dashboard to match your production URL.

## Troubleshooting

### "No devices found"
- Open Spotify on your phone, computer, or speaker
- Make sure you're logged into the same Spotify account

### "Camera permission denied"
- Check browser settings and allow camera access
- On iOS, you may need to use Safari

### "Premium required"
- Spotify playback control requires a Premium subscription
- The API won't work with free accounts

### QR codes not scanning
- Ensure good lighting
- Hold the card steady
- Try moving closer or further from the camera

## Tech Stack

- **Vite** - Build tool and dev server
- **html5-qrcode** - Camera-based QR scanning
- **Spotify Web API** - Playback control

## License

Part of the Hitster Card Generator project.

