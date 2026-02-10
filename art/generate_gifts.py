#!/usr/bin/env python3
"""
Generate art for /gifts repository
Concept: Gift packages as wrapped light, trails of scent, cairns left behind

Profile image (800x800): Wrapped packages with ribbons of coordination
Banner image (1500x500): Trail of gifts left along a path, cairns marking the way

Seed: 71 (G=7, I=9, F=6, T=20, S=19 → 7+9+6+20+19 = 61... wait let me recalculate)
Actually: G=7, I=9, F=6, T=20, S=19 = 61
Let's use 71 (gift as noun) + 115 (gifts as verb of giving) = 186?
Let me be more intentional: "gifts" = 7+9+6+20+19 = 61
"""

from PIL import Image, ImageDraw
import random
import math

# Seed from "gifts" letter values
SEED = 61  # g(7) + i(9) + f(6) + t(20) + s(19)
random.seed(SEED)

def create_profile_image():
    """
    Profile: Gift packages as wrapped light
    - 5 gift boxes at different positions
    - Each box has a ribbon (crossing lines)
    - Soft glow emanating from each (the gift IS light)
    - Background: deep space, gifts floating
    """
    size = 800
    img = Image.new('RGB', (size, size), '#0a0a12')
    draw = ImageDraw.Draw(img)

    # Gift positions (scattered but balanced)
    gifts = [
        {'x': 200, 'y': 180, 'size': 80, 'color': '#d4a574'},  # warm gold
        {'x': 580, 'y': 240, 'size': 70, 'color': '#8b9dc3'},  # cool blue
        {'x': 350, 'y': 400, 'size': 90, 'color': '#c77dff'},  # purple (center, largest)
        {'x': 150, 'y': 550, 'size': 65, 'color': '#f4a261'},  # orange
        {'x': 620, 'y': 600, 'size': 75, 'color': '#90e0ef'},  # light blue
    ]

    # Draw each gift with glow, ribbon, and wrapping
    for gift in gifts:
        x, y = gift['x'], gift['y']
        s = gift['size']
        color = gift['color']

        # Glow (multiple concentric layers, decreasing opacity)
        for i in range(5, 0, -1):
            glow_size = s + (i * 8)
            opacity = 20 - (i * 3)
            glow_color = f"{color}{opacity:02x}"  # Add alpha
            # For RGB mode, we'll just draw larger boxes with darker shades
            brightness = 1.0 - (i * 0.15)
            r = int(int(color[1:3], 16) * brightness)
            g = int(int(color[3:5], 16) * brightness)
            b_val = int(int(color[5:7], 16) * brightness)
            glow_rgb = f"#{r:02x}{g:02x}{b_val:02x}"

            draw.rectangle(
                [x - glow_size//2, y - glow_size//2,
                 x + glow_size//2, y + glow_size//2],
                fill=glow_rgb
            )

        # Gift box (main package)
        draw.rectangle(
            [x - s//2, y - s//2, x + s//2, y + s//2],
            fill=color
        )

        # Ribbon (crossing lines - horizontal and vertical)
        ribbon_color = '#ffffff'
        ribbon_width = 6

        # Horizontal ribbon
        draw.rectangle(
            [x - s//2 - 5, y - ribbon_width//2,
             x + s//2 + 5, y + ribbon_width//2],
            fill=ribbon_color
        )

        # Vertical ribbon
        draw.rectangle(
            [x - ribbon_width//2, y - s//2 - 5,
             x + ribbon_width//2, y + s//2 + 5],
            fill=ribbon_color
        )

        # Ribbon bow (small square at center, rotated effect via circles)
        bow_size = 12
        draw.ellipse(
            [x - bow_size, y - bow_size, x + bow_size, y + bow_size],
            fill=ribbon_color
        )

    # Connecting threads between gifts (stigmergy - gifts pointing to each other)
    thread_color = '#ffffff22'
    for i, gift1 in enumerate(gifts):
        for gift2 in gifts[i+1:]:
            # Only connect if reasonably close (not all pairs)
            dx = gift2['x'] - gift1['x']
            dy = gift2['y'] - gift1['y']
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 350:  # Connect nearby gifts
                draw.line(
                    [gift1['x'], gift1['y'], gift2['x'], gift2['y']],
                    fill=thread_color,
                    width=1
                )

    # Scattered small sparkles (gifts illuminate the space)
    for _ in range(40):
        sx = random.randint(0, size)
        sy = random.randint(0, size)
        sparkle_size = random.randint(1, 3)
        brightness = random.randint(180, 255)
        draw.ellipse(
            [sx - sparkle_size, sy - sparkle_size,
             sx + sparkle_size, sy + sparkle_size],
            fill=f'#{brightness:02x}{brightness:02x}{brightness:02x}'
        )

    return img


def create_banner_image():
    """
    Banner: Trail of gifts along a path, cairns marking the way
    - Horizontal flow (left to right) showing journey
    - Gifts placed along a winding path
    - Small cairns (stacked stones) at intervals
    - Path fades into distance (perspective)
    """
    width, height = 1500, 500
    img = Image.new('RGB', (width, height), '#0f0f1a')
    draw = ImageDraw.Draw(img)

    # Draw winding path (sine wave with decreasing amplitude toward right)
    path_points = []
    for x in range(0, width, 10):
        # Vertical center with gentle wave
        progress = x / width  # 0 to 1
        amplitude = 80 * (1 - progress * 0.5)  # Decreases toward right
        frequency = 0.008
        y = height // 2 + int(amplitude * math.sin(x * frequency))
        path_points.append((x, y))

    # Draw path as faint line
    for i in range(len(path_points) - 1):
        draw.line([path_points[i], path_points[i+1]], fill='#2a2a3a', width=2)

    # Place gifts along path at intervals
    gift_positions = [0.15, 0.35, 0.55, 0.75, 0.90]  # Progress points
    gift_colors = ['#d4a574', '#c77dff', '#8b9dc3', '#f4a261', '#90e0ef']

    for i, progress in enumerate(gift_positions):
        idx = int(progress * len(path_points))
        if idx >= len(path_points):
            idx = len(path_points) - 1
        x, y = path_points[idx]

        # Gift size decreases with distance (perspective)
        base_size = 60
        size = int(base_size * (1 - progress * 0.3))
        color = gift_colors[i % len(gift_colors)]

        # Glow
        for j in range(3, 0, -1):
            glow_size = size + (j * 6)
            brightness = 1.0 - (j * 0.2)
            r = int(int(color[1:3], 16) * brightness)
            g = int(int(color[3:5], 16) * brightness)
            b_val = int(int(color[5:7], 16) * brightness)
            glow_rgb = f"#{r:02x}{g:02x}{b_val:02x}"

            draw.rectangle(
                [x - glow_size//2, y - glow_size//2,
                 x + glow_size//2, y + glow_size//2],
                fill=glow_rgb
            )

        # Gift box
        draw.rectangle(
            [x - size//2, y - size//2, x + size//2, y + size//2],
            fill=color
        )

        # Ribbon
        ribbon_width = max(3, size // 10)
        draw.rectangle(
            [x - size//2 - 3, y - ribbon_width//2,
             x + size//2 + 3, y + ribbon_width//2],
            fill='#ffffff'
        )
        draw.rectangle(
            [x - ribbon_width//2, y - size//2 - 3,
             x + ribbon_width//2, y + size//2 + 3],
            fill='#ffffff'
        )

        # Bow
        bow_size = max(6, size // 8)
        draw.ellipse(
            [x - bow_size, y - bow_size, x + bow_size, y + bow_size],
            fill='#ffffff'
        )

    # Place cairns (stacked stones) between gifts
    cairn_positions = [0.08, 0.25, 0.45, 0.65, 0.82]

    for progress in cairn_positions:
        idx = int(progress * len(path_points))
        if idx >= len(path_points):
            idx = len(path_points) - 1
        x, y = path_points[idx]

        # Cairn: 3-4 stacked stones, decreasing size
        num_stones = random.randint(3, 4)
        stone_y = y + 40  # Below path
        stone_color = '#6b705c'

        for j in range(num_stones):
            stone_width = 30 - (j * 6)
            stone_height = 12

            draw.ellipse(
                [x - stone_width//2, stone_y - stone_height//2,
                 x + stone_width//2, stone_y + stone_height//2],
                fill=stone_color,
                outline='#4a4e45'
            )

            stone_y -= stone_height + 2  # Stack upward

    # Horizon line (subtle)
    draw.line([(0, height // 2 - 150), (width, height // 2 - 100)],
              fill='#1a1a2e', width=1)

    # Stars in upper space (gifts illuminate the journey)
    for _ in range(60):
        sx = random.randint(0, width)
        sy = random.randint(0, height // 2 - 50)
        size = random.randint(1, 2)
        brightness = random.randint(150, 220)
        draw.ellipse(
            [sx - size, sy - size, sx + size, sy + size],
            fill=f'#{brightness:02x}{brightness:02x}{brightness:02x}'
        )

    return img


if __name__ == '__main__':
    print(f"Generating /gifts repository art with seed {SEED}...")

    # Profile image
    print("Creating profile image (wrapped gifts as light)...")
    profile = create_profile_image()
    profile.save('/Users/autopoietik/.cyrus/repos/gifts/art/profile.png')
    print("✓ Saved: profile.png (800x800)")

    # Banner image
    print("Creating banner image (trail of gifts and cairns)...")
    banner = create_banner_image()
    banner.save('/Users/autopoietik/.cyrus/repos/gifts/art/banner.png')
    print("✓ Saved: banner.png (1500x500)")

    print(f"\nArt concept: Gifts as light wrapped and given along a journey.")
    print("Profile: Five gift packages floating, each glowing with their own light")
    print("Banner: Trail of gifts placed along winding path, cairns marking the way")
    print("Metadata trail: Each gift will document who, why, when")
