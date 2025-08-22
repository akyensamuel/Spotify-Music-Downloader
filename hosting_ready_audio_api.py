"""
Audio API view - Hosting-Ready Version (No FFmpeg)
Returns download instructions instead of actual audio files
"""

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def audio_api(request):
    """Handle audio download - returns YouTube links instead of files"""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        search_query = data.get('query', '')
        quality = data.get('quality', '192')
        
        if not search_query:
            return JsonResponse({'success': False, 'error': 'Missing search query'}, status=400)
        
        # Return YouTube search URL instead of actual file
        youtube_search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        
        response_data = {
            'success': True,
            'youtube_url': youtube_search_url,
            'search_query': search_query,
            'quality': quality,
            'message': 'Use a YouTube downloader to get this track',
            'instructions': [
                f"1. Search YouTube for: {search_query}",
                "2. Use yt-dlp or similar tool to download",
                f"3. Convert to MP3 at {quality}kbps quality"
            ]
        }
        
        response = JsonResponse(response_data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)
