import os
import json
import datetime
import logging
from typing import List, Dict, Any, Optional
import openai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import polars as pl
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)
load_dotenv(override=True)

# Set your OpenAI API key
# openai.api_key = 'YOUR_OPENAI_API_KEY'

# Model and file paths
MODEL_NAME = "gpt-4o"
PROCESSED_VIDEOS_PATH = "data/processed_videos"
os.makedirs(PROCESSED_VIDEOS_PATH, exist_ok=True)  # Create directory if not exists


def get_llm(model_name: str) -> ChatOpenAI:
    """Initialize and return a LangChain ChatOpenAI model."""
    return ChatOpenAI(model_name=model_name, temperature=0.0)


def get_transcript(video_id: str) -> List[Dict[str, Any]]:
    """
    Fetches the transcript for a given YouTube video ID.
    """
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        logger.error(f"Error retrieving transcript for video {video_id}: {e}")
        return None


class PlayerMention(BaseModel):
    name: str
    team: Optional[str]
    advice: str
    urgency: int
    analysis: str


class MetaData(BaseModel):
    date: str
    video_id: str


class PlayerMentions(BaseModel):
    mentions: List[PlayerMention]
    metadata: Optional[MetaData] = None


def extract_player_mentions(
    transcript: str, players: Optional[list[dict]], video_id: str
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
        )
        output.metadata = metadata
        return output

    except Exception as e:
        logger.error(f"Error extracting player mentions: {e}")
        raise


def process_video(video_id: str, players: Optional[list[dict]]) -> list[dict]:
    """
    Process a YouTube video by fetching its transcript and extracting player mentions.
    If a JSON file already exists, load the data instead of reprocessing.
    """
    file_path = os.path.join(PROCESSED_VIDEOS_PATH, f"{video_id}.json")

    # Check if the video has already been processed
    if os.path.exists(file_path):
        logger.info(f"Loading previously processed data for video {video_id}")
        with open(file_path, "r") as file:
            data = json.load(file)
            player_mentions = PlayerMentions.model_validate(data)
            return [player.model_dump() for player in player_mentions.mentions]

    # Process the video if no file exists
    transcript_data = get_transcript(video_id)
    if not transcript_data:
        logger.warning(f"No transcript available for video {video_id}")
        return None

    # Convert the transcript segments to a single text
    df = pl.DataFrame(transcript_data).sort("start")
    transcript = " ".join(df["text"].to_list())

    # Extract player mentions
    player_mentions = extract_player_mentions(transcript, players, video_id)

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
                "player_mentions": [pm.model_dump() for pm in player_mentions.mentions],
            }
            logger.info(log_message)
            print(json.dumps(log_message, indent=4))
