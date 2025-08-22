/* 
FFmpeg.wasm Implementation
Runs FFmpeg directly in the browser - perfect for hosting
*/

// Add to your HTML head:
// <script src="https://unpkg.com/@ffmpeg/ffmpeg@0.12.10/dist/umd/ffmpeg.js"></script>

class FFmpegProcessor {
    constructor() {
        this.ffmpeg = null;
        this.isLoaded = false;
    }

    async loadFFmpeg() {
        if (this.isLoaded) return;
        
        try {
            const { FFmpeg } = FFmpegWASM;
            this.ffmpeg = new FFmpeg();
            
            // Load FFmpeg with progress callback
            await this.ffmpeg.load({
                coreURL: 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd/ffmpeg-core.js',
                wasmURL: 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd/ffmpeg-core.wasm',
                workerURL: 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd/ffmpeg-core.worker.js'
            });
            
            this.isLoaded = true;
            console.log('✅ FFmpeg loaded successfully');
            return true;
        } catch (error) {
            console.error('❌ Failed to load FFmpeg:', error);
            return false;
        }
    }

    async convertAudioToMp3(audioBlob, quality = '192') {
        if (!this.isLoaded) {
            await this.loadFFmpeg();
        }

        try {
            // Write input file to FFmpeg filesystem
            const inputName = 'input.webm';
            const outputName = 'output.mp3';
            
            await this.ffmpeg.writeFile(inputName, new Uint8Array(await audioBlob.arrayBuffer()));

            // Run FFmpeg conversion
            await this.ffmpeg.exec([
                '-i', inputName,
                '-vn',  // No video
                '-acodec', 'libmp3lame',
                '-ab', `${quality}k`,
                '-ar', '44100',
                outputName
            ]);

            // Read converted file
            const data = await this.ffmpeg.readFile(outputName);
            
            // Clean up
            await this.ffmpeg.deleteFile(inputName);
            await this.ffmpeg.deleteFile(outputName);

            return new Blob([data], { type: 'audio/mpeg' });
        } catch (error) {
            console.error('Conversion error:', error);
            throw error;
        }
    }
}

// Usage in your playlist downloader
async function downloadWithFFmpegWasm(track, quality = '192') {
    const processor = new FFmpegProcessor();
    
    try {
        // 1. Get audio from YouTube (as WebM/MP4)
        const audioBlob = await downloadYouTubeAudio(track);
        
        // 2. Convert to MP3 using FFmpeg.wasm
        const mp3Blob = await processor.convertAudioToMp3(audioBlob, quality);
        
        // 3. Download the converted file
        const fileName = `${track.artist} - ${track.name}.mp3`;
        downloadBlob(mp3Blob, fileName);
        
        return true;
    } catch (error) {
        console.error('Download failed:', error);
        return false;
    }
}
