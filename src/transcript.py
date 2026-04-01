from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def extract_video_id(video_url: str) -> str:
    return video_url.split("v=")[-1]


def get_transcript(video_url: str) -> str:
    """
    Retrieves the transcript for a given video URL.

    :param video_url: The URL of the video you want to retrieve the transcript for.
                    (e.g., "https://www.youtube.com/watch?v=VIDEO_ID")
    :return: The transcript of the video as a string, or None if an error occurred.
    """
    
    video_id = extract_video_id(video_url)
    
    try:
        YtApi = YouTubeTranscriptApi()
        transcript_list = YtApi.fetch(video_id, languages=['en'])
        transcript = " ".join(chunk.text for chunk in transcript_list)
        return transcript

    except (TranscriptsDisabled, Exception) as e:
        print(f"Error fetching transcript: {e}")
        return None