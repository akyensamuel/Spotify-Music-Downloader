# 🚀 Vercel Deployment Guide

This guide will help you deploy your Spotify Playlist Downloader to Vercel with serverless audio processing capabilities.

## ⚡ Quick Setup

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel --prod
```

## 🔧 Detailed Configuration

### Step 1: Prepare Your Environment

1. **Update your `.env` file** with production values:
   ```bash
   SECRET_KEY=your-super-secret-production-key
   DEBUG=False
   ALLOWED_HOSTS=.vercel.app,your-custom-domain.com
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ```

2. **Install additional dependencies** for Vercel:
   ```bash
   pip install -r requirements-vercel.txt
   ```

### Step 2: Configure Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Import your GitHub repository
3. Set up environment variables in Settings > Environment Variables:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.vercel.app`

### Step 3: Deploy

#### Option A: GitHub Integration (Recommended)
1. Push your code to GitHub
2. Connect repository to Vercel
3. Automatic deployments on push

#### Option B: Direct Deploy
```bash
# From project root
vercel --prod
```

## 🎵 Audio Processing Features

### Serverless Functions
- **`/api/download/playlist`** - Extracts Spotify playlist metadata
- **`/api/download/audio`** - Downloads and converts YouTube audio to MP3

### Processing Capabilities
- ✅ Real FFmpeg audio conversion (using yt-dlp + FFmpeg)
- ✅ Multiple quality options (128, 192, 320 kbps)
- ✅ Automatic format conversion to MP3
- ✅ File size optimization for serverless limits

### Limitations & Optimizations
- **Max execution time:** 10 seconds (Hobby), 300 seconds (Pro)
- **Max file size:** 50MB per download (configurable)
- **Memory limit:** 1024MB per function
- **Timeout handling:** Automatic retries for failed downloads

## 🔐 Security Configuration

### Environment Variables
Set these in Vercel Dashboard > Settings > Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SPOTIFY_CLIENT_ID` | Your Spotify App Client ID | `abc123def456` |
| `SPOTIFY_CLIENT_SECRET` | Your Spotify App Client Secret | `secret123456` |
| `SECRET_KEY` | Django secret key (generate new) | `super-secret-key-here` |
| `DEBUG` | Set to False for production | `False` |
| `ALLOWED_HOSTS` | Allowed domain names | `.vercel.app,yourdomain.com` |

### HTTPS Configuration
Vercel automatically provides HTTPS certificates. The app is configured to:
- Force HTTPS in production
- Set secure cookies
- Handle SSL proxy headers

## 🛠️ Troubleshooting

### Common Issues

**1. "Module not found" errors**
- Ensure all dependencies are in `requirements-vercel.txt`
- Check Python version compatibility (Vercel uses Python 3.9)

**2. "Function timeout" errors**
- Large files may exceed serverless limits
- Consider implementing file size checks
- Use Pro plan for longer execution times

**3. "FFmpeg not found" errors**
- Vercel includes FFmpeg by default in Python runtime
- Check yt-dlp configuration in `api/download/audio.py`

**4. "CORS" errors**
- Check CORS headers in serverless functions
- Verify API endpoint URLs in frontend

### Debug Commands
```bash
# Test locally with Vercel CLI
vercel dev

# Check function logs
vercel logs [deployment-url]

# Test API endpoints
curl -X POST https://your-app.vercel.app/api/download/playlist \
  -H "Content-Type: application/json" \
  -d '{"playlist_url": "spotify:playlist:..."}'
```

## 🎯 Performance Optimization

### Frontend Optimizations
- Client-side folder selection (File System Access API)
- Lazy loading of playlist tracks
- Progress tracking for downloads
- Error handling and retry logic

### Backend Optimizations
- Efficient yt-dlp configuration
- File size limits to prevent timeouts
- Memory-optimized audio processing
- Base64 encoding for binary data transfer

## 📊 Monitoring

### Vercel Analytics
Enable in Dashboard > Analytics for:
- Page views and user engagement
- Function execution metrics
- Error tracking
- Performance monitoring

### Custom Monitoring
The app includes:
- Download success/failure tracking
- Processing time measurements
- Error logging to console

## 🚀 Going Live

### Custom Domain (Optional)
1. Go to Vercel Dashboard > Settings > Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `ALLOWED_HOSTS` environment variable

### SSL Certificate
- Automatically provided by Vercel
- Includes your custom domain
- Auto-renewal

## 📈 Scaling Considerations

### Vercel Limits
- **Hobby Plan:** 100GB bandwidth, 100 GB-hrs execution time
- **Pro Plan:** 1TB bandwidth, unlimited execution time
- **Team Plan:** Advanced features and higher limits

### Upgrade Triggers
Consider upgrading when you hit:
- Function timeout limits (need longer processing)
- Bandwidth limits (many users downloading)
- Execution time limits (heavy usage)

## 🔄 Updates and Maintenance

### Automatic Updates
- Push to GitHub → Auto-deploy to Vercel
- Environment variables persist across deployments
- Zero-downtime deployments

### Manual Updates
```bash
# Update dependencies
pip install -U yt-dlp spotipy

# Test locally
python manage.py runserver

# Deploy
vercel --prod
```

## 📋 Pre-Deployment Checklist

- [ ] Environment variables configured in Vercel
- [ ] Spotify API credentials working
- [ ] Test playlist loading locally
- [ ] Test audio download functionality
- [ ] Check file size limits and timeouts
- [ ] Verify CORS configuration
- [ ] Test with various playlist sizes
- [ ] Confirm HTTPS redirects work
- [ ] Custom domain configured (if applicable)

---

**🎉 Your Spotify Downloader is now ready for Vercel deployment!**

The setup provides:
- ⚡ Serverless audio processing with real FFmpeg conversion
- 🎵 Support for high-quality MP3 downloads (128/192/320 kbps)
- 📁 Client-side folder selection for modern browsers
- 🔒 Secure HTTPS deployment with environment variable management
- 📊 Built-in monitoring and error handling
- 🌍 Global CDN distribution through Vercel Edge Network
