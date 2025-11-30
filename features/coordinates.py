import re
import math
import discord
from utils.llm import call_openrouter

def extract_simple_coordinates(message_content):
    """Extract coordinates from simple patterns like '!ncc 100 200' or '!occ 25 50'"""
    content = re.sub(r"!(?:ncc|occ)", "", message_content, flags=re.IGNORECASE).strip()
    
    patterns = [
        r"^(-?\d+)\s+(-?\d+)$",
        r"^(-?\d+),\s*(-?\d+)$",
        r"^x:?\s*(-?\d+)\s+z:?\s*(-?\d+)$",
        r"^(-?\d+)\s+(-?\d+)\s*$",
    ]

    for pattern in patterns:
        match = re.match(pattern, content, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1)), int(match.group(2))
            except ValueError:
                continue
    return None

def get_conversion_direction(message_content):
    content_lower = message_content.lower()
    if "!ncc" in content_lower:
        return "nether"
    elif "!occ" in content_lower:
        return "overworld"
    return None

def convert_coordinates_programmatically(x, z, direction):
    if direction == "nether":
        # Overworld to Nether: divide by 8, round down
        return math.floor(x / 8), math.floor(z / 8)
    elif direction == "overworld":
        # Nether to Overworld: multiply by 8
        return x * 8, z * 8
    return None

def is_simple_coordinate_request(message_content):
    content = re.sub(r"!(?:ncc|occ)", "", message_content, flags=re.IGNORECASE).strip()
    simple_patterns = [
        r"^(-?\d+)\s+(-?\d+)$",
        r"^(-?\d+),\s*(-?\d+)$",
        r"^x:?\s*(-?\d+)\s+z:?\s*(-?\d+)$",
    ]
    for pattern in simple_patterns:
        if re.match(pattern, content, re.IGNORECASE):
            return True
    return False

async def extract_coordinates_with_llm(message_content, direction):
    prompt = f"""Extract the X and Z coordinates from this Minecraft message and determine the conversion direction.

    Message: "{message_content}"

    Analyze the context to determine if this is:
    - "nether" conversion (Overworld → Nether)
    - "overworld" conversion (Nether → Overworld)

    Return ONLY two lines:
    Line 1: Two integers separated by a space (e.g., "100 200")
    Line 2: The direction ("nether" or "overworld")

    If you cannot find coordinates, respond with "Error" on line 1."""

    content = call_openrouter([{"role": "user", "content": prompt}], max_tokens=50)
    
    if not content or "error" in content.lower():
        return None, direction

    lines = content.split("\n")
    if len(lines) < 2:
        return None, direction

    numbers = re.findall(r"-?\d+", lines[0])
    if len(numbers) < 2:
        return None, direction

    coordinates = (int(numbers[0]), int(numbers[1]))
    
    extracted_direction = lines[1].strip().lower()
    if "nether" in extracted_direction:
        extracted_direction = "nether"
    elif "overworld" in extracted_direction:
        extracted_direction = "overworld"
    else:
        extracted_direction = direction

    return coordinates, extracted_direction

async def handle_coordinate_conversion(message):
    print(f"Processing message from {message.author.name}: {message.content}")

    direction = get_conversion_direction(message.content)
    if not direction:
        return

    if is_simple_coordinate_request(message.content):
        coordinates = extract_simple_coordinates(message.content)
    else:
        print("📤 Using LLM to extract coordinates from complex message")
        async with message.channel.typing():
            coordinates, direction = await extract_coordinates_with_llm(message.content, direction)

    if not coordinates:
        print("❌ Could not extract coordinates")
        return

    x, z = coordinates
    result = convert_coordinates_programmatically(x, z, direction)

    if result:
        new_x, new_z = result
        try:
            await message.reply(f"{new_x} {new_z}", mention_author=True)
            print(f"✅ Programmatic conversion: {x} {z} -> {new_x} {new_z}")
        except discord.errors.HTTPException as e:
            print(f"❌ Failed to send Discord message: {e}")

