import re
import math

ITEMS_PER_STACK = 64
STACKS_PER_SB = 27
ITEMS_PER_SB = ITEMS_PER_STACK * STACKS_PER_SB  # 1728

def parse_snc_input(input_str):
    """
    Parse input for !snc (Stacks to Items).
    Supports: "16", "16stacks", "16sb", "36sb 12", "12 36sb"
    Returns total items or None if invalid.
    """
    # Normalize
    input_str = input_str.lower().replace(",", "")
    parts = input_str.split()
    
    total_items = 0
    found_any = False

    for part in parts:
        # Check for SB pattern first
        sb_match = re.match(r"^(\d+)sb$", part)
        if sb_match:
            count = int(sb_match.group(1))
            total_items += count * ITEMS_PER_SB
            found_any = True
            continue

        # Check for Stacks pattern (explicit or implicit)
        # "64stacks" or just "64" (if it's a number)
        stack_match = re.match(r"^(\d+)(?:stacks)?$", part)
        if stack_match:
            count = int(stack_match.group(1))
            total_items += count * ITEMS_PER_STACK
            found_any = True
            continue
        
        # If part is not understood and not whitespace, return None (invalid format)
        if part.strip():
            return None

    return total_items if found_any else None

def format_number(n):
    return f"{n:,}"

async def handle_snc_command(message):
    """Handle !snc (Stacks to Items)"""
    content = message.content[4:].strip() # remove !snc
    if not content:
        await message.reply("Usage: `!snc <amount>[stacks|sb] [additional_stacks]`")
        return

    total_items = parse_snc_input(content)
    
    if total_items is None:
        await message.reply("Invalid format. Examples: `!snc 16`, `!snc 16sb`, `!snc 36sb 12`")
        return

    # Reconstruct readable input description for the output
    # This is a bit tricky since we just summed it up, so let's just show the total.
    # The user requirements showed: "36 shulker boxes + 16 stacks = ... = items"
    # To match that exactly, we might need to parse again or keep track.
    # Simple approach: just show the result clearly.
    
    # "16 stacks = 16 × 64 = 1,024 items"
    # "16 shulker boxes = 16 × 1,728 = 27,648 items"
    # "36 shulker boxes + 16 stacks = ..."
    
    # Let's try to detect what was passed to give a nice output string.
    sb_count = 0
    stack_count = 0
    
    parts = content.lower().replace(",", "").split()
    for part in parts:
        sb_match = re.match(r"^(\d+)sb$", part)
        if sb_match:
            sb_count += int(sb_match.group(1))
            continue
        stack_match = re.match(r"^(\d+)(?:stacks)?$", part)
        if stack_match:
            stack_count += int(stack_match.group(1))
            continue

    components = []
    calcs = []
    
    if sb_count > 0:
        components.append(f"{sb_count} __**shulker boxes**__")
        calcs.append(f"({sb_count} × {format_number(ITEMS_PER_SB)})")
    if stack_count > 0:
        components.append(f"{stack_count} __**stacks**__")
        calcs.append(f"({stack_count} × {ITEMS_PER_STACK})")
        
    input_desc = " + ".join(components)
    calc_desc = " + ".join(calcs)
    
    if len(components) == 1:
        # Simplier format for single type
        if sb_count > 0:
            response = f"{input_desc} = {sb_count} × {format_number(ITEMS_PER_SB)} = {format_number(total_items)} __**items**__"
        else:
            response = f"{input_desc} = {stack_count} × {ITEMS_PER_STACK} = {format_number(total_items)} __**items**__"
    else:
        response = f"{input_desc} = {calc_desc} = {format_number(total_items)} __**items**__"

    await message.reply(response)

async def handle_nsc_command(message):
    """Handle !nsc (Items to Stacks)"""
    content = message.content[4:].strip().replace(",", "")
    try:
        total_items = int(content)
    except ValueError:
        await message.reply("Usage: `!nsc <total_items>`")
        return

    if total_items < 0:
        await message.reply("Please provide a positive number.")
        return

    # Calculate Breakdown 1: Stacks + Items
    stacks_only = total_items // ITEMS_PER_STACK
    rem_items_only = total_items % ITEMS_PER_STACK
    
    breakdown1 = f"{stacks_only} __**stacks**__"
    if rem_items_only > 0:
        breakdown1 += f" + {rem_items_only} __**items**__"
    else:
        breakdown1 += " + 0 __**items**__" # Per example

    # Calculate Breakdown 2: SB + Stacks + Items
    sb = total_items // ITEMS_PER_SB
    rem_after_sb = total_items % ITEMS_PER_SB
    stacks = rem_after_sb // ITEMS_PER_STACK
    rem_items = rem_after_sb % ITEMS_PER_STACK

    parts = []
    if sb > 0:
        parts.append(f"{sb} __**shulker boxes**__") # usually plural even if 1 based on example? "1 shulker box" in example.
        # Example says "1 shulker box"
        if sb == 1:
             parts[-1] = "1 __**shulker box**__"
    
    if stacks > 0:
        parts.append(f"{stacks} __**stacks**__")
    elif sb > 0 and rem_items > 0: 
        # If we have SBs and items, but 0 stacks in between, do we show 0 stacks?
        # Example: 2854 -> 1 sb + 17 stacks + 38 items.
        # Example: 27648 -> 16 shulker boxes (no stacks listed).
        pass

    if rem_items > 0:
        parts.append(f"{rem_items} __**items**__")
    elif len(parts) == 0:
        parts.append("0 __**items**__")
        
    breakdown2 = " + ".join(parts)
    
    # Format: "2,854 items = 44 stacks + 38 items = 1 shulker box + 17 stacks + 38 items"
    # If breakdowns are identical (e.g. < 1 SB), maybe simplify?
    # Example 1024: "1,024 items = 16 stacks + 0 items" (No second part needed if 0 SB)
    
    response = f"{format_number(total_items)} __**items**__ = {breakdown1}"
    if sb > 0:
        response += f" = {breakdown2}"

    await message.reply(response)

