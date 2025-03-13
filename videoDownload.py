import subprocess
import os
import re

def videoDownload(URL):
    
    isDownloaded = False
    outputPath = "songs/%(title)s.%(ext)s"

    commandGetFilename = [
        'yt-dlp', 
        '--get-filename',
        "-o",
        "%(title)s.%(ext)s",  
        URL
    ]
    
    try:
        result = subprocess.run(commandGetFilename, capture_output=True, text=True, check=True)
        
        videoFilename = result.stdout.strip()
        print("vidéo "+videoFilename)
        videoFilename = re.sub(r"\.[^.]+$", ".mp3", videoFilename)
        if os.path.exists(f"songs/{videoFilename}"):
            isDownloaded = True
            

        command_download = [
            'yt-dlp',
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--verbose',
            '-o', outputPath,
            URL
        ]

        if not isDownloaded:
            subprocess.run(command_download, check=True)
            print("déjà download")
        
        filePath = os.path.join("songs", videoFilename)
        names = re.match(r"^(.*?)\s*[-|–|—｜]\s*(.*?)(\.\w{2,4})?$", videoFilename)
        if names:
            artistName = names.group(1)
            title = names.group(2)
        else :
            artistName = "Unknown"
            title = videoFilename


        return filePath , artistName, title
        
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de yt-dlp: {e}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

