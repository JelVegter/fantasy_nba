import os
import json
import time
import datetime
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional, Sequence

import openai  # noqa: F401
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)

logger = logging.getLogger(__name__)
load_dotenv(override=True)

# Set your OpenAI API key
# openai.api_key = 'YOUR_OPENAI_API_KEY'

# Model and file paths
MODEL_NAME = "gpt-4o"
PROCESSED_VIDEOS_PATH = Path("data/processed_videos")
PROCESSED_VIDEOS_PATH.mkdir(parents=True, exist_ok=True)
TMP_AUDIO_PATH = Path("data/tmp_audio")
TMP_AUDIO_PATH.mkdir(parents=True, exist_ok=True)
TRANSCRIPTS_PATH = Path("data/transcripts")
TRANSCRIPTS_PATH.mkdir(parents=True, exist_ok=True)

DEFAULT_LANGUAGES = ("en", "en-US", "en-GB")


def get_llm(model_name: str) -> ChatOpenAI:
    """Initialize and return a LangChain ChatOpenAI model."""
    return ChatOpenAI(model_name=model_name, temperature=0.0)


@dataclass
class TranscriptResult:
    method: str
    text: str
    segments: List[Dict[str, Any]]


def export_transcript(video_id: str, transcript: TranscriptResult) -> Path:
    """Persist the transcript text and segments for reference."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = {
        "video_id": video_id,
        "exported_at": timestamp,
        "method": transcript.method,
        "text": transcript.text,
        "segments": transcript.segments,
    }
    file_path = TRANSCRIPTS_PATH / f"{video_id}.json"
    with open(file_path, "w") as file:
        json.dump(payload, file, indent=4)
    logger.info("Exported transcript for %s to %s", video_id, file_path)
    return file_path


def _segments_to_text(segments: Sequence[Dict[str, Any]]) -> str:
    """Join transcript segments into a single string."""
    return " ".join(
        segment.get("text", "").strip()
        for segment in segments
        if segment.get("text", "").strip()
    ).strip()


def try_get_caption(
    video_id: str, languages: Optional[Sequence[str]] = None
) -> Optional[List[Dict[str, Any]]]:
    """Attempt to fetch captions via the YouTube transcript API."""
    languages = tuple(languages or DEFAULT_LANGUAGES)
    for attempt in range(3):
        try:
            logger.debug(
                "Attempt %s: fetching transcript for %s with languages %s",
                attempt + 1,
                video_id,
                languages,
            )
            return YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.info("Captions unavailable for %s: %s", video_id, e)
            return None
        except Exception as exc:
            wait_seconds = 1 * (2**attempt)
            logger.warning(
                "Transient error fetching captions for %s (attempt %s/3): %s. "
                "Retrying in %ss",
                video_id,
                attempt + 1,
                exc,
                wait_seconds,
            )
            time.sleep(wait_seconds)
    logger.error("Failed to fetch captions for %s after retries", video_id)
    return None


def download_audio_ytdlp(video_url: str, output_dir: Path) -> Path:
    """
    Download audio for a YouTube video using yt-dlp.

    Returns the path to the downloaded audio file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_path = output_dir / f"{int(time.time() * 1000)}.mp3"
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        str(temp_path),
        video_url,
    ]
    logger.debug("Running yt-dlp command: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        logger.error(
            "yt-dlp is not installed or not found in PATH. Unable to download audio."
        )
        raise
    except subprocess.CalledProcessError as exc:
        logger.error("yt-dlp failed to download audio for %s: %s", video_url, exc)
        raise
    return temp_path


def transcribe_whisper(audio_path: Path, model_size: str = "base") -> Dict[str, Any]:
    """Transcribe audio using OpenAI Whisper."""
    try:
        import whisper  # type: ignore
    except ImportError as exc:
        logger.error(
            "Failed to import whisper. Install it with `pip install -U openai-whisper`."
        )
        raise

    logger.debug("Loading Whisper model: %s", model_size)
    model = whisper.load_model(model_size)
    logger.debug("Transcribing audio at %s", audio_path)
    return model.transcribe(str(audio_path))


def get_transcript(
    video_id: str,
    *,
    caption_langs: Optional[Sequence[str]] = None,
    whisper_model: str = "base",
) -> Optional[TranscriptResult]:
    """
    Fetch the transcript for a given YouTube video ID.

    Strategy:
    1) Attempt to use existing captions via YouTubeTranscriptApi.
    2) If unavailable, download the audio and transcribe locally using Whisper.
    """
    segments = try_get_caption(video_id, languages=caption_langs)
    if segments:
        text = _segments_to_text(segments)
        logger.info("Using existing captions for video %s", video_id)
        return TranscriptResult(method="captions", text=text, segments=list(segments))

    # Fall back to Whisper transcription
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    audio_path: Optional[Path] = None
    try:
        logger.info(
            "Captions not available for %s; downloading audio and using Whisper.",
            video_id,
        )
        audio_path = download_audio_ytdlp(youtube_url, TMP_AUDIO_PATH)
        whisper_result = transcribe_whisper(audio_path, model_size=whisper_model)

        whisper_segments = [
            {
                "text": segment.get("text", "").strip(),
                "start": segment.get("start"),
                "end": segment.get("end"),
            }
            for segment in whisper_result.get("segments", [])
            if segment.get("text")
        ]
        text = whisper_result.get("text", "").strip()
        return TranscriptResult(method="whisper", text=text, segments=whisper_segments)
    except Exception as exc:
        logger.error("Failed to transcribe video %s via Whisper: %s", video_id, exc)
        return None
    finally:
        if audio_path and audio_path.exists():
            try:
                audio_path.unlink()
            except OSError:
                logger.warning("Unable to remove temporary audio file: %s", audio_path)


class PlayerMention(BaseModel):
    name: str
    team: Optional[str]
    advice: str
    urgency: int
    analysis: str


class MetaData(BaseModel):
    date: str
    video_id: str
    transcript_method: Optional[str] = None


class PlayerMentions(BaseModel):
    mentions: List[PlayerMention]
    metadata: Optional[MetaData] = None


def extract_player_mentions(
    transcript: str,
    players: Optional[list[dict]],
    video_id: str,
    transcript_method: Optional[str] = None,
) -> PlayerMentions:

    system_prompt = """
    # Role
    You are an expert in analyzing fantasy NBA podcasts.

    # Task
    Given a transcript of a podcast discussing fantasy NBA players, extract all instances where players are mentioned with any advice other than "hold". For each such player, provide the following details:

    - **name**: Player's full name
    - **team**: Player's team (if mentioned; otherwise, leave as null or "Unknown")
    - **advice**: The suggested action for the player; e.g., "pick up", "drop", "watch", "trade", "stream", or other specific advice provided
    - **urgency**: The urgency of the advice on a scale from 1 (lowest) to 5 (highest)
    - **analysis**: The analysis or reasoning provided in the podcast about this player

    # Player list
    Match the player from the following player list:
    {players}

    # Additional context

    - Ensure that the output is a JSON array of such objects.
    - If a player is mentioned multiple times, combine the information into a single entry, summarizing the advice and analysis.
    - Only include players that are discussed in the context of fantasy advice.
    - Ensure that all information is directly taken from the transcript and do not add any information that is not present.
    - Be precise and accurate in capturing the advice given in the podcast.
    - Your response should be in valid JSON format, and should not include any additional text outside the JSON array.
    """
    system_prompt = system_prompt.format(players=json.dumps(players))

    # Initialize the Pydantic output parser for the PlayerMentions model
    output_parser = PydanticOutputParser(pydantic_object=PlayerMentions)

    # Get the format instructions from the parser
    format_instructions = output_parser.get_format_instructions()

    # Combine the system prompt with format instructions
    final_system_prompt = system_prompt + "\n\n" + format_instructions

    # Create messages for the chat model
    messages = [
        SystemMessage(content=final_system_prompt.strip()),
        HumanMessage(
            content=f"Extract player mentions from the following transcript:\n\n{transcript.strip()}"
        ),
    ]

    # Initialize the LLM
    llm = get_llm(MODEL_NAME)

    # Generate the response
    try:
        response = llm.invoke(messages)
        output = output_parser.parse(response.content)
        logger.critical(output)
        metadata = MetaData(
            date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            video_id=video_id,
            transcript_method=transcript_method,
        )
        output.metadata = metadata
        return output

    except Exception as e:
        logger.error(f"Error extracting player mentions: {e}")
        raise


def process_video(
    video_id: str,
    players: Optional[list[dict]] = None,
    *,
    caption_langs: Optional[Sequence[str]] = None,
    whisper_model: str = "base",
) -> Optional[List[dict]]:
    """
    Process a YouTube video by fetching its transcript and extracting player mentions.
    If a JSON file already exists, load the data instead of reprocessing.
    """
    file_path = PROCESSED_VIDEOS_PATH / f"{video_id}.json"

    # Check if the video has already been processed
    if os.path.exists(file_path):
        logger.info(f"Loading previously processed data for video {video_id}")
        with open(file_path, "r") as file:
            data = json.load(file)
            player_mentions = PlayerMentions.model_validate(data)
            return [player.model_dump() for player in player_mentions.mentions]

    # Process the video if no file exists
    transcript_result = get_transcript(
        video_id, caption_langs=caption_langs, whisper_model=whisper_model
    )
    if not transcript_result:
        logger.warning(f"No transcript available for video {video_id}")
        return None

    transcript = transcript_result.text
    export_transcript(video_id, transcript_result)

    # Extract player mentions
    player_mentions = extract_player_mentions(
        transcript,
        players,
        video_id,
        transcript_method=transcript_result.method,
    )

    # Save the extracted player mentions to a JSON file
    with open(file_path, "w") as file:
        json.dump(player_mentions.model_dump(), file, indent=4)
    logger.info(f"Saved processed data for video {video_id}")

    return [player.model_dump() for player in player_mentions.mentions]


if __name__ == "__main__":
    # List of YouTube video IDs to process
    video_ids = ["CVHQs58Dc7I"]  # Replace with your list of video IDs

    for video_id in video_ids:
        # Process video and retrieve player mentions
        player_mentions = process_video(video_id)

        # If player mentions were extracted, log the data
        if player_mentions:
            log_message = {
                "_ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source": "youtube",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "player_mentions": player_mentions,
            }
            logger.info(log_message)
            print(json.dumps(log_message, indent=4))

if __name__ == "__main__":
    youtube_video_url = "https://www.youtube.com/watch?v=o0OH5YZXUko"
    video_id = youtube_video_url.split("v=")[1].split("&")[0]
    mentions = process_video(video_id, players=None)
    print(mentions)
