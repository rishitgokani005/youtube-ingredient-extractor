from yt_dlp import YoutubeDL

url = 'https://www.youtube.com/watch?v=N8XBGuHrzro'
opts = {'listformats': True, 'quiet': False}
with YoutubeDL(opts) as ydl:
    try:
        ydl.extract_info(url, download=False)
    except Exception as e:
        print('ERROR:', e)
