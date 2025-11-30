import asyncio
from utils.llm import call_openrouter

async def handle_crazy_text(message):
    """Handle the !c <text> command for crazy copypasta generation"""
    input_text = message.content[3:].strip()
    if not input_text:
        return

    async with message.channel.typing():
        prompt = f"""Create a funny, non-sensical variation of the 'Crazy? I was crazy once...' copypasta using the input: "{input_text}".

        The original goes:
        "Crazy?\n I was crazy once.\n They locked me in a room.\n A rubber room.\n A rubber room with rats.\n And rats make me crazy."

        Your version should:
        1. Be based on "{input_text}"
        2. Follow the repetitive, escalating rhythm of the original
        3. Be short (max 5-6 lines)
        4. Be funny and slightly unhinged
        5. NOT just replace the word "crazy" - vary the structure creatively
        6. Include line breaks as the example for dramatic effect

        Return ONLY the text of the copypasta."""

        response_content = call_openrouter([{"role": "user", "content": prompt}], max_tokens=150)

    if response_content:
        lines = response_content.split("\n")
        for line in lines:
            if line.strip():
                await message.channel.send(line)
                await asyncio.sleep(0.7)
    else:
        await message.channel.send("Error generating crazy text.")

