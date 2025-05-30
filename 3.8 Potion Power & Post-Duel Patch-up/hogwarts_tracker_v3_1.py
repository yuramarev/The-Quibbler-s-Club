import tkinter as tk
from tkinter import ttk, messagebox, font, simpledialog, filedialog
import json
import winsound # Note: winsound is Windows-specific.
import os
import random
from datetime import datetime
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont # Pillow library for image manipulation
import webbrowser
import platform
import math
import threading
import time # For duel pacing

# Attempt to import pygame for audio, but make it optional
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Note: Pygame library not found. Theme song and dueling sound effects will be disabled. Install with 'pip install pygame'")


# ==== MAGICAL CONFIGURATION ====
VERSION = "3.8 Potion Power & Post-Duel Patch-up" # Updated Version
HOUSES = {
    "Gryffindor": {"points": 0, "color": "#AE0001", "secondary": "#FFDB00", "animal": "🦁", "traits": "Bravery, Courage, Chivalry"},
    "Ravenclaw": {"points": 0, "color": "#2B4C7E", "secondary": "#946B2D", "animal": "🦅", "traits": "Intelligence, Wisdom, Creativity"},
    "Hufflepuff": {"points": 0, "color": "#FFDB00", "secondary": "#000000", "animal": "🦡", "traits": "Loyalty, Patience, Fairness"},
    "Slytherin": {"points": 0, "color": "#2A623D", "secondary": "#AAAAAA", "animal": "🐍", "traits": "Ambition, Cunning, Resourcefulness"}
}

DEFAULT_STUDENTS = ["Harry Potter", "Hermione Granger", "Ron Weasley", "Luna Lovegood"]
DEFAULT_HP = 150 # Increased for longer duels
DEFAULT_MP = 75  # Slightly increased MP pool

ACHIEVEMENTS = {
    "Dumbledore's Wisdom": {"points": 50, "icon": "🎓", "color": "#F4D03F", "description": "For exceptional wisdom and leadership"},
    "Marauder's Prank": {"points": 40, "icon": "🌙", "color": "#8E44AD", "description": "For outstanding mischief and creativity"},
    "Patronus Charm": {"points": 30, "icon": "🦌", "color": "#3498DB", "description": "For mastering advanced defensive magic"},
    "Time-Turner": {"points": 60, "icon": "⏳", "color": "#1ABC9C", "description": "For exceptional time management skills"},
    "Golden Snitch": {"points": 100, "icon": "⚡", "color": "#F1C40F", "description": "For catching the Golden Snitch in Quidditch"},
    "Potions Master": {"points": 35, "icon": "🧪", "color": "#E74C3C", "description": "For excellence in potion-making"},
    "Quidditch Champion": {"points": 45, "icon": "🏆", "color": "#2ECC71", "description": "For outstanding performance in Quidditch"},
    "Animagus": {"points": 70, "icon": "🐾", "color": "#9B59B6", "description": "For mastering the Animagus transformation"},
    "Parseltongue": {"points": 55, "icon": "🐍", "color": "#27AE60", "description": "For rare ability to speak to snakes"},
    "Phoenix Feather": {"points": 80, "icon": "🔥", "color": "#E67E22", "description": "For demonstrating exceptional loyalty and rebirth"}
}

SOUNDS = {
    "points": [440, 523, 659], "achievement": [784, 659, 523, 659, 784], "error": [220, 110],
    "sorting": [349, 392, 440, 523, 440, 392, 349], "celebration": [659, 698, 784, 880, 784, 698, 659],
    "spell_cast_ui": [523, 587, 659, 698, 784], "duel_start": [200, 300, 400, 500],
    "duel_hit": [600, 400], "duel_miss": [300, 200], "duel_crit_hit": [800, 900, 700], "duel_crit_miss": [200,150,100],
    "duel_block": [400, 400], "shield_break": [300,250,200], "priori_incantatem": [300, 500, 700, 900, 700, 500, 300],
    "heal_sound": [587, 698, 784], "status_inflict": [400, 350, 300], "status_cure": [500, 600, 700],
    "unforgivable_cast": [200, 150, 100, 300], "generic_spell_clash": [450, 550, 350],
    "elemental_clash_steam": [300, 600, 350, 650], "elemental_clash_ice": [600, 700, 800], "elemental_clash_fire": [700, 500, 600],
    "dark_magic_clash": [250, 350, 150], "potion_use": [400, 500, 600]
}

SAVE_FILE = "hogwarts_save.json"
AVATAR_DIR = "student_avatars"
ASSETS_DIR = "assets"
THEME_SONG_FILE = "theme_song.ogg"

# Expanded Spell List for Dueling
SPELLS = [
    "Expelliarmus", "Stupefy", "Protego", "Incendio", "Diffindo", "Riddikulus", "Petrificus Totalus",
    "Finite Incantatem", "Lumos", "Nox", "Wingardium Leviosa", "Alohomora", "Accio", "Episkey",
    "Confringo", "Bombarda", "Reducto", "Aguamenti", "Confundo", "Silencio", "Muffliato", "Obliviate",
    "Levicorpus", "Liberacorpus", "Expecto Patronum", "Avada Kedavra", "Crucio", "Imperio",
    "Furnunculus", "Densaugeo", "Tarantallegra", "Locomotor Mortis", "Impedimenta", "Relashio",
    "Serpensortia", "Oppugno", "Sectumsempra",
    "Glacius", "Reparo", "Sonorus", "Protego Maxima", "Bombarda Maxima", "Rictusempra", "Flipendo",
    "Expulso", "Anteoculatia", "Mimblewimble", "Langlock", "Slugulus Eructo", "Ebublio", "Vermiculus",
    "Orchideous", "Avis", "Lacarnum Inflamarae"
]

# Detailed spell properties for dueling
SPELL_DETAILS = {
    "Expelliarmus": {"mp": 5, "base_dmg": 10, "type": "offensive_beam", "accuracy": 9, "crit_chance": 19, "desc": "Disarming Charm. Moderate damage."},
    "Stupefy": {"mp": 8, "base_dmg": 15, "type": "offensive_beam", "accuracy": 10, "crit_chance": 19, "desc": "Stunning Spell. Good damage."},
    "Incendio": {"mp": 10, "base_dmg": 18, "type": "offensive_projectile", "element": "fire", "accuracy": 11, "crit_chance": 18, "desc": "Fire-Making Spell. Fire damage."},
    "Diffindo": {"mp": 7, "base_dmg": 12, "type": "offensive_cut", "accuracy": 10, "crit_chance": 19, "desc": "Severing Charm. Moderate damage."},
    "Reducto": {"mp": 12, "base_dmg": 22, "type": "offensive_blast", "accuracy": 12, "crit_chance": 18, "desc": "Reductor Curse. Significant damage."},
    "Confringo": {"mp": 15, "base_dmg": 28, "type": "offensive_blast", "element": "fire", "accuracy": 13, "crit_chance": 17, "desc": "Blasting Curse. High fire damage."},
    "Bombarda": {"mp": 18, "base_dmg": 35, "type": "offensive_blast", "accuracy": 14, "crit_chance": 17, "desc": "Exploding Charm. Very high damage."},
    "Sectumsempra": {"mp": 30, "base_dmg": 40, "type": "offensive_dark", "accuracy": 12, "crit_chance": 18, "desc": "Dark cutting curse. Severe damage. Ignores some defenses."},
    "Furnunculus": {"mp": 6, "base_dmg": 8, "type": "offensive_curse", "effect": "boils", "duration": 2, "accuracy": 9, "effect_chance": 11, "desc": "Causes boils. Minor damage, accuracy debuff."},
    "Densaugeo": {"mp": 6, "base_dmg": 8, "type": "offensive_curse", "effect": "teeth", "duration": 2, "accuracy": 9, "effect_chance": 11, "desc": "Enlarges teeth. Minor damage, distracting."},
    "Relashio": {"mp": 9, "base_dmg": 12, "type": "offensive_force", "accuracy": 10, "crit_chance": 19, "desc": "Revulsion Jinx. Pushes back, moderate damage."},
    "Petrificus Totalus": {"mp": 10, "base_dmg": 5, "type": "offensive_bind", "effect": "stun", "duration": 1, "accuracy": 11, "effect_chance": 12, "desc": "Full Body-Bind. Minor damage, may stun for 1 round."},
    "Tarantallegra": {"mp": 7, "base_dmg": 3, "type": "offensive_curse", "effect": "dance", "duration": 2, "accuracy": 10, "effect_chance": 11, "desc": "Dancing Feet Jinx. Minimal damage, forces dance."},
    "Locomotor Mortis": {"mp": 8, "base_dmg": 3, "type": "offensive_bind", "effect": "leg_lock", "duration": 2, "accuracy": 10, "effect_chance": 11, "desc": "Leg-Locker Curse. Minimal damage, prevents movement."},
    "Impedimenta": {"mp": 12, "base_dmg": 8, "type": "offensive_slow", "effect": "slow", "duration": 2, "accuracy": 11, "effect_chance": 12, "desc": "Impediment Jinx. Slows opponent, minor damage."},
    "Confundo": {"mp": 10, "type": "offensive_utility", "effect": "confuse", "duration": 1, "accuracy": 12, "effect_chance": 10, "desc": "Confundus Charm. May cause opponent to miss/use weak spell."},
    "Silencio": {"mp": 7, "type": "offensive_utility", "effect": "silence", "duration": 1, "accuracy": 11, "effect_chance": 13, "desc": "Silencing Charm. Prevents spellcasting for 1 round."},
    "Avada Kedavra": {"mp": 50, "base_dmg": 80, "type": "offensive_dark_unforgivable", "accuracy": 18, "crit_chance": 20, "desc": "The Killing Curse. Massive damage. Very hard to land."},
    "Crucio": {"mp": 35, "base_dmg": 20, "type": "offensive_dark_unforgivable", "effect": "pain_dot", "dot_dmg": 8, "duration": 2, "accuracy": 14, "effect_chance": 10, "desc": "Cruciatus Curse. Damage + pain over time."},
    "Imperio": {"mp": 30, "type": "offensive_dark_unforgivable", "effect": "control", "duration": 1, "accuracy": 15, "effect_chance": 9, "desc": "Imperius Curse. Chance to control opponent."},
    "Protego": {"mp": 10, "type": "shield", "strength": 25, "duration": 1, "accuracy": 21, "desc": "Shield Charm. Blocks/reduces damage for 1 turn."},
    "Expecto Patronum": {"mp": 25, "type": "shield_special", "strength": 40, "duration": 1, "accuracy": 21, "desc": "Patronus Charm. Strong defense, esp. vs Dark."},
    "Finite Incantatem": {"mp": 10, "type": "counter_utility", "accuracy": 21, "desc": "General Counter-Spell. May dispel ongoing effects."},
    "Episkey": {"mp": 12, "base_heal": 30, "type": "heal", "accuracy": 21, "desc": "Healing spell. Restores HP."},
    "Levicorpus": {"mp": 8, "base_dmg": 5, "type": "offensive_utility", "effect": "levitate_target", "duration": 1, "accuracy": 10, "effect_chance": 12, "desc": "Dangles opponent by ankle, may cause miss."},
    "Liberacorpus": {"mp": 3, "type": "counter_utility", "accuracy": 21, "desc": "Counter-jinx for Levicorpus."},
    "Aguamenti": {"mp": 5, "base_dmg": 5, "type": "offensive_utility", "element": "water", "accuracy": 9, "desc": "Water-Making Spell. Minor water damage."},
    "Serpensortia": {"mp": 12, "type": "summon_snake", "accuracy": 12, "desc": "Summons a snake to attack next turn."},
    "Oppugno": {"mp": 8, "base_dmg": 15, "type": "summon_attack", "accuracy": 11, "desc": "Directs summoned/conjured items to attack."},
    "Glacius": {"mp": 12, "base_dmg": 10, "type": "offensive_utility", "element": "ice", "effect": "freeze", "duration": 1, "accuracy": 11, "effect_chance": 11, "desc": "Freezing spell. Damage and chance to immobilize."},
    "Reparo": {"mp": 8, "type": "utility_flavor", "accuracy": 21, "desc": "Mending Charm. (No direct combat effect here)."},
    "Sonorus": {"mp": 3, "type": "utility_flavor", "accuracy": 21, "desc": "Amplifies caster's voice."},
    "Protego Maxima": {"mp": 20, "type": "shield_area", "strength": 35, "duration": 1, "accuracy": 21, "desc": "Stronger, wider shield."},
    "Bombarda Maxima": {"mp": 25, "base_dmg": 45, "type": "offensive_blast_area", "accuracy": 15, "crit_chance": 16, "desc": "More powerful exploding charm."},
    "Rictusempra": {"mp": 6, "base_dmg": 5, "type": "offensive_curse", "effect": "tickle", "duration": 1, "accuracy": 9, "effect_chance": 13, "desc": "Tickling Charm. Distracts opponent."},
    "Flipendo": {"mp": 7, "base_dmg": 10, "type": "offensive_force", "accuracy": 10, "desc": "Knockback Jinx. Pushes target, moderate damage."},
    "Expulso": {"mp": 14, "base_dmg": 25, "type": "offensive_blast", "accuracy": 13, "desc": "Expulsion Curse. Stronger than Reducto."},
    "Anteoculatia": {"mp": 5, "type": "offensive_curse", "effect": "antlers", "duration": 2, "accuracy": 10, "effect_chance": 10, "desc": "Causes antlers to sprout. Humiliating debuff (e.g. accuracy down)."},
    "Mimblewimble": {"mp": 9, "type": "offensive_utility", "effect": "tongue_tie", "duration": 1, "accuracy": 12, "effect_chance": 11, "desc": "Tongue-Tying Curse. Chance to prevent spell next turn."},
    "Langlock": {"mp": 8, "type": "offensive_utility", "effect": "tongue_lock", "duration": 1, "accuracy": 11, "effect_chance": 12, "desc": "Locks tongue to roof of mouth. Harder to cast."},
    "Slugulus Eructo": {"mp": 10, "base_dmg": 5, "type": "offensive_curse", "effect": "slug_vomit", "duration": 2, "accuracy": 10, "effect_chance": 10, "desc": "Slug-Vomiting Charm. Gross, minor damage over time."},
    "Ebublio": {"mp": 12, "base_dmg": 20, "type": "offensive_projectile", "element": "water", "accuracy": 11, "desc": "Bubble-Producing Charm. Large forceful bubbles."},
    "Vermiculus": {"mp": 7, "type": "offensive_curse", "effect": "worms", "duration": 2, "accuracy": 9, "effect_chance": 11, "desc": "Transfigures target into a worm (briefly, causing miss chance)."},
    "Orchideous": {"mp": 4, "type": "utility_flavor", "accuracy": 21, "desc": "Conjures flowers."},
    "Avis": {"mp": 6, "type": "summon_birds", "accuracy": 21, "desc": "Conjures a flock of birds (can be used with Oppugno)."},
    "Lacarnum Inflamarae": {"mp": 9, "base_dmg": 12, "type": "offensive_projectile", "element": "fire", "accuracy": 10, "desc": "Shoots a ball of fire."},
    "Lumos": {"mp": 1, "type": "utility_flavor", "accuracy": 21, "desc": "Wand-Lighting Charm."},
    "Nox": {"mp": 1, "type": "utility_flavor", "accuracy": 21, "desc": "Wand-Extinguishing Charm."},
    "Wingardium Leviosa": {"mp": 3, "base_dmg": 1, "type": "utility_flavor", "accuracy": 21, "desc": "Levitation Charm."},
    "Alohomora": {"mp": 2, "type": "utility_flavor", "accuracy": 21, "desc": "Unlocking Charm."},
    "Accio": {"mp": 3, "type": "utility_flavor", "accuracy": 21, "desc": "Summoning Charm."},
    "Riddikulus": {"mp": 5, "type": "utility_flavor", "accuracy": 21, "desc": "Boggart-Banishing Spell."},
    "Obliviate": {"mp": 15, "type": "utility_flavor", "accuracy": 21, "desc": "Memory Charm."},
    "Muffliato": {"mp": 4, "type": "utility_flavor", "accuracy": 21, "desc": "Muffling Charm."},
}

POTIONS = {
    "Wiggenweld Potion": {"type": "heal", "amount": 40, "uses_per_duel": 1, "desc": "Restores 40 HP.", "sound": "heal_sound"}
}

SPELL_INTERACTIONS = {
    # Core Interactions
    tuple(sorted(("Avada Kedavra", "Expelliarmus"))): {"log": "The Killing Curse meets the Disarming Charm! Priori Incantatem erupts!", "sound": "priori_incantatem", "resolve": "priori_incantatem"},
    tuple(sorted(("Incendio", "Aguamenti"))): {"log": "Fire and Water collide, creating a blinding steam cloud!", "sound": "elemental_clash_steam", "resolve": "custom:steam_cloud_miss_both"},
    tuple(sorted(("Protego", "Stupefy"))): {"log": "Stupefy ricochets off Protego!", "sound": "duel_block", "resolve": "custom:protego_deflects_projectile"},
    tuple(sorted(("Protego", "Avada Kedavra"))): {"log": "Protego shatters against the Killing Curse, but slightly weakens it!", "sound": "shield_break", "resolve": "custom:protego_vs_ak"},
    tuple(sorted(("Sectumsempra", "Episkey"))): {"log": "Episkey struggles against the dark wounds of Sectumsempra!", "sound": "dark_magic_clash", "resolve": "custom:sectumsempra_hinders_episkey"},
    tuple(sorted(("Finite Incantatem", "Petrificus Totalus"))): {"log": "Finite Incantatem breaks the Full Body-Bind!", "sound": "status_cure", "resolve": "custom:finite_breaks_bind"},
    tuple(sorted(("Finite Incantatem", "Crucio"))): {"log": "Finite Incantatem lessens the Cruciatus Curse's grip!", "sound": "status_cure", "resolve": "custom:finite_lessens_crucio"},
    tuple(sorted(("Levicorpus", "Liberacorpus"))): {"log": "Liberacorpus counters Levicorpus!", "sound": "generic_spell_clash", "resolve": "both_fizzle"},

    # New Interactions
    tuple(sorted(("Expelliarmus", "Protego"))): {"log": "Expelliarmus is blocked by Protego!", "sound": "duel_block", "resolve": "custom:expelliarmus_vs_protego"},
    tuple(sorted(("Incendio", "Incendio"))): {"log": "Twin flames erupt into a larger inferno, scorching the air!", "sound": "elemental_clash_fire", "resolve": "custom:double_incendio"},
    tuple(sorted(("Petrificus Totalus", "Protego"))): {"log": "Petrificus Totalus is deflected harmlessly by the Shield Charm!", "sound": "duel_block", "resolve": "custom:bind_vs_shield"},
    tuple(sorted(("Confundo", "Protego"))): {"log": "Protego wavers but manages to repel the Confundus Charm!", "sound": "duel_block", "resolve": "custom:confound_vs_shield"},
    tuple(sorted(("Aguamenti", "Aguamenti"))): {"log": "A great splash of water, but no real harm done!", "sound": "elemental_clash_steam", "resolve": "both_fizzle"},


    # Elemental Interactions
    tuple(sorted(("Incendio", "Glacius"))): {"log": "Fire melts ice, creating a burst of steam and water!", "sound": "elemental_clash_steam", "resolve": "custom:fire_vs_ice_steam"},
    tuple(sorted(("Aguamenti", "Glacius"))): {"log": "Water freezes solid as Glacius hits!", "sound": "elemental_clash_ice", "resolve": "custom:water_frozen_by_glacius"},
    tuple(sorted(("Lacarnum Inflamarae", "Aguamenti"))): {"log": "A lesser fire meets water, producing some steam.", "sound": "elemental_clash_steam", "resolve": "both_reduced_effect"},
    tuple(sorted(("Ebublio", "Incendio"))): {"log": "Fiery bubbles pop and scatter!", "sound": "elemental_clash_steam", "resolve": "custom:ebublio_fire_pop"},


    # Offensive vs. Offensive
    tuple(sorted(("Stupefy", "Stupefy"))): {"log": "Twin Stunning Spells collide mid-air, creating a shockwave!", "sound": "generic_spell_clash", "resolve": "custom:stunner_stalemate"},
    tuple(sorted(("Expelliarmus", "Expelliarmus"))): {"log": "Disarming Charms meet! Both wands fly from careless hands!", "sound": "generic_spell_clash", "resolve": "custom:double_disarm_attempt"}, # No actual disarm, just flavor
    tuple(sorted(("Confringo", "Bombarda"))): {"log": "Two powerful blasting curses meet with a deafening explosion!", "sound": "duel_crit_hit", "resolve": "custom:double_blast_recoil"},
    tuple(sorted(("Sectumsempra", "Crucio"))): {"log": "A torrent of dark magic! Both casters are strained!", "sound": "dark_magic_clash", "resolve": "custom:dark_magic_overload"},

    # Defensive vs. Defensive
    tuple(sorted(("Protego", "Protego Maxima"))): {"log": "Two shield charms shimmer, the stronger one slightly bolstered.", "sound": "duel_block", "resolve": "custom:shields_combine_minor"},

    # Utility/Curse Interactions
    tuple(sorted(("Silencio", "Sonorus"))): {"log": "Silence and Amplification clash! The sound is erratically muffled then loud!", "sound": "generic_spell_clash", "resolve": "custom:silence_vs_sonorus"},
    tuple(sorted(("Furnunculus", "Densaugeo"))): {"log": "Boils and enlarged teeth! A truly hideous combination afflicts the target of the stronger curse!", "sound": "status_inflict", "resolve": "custom:combined_minor_curses"},
    tuple(sorted(("Tarantallegra", "Locomotor Mortis"))): {"log": "Dancing feet are suddenly locked! A bizarre, twitching state!", "sound": "generic_spell_clash", "resolve": "custom:dance_then_leglock"},
    tuple(sorted(("Mimblewimble", "Langlock"))): {"log": "Tongue-Tying and Tongue-Locking! Speech becomes utterly impossible!", "sound": "status_inflict", "resolve": "custom:double_tongue_curse"},
    tuple(sorted(("Slugulus Eructo", "Anteoculatia"))): {"log": "Vomiting slugs while sprouting antlers! A dreadful sight!", "sound": "status_inflict", "resolve": "custom:slugs_and_antlers"},

    # Summoning Interactions
    tuple(sorted(("Serpensortia", "Avis"))): {"log": "Snakes and birds erupt from the wands, instantly fighting each other!", "sound": "generic_spell_clash", "resolve": "custom:snakes_vs_birds"},
    tuple(sorted(("Oppugno", "Avis"))): {"log": "The conjured birds are directed to attack by Oppugno!", "sound": "duel_hit", "resolve": "custom:oppugno_directs_avis"}, # Assumes Avis caster is target of Oppugno

    # Light/Flavor Interactions
    tuple(sorted(("Lumos", "Nox"))): {"log": "Light and darkness struggle, then neutralize each other.", "sound": "generic_spell_clash", "resolve": "both_fizzle"},
    tuple(sorted(("Lumos", "Lumos"))): {"log": "The area becomes exceptionally bright for a moment!", "sound": "spell_cast_ui", "resolve": "custom:double_lumos_flash"},
    tuple(sorted(("Orchideous", "Incendio"))): {"log": "Conjured flowers are instantly incinerated!", "sound": "elemental_clash_fire", "resolve": "custom:flowers_burn"},
}


DARK_THEME = {
    "bg": "#0C1C33", "fg": "#E0E0E0", "frame_bg": "#1A2B3C", "accent_bg": "#2A3B4D",
    "selected_tab_bg": "#3D5568", "button_fg": "#FFFFFF", "gold_fg": "#FFD700",
    "silver_fg": "#C0C0C0", "entry_bg": "#2A3B4D", "entry_fg": "#E0E0E0",
    "canvas_bg": "#0C1C33", "header_fg": "#FFD700", "history_date_fg": "#FFD700",
    "history_reason_fg": "#AAAAAA", "banner_text_light_bg": "#111111",
    "banner_text_dark_bg": "#F0F0F0", "disabled_fg": "#777777"
}

# ==== ENCHANTED FUNCTIONS ====
def play_sound(freq=440, duration=300, blocking=False):
    def play():
        if platform.system() == "Windows":
            try:
                if isinstance(freq, list):
                    for f_val in freq: winsound.Beep(f_val, duration)
                else: winsound.Beep(freq, duration)
            except Exception as e: print(f"Sound playback error (winsound): {e}")
        elif PYGAME_AVAILABLE and pygame.mixer.get_init():
            try:
                # This part is tricky for direct frequency beeps with pygame if not pre-loaded.
                # For complex sounds, pygame.mixer.Sound objects are better.
                # For simple beeps, winsound is more direct on Windows.
                # If truly needing cross-platform beeps via pygame, one might generate a sine wave.
                print(f"Pygame sound requested for freq: {freq} (simple beeps not directly implemented via freq in this example)")
            except Exception as e: print(f"Pygame sound error: {e}")
        else: pass # No sound playback method available or initialized
    if blocking: play()
    else: threading.Thread(target=play, daemon=True).start()

def create_scrollable_frame(parent, theme_colors):
    container = ttk.Frame(parent, style="Scrollable.TFrame")
    canvas = tk.Canvas(container, bg=theme_colors["canvas_bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
    scrollable_content_frame = ttk.Frame(canvas, style="ScrollableContent.TFrame")
    scrollable_content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_content_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    container.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True, padx=(0,2), pady=(0,2))
    scrollbar.pack(side="right", fill="y")
    return scrollable_content_frame, canvas, container

def ensure_directory(dir_name):
    if not os.path.exists(dir_name): os.makedirs(dir_name)

def get_asset_path(asset_name):
    ensure_directory(ASSETS_DIR)
    return os.path.join(ASSETS_DIR, asset_name)

def get_avatar_path(student_name):
    ensure_directory(AVATAR_DIR)
    safe_student_name = "".join(c if c.isalnum() else "_" for c in student_name)
    return os.path.join(AVATAR_DIR, f"{safe_student_name}.png")

def create_animated_sparkles(canvas, x, y, color="gold", size=15, count=8, duration_ms=1000):
    sparkles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, size)
        dx, dy = distance * math.cos(angle), distance * math.sin(angle)
        sparkle = canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color, outline="")
        sparkles.append({'id': sparkle, 'dx': dx / 20, 'dy': dy / 20, 'life': 20})
    def animate_sparkle_step():
        nonlocal sparkles
        active_sparkles = False
        for s_idx in range(len(sparkles) -1, -1, -1): # Iterate backwards for safe removal
            s = sparkles[s_idx]
            if s['life'] > 0:
                active_sparkles = True
                try:
                    if canvas.winfo_exists() and s['id'] in canvas.find_all(): # Check if item exists
                         canvas.move(s['id'], s['dx'], s['dy'])
                except tk.TclError: # Handle cases where item might be gone
                    sparkles.pop(s_idx)
                    continue
                s['life'] -= 1
                if s['life'] == 0: # If life ended
                    if canvas.winfo_exists() and s['id'] in canvas.find_all(): canvas.delete(s['id'])
                    sparkles.pop(s_idx)
            elif canvas.winfo_exists() and s['id'] in canvas.find_all(): # If life was already 0 but item somehow exists
                 canvas.delete(s['id'])
                 sparkles.pop(s_idx)

        if active_sparkles and canvas.winfo_exists(): # Only continue if there are active sparkles and canvas exists
            canvas.after(duration_ms // 20, animate_sparkle_step)
    if canvas.winfo_exists(): animate_sparkle_step()


def get_contrasting_text_color(hex_bg_color):
    try: r, g, b = tuple(int(hex_bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except ValueError: return DARK_THEME["banner_text_dark_bg"] # Default if color is invalid
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return DARK_THEME["banner_text_light_bg"] if luminance > 0.5 else DARK_THEME["banner_text_dark_bg"]

def generate_house_banner(house_name, width=200, height=100):
    house_data = HOUSES[house_name]
    img = Image.new("RGB", (width, height), house_data["color"])
    draw = ImageDraw.Draw(img)
    primary_font_size = max(22, int(height / 4.5))
    secondary_font_size = max(12, int(height / 7.5))
    try:
        font_path_title = get_asset_path("Lumos.ttf") # Ensure you have this font or use a fallback
        title_font = ImageFont.truetype(font_path_title, primary_font_size)
        font_path_detail = get_asset_path("arial.ttf") # Standard font
        detail_font = ImageFont.truetype(font_path_detail, secondary_font_size)
    except IOError:
        title_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()

    text_name = f"{house_data['animal']} {house_name}"
    name_color = house_data["secondary"]
    if house_name == "Ravenclaw": name_color = DARK_THEME["banner_text_dark_bg"] # Special case for Ravenclaw secondary
    
    name_bbox = draw.textbbox((0,0), text_name, font=title_font)
    name_width, name_height = name_bbox[2] - name_bbox[0], name_bbox[3] - name_bbox[1]
    draw.text(((width - name_width) / 2, (height * 0.33) - (name_height / 2)), text_name, fill=name_color, font=title_font)

    traits_text = house_data["traits"]
    traits_color = get_contrasting_text_color(house_data["color"])
    traits_bbox = draw.textbbox((0,0), traits_text, font=detail_font)
    traits_width, traits_height = traits_bbox[2] - traits_bbox[0], traits_bbox[3] - traits_bbox[1]
    draw.text(((width - traits_width) / 2, (height * 0.66) - (traits_height / 2)), traits_text, fill=traits_color, font=detail_font)
    
    # Add a border
    draw.rectangle([1,1, width-2, height-2], outline=house_data["secondary"], width=2)
    return ImageTk.PhotoImage(img)

# ==== MAGICAL GUI ====
class HogwartsTracker:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title(f"Hogwarts House Cup Tracker - {VERSION}")
        self.root.geometry("1350x980") # Adjusted default size
        self.root.minsize(1100, 700)
        self.theme_colors = DARK_THEME.copy()
        self.current_assignments = {}
        self.student_data = {} # Stores {"Student Name": {"points": X, "achievements": [], "hp": Y, "mp": Z, "status_effects": {}}}
        self.history = []
        self.spell_effects = [] # For main screen spell animations
        self.house_banners_photoimages = {} # Cache for generated banner images
        self.music_playing = False
        self.dueling_club_window = None # Reference to the DuelingClubWindow instance

        self.load_assets()
        self.setup_styles()
        self.create_main_frame()
        self.load_progress() # Load saved data
        self.apply_theme() # Apply theme colors and styles
        self.update_display() # Update all UI elements with current data
        self.center_window()
        self.animate_spell_effects_loop() # Start visual effect loop
        self.start_theme_music()

    def start_theme_music(self):
        if PYGAME_AVAILABLE:
            try:
                if not pygame.mixer.get_init(): pygame.mixer.init()
                song_path = get_asset_path(THEME_SONG_FILE)
                if os.path.exists(song_path):
                    pygame.mixer.music.load(song_path)
                    pygame.mixer.music.play(loops=-1) # Loop indefinitely
                    self.music_playing = True
                    if hasattr(self, "music_button"): self.music_button.configure(text="🎵 Mute")
                else:
                    print(f"Theme song not found at {song_path}")
                    self.music_playing = False
                    if hasattr(self, "music_button"): self.music_button.configure(text="🎵 Play", state=tk.DISABLED)
            except Exception as e:
                print(f"Could not play theme music: {e}")
                self.music_playing = False
                if hasattr(self, "music_button"): self.music_button.configure(text="🎵 Error", state=tk.DISABLED)
        elif hasattr(self, "music_button"): self.music_button.configure(text="🎵 N/A", state=tk.DISABLED)


    def toggle_music(self):
        if not PYGAME_AVAILABLE or not pygame.mixer.get_init():
            messagebox.showinfo("Music Error", "Pygame mixer not initialized or music file not loaded.", parent=self.root)
            return
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
            self.music_button.configure(text="🎵 Play")
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            self.music_button.configure(text="🎵 Mute")

    def animate_spell_effects_loop(self):
        if hasattr(self, 'main_canvas_scrollable_area'): # Ensure canvas exists
            for effect_idx in range(len(self.spell_effects) -1, -1, -1): # Iterate backwards
                effect = self.spell_effects[effect_idx]
                item_id, lifetime, dx, dy = effect
                if lifetime > 0:
                    try:
                        if self.main_canvas_scrollable_area.winfo_exists() and item_id in self.main_canvas_scrollable_area.find_all():
                            self.main_canvas_scrollable_area.move(item_id, dx, dy)
                            self.spell_effects[effect_idx] = (item_id, lifetime - 1, dx, dy)
                        else: # Item or canvas gone
                            self.spell_effects.pop(effect_idx)
                    except tk.TclError: # Catch error if item is already deleted
                        self.spell_effects.pop(effect_idx)
                else: # Lifetime ended
                    if self.main_canvas_scrollable_area.winfo_exists() and item_id in self.main_canvas_scrollable_area.find_all():
                        self.main_canvas_scrollable_area.delete(item_id)
                    self.spell_effects.pop(effect_idx)
        self.root.after(50, self.animate_spell_effects_loop) # Repeat animation step

    def center_window(self):
        self.root.update_idletasks() # Ensure window dimensions are up-to-date
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x_offset = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y_offset = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x_offset}+{y_offset}")

    def load_assets(self):
        try:
            bg_path = get_asset_path("hogwarts_bg_dark.jpg")
            self.bg_image_pil = Image.open(bg_path) if os.path.exists(bg_path) else None
            self.bg_photoimage = None # Will be created on resize
            logo_path = get_asset_path("hogwarts_logo.png")
            self.logo_image_pil = Image.open(logo_path) if os.path.exists(logo_path) else None
            if self.logo_image_pil: self.logo_photoimage = ImageTk.PhotoImage(self.logo_image_pil.resize((150,150), Image.Resampling.LANCZOS))
            else: self.logo_photoimage = None
            self.house_crests_pil = {}
            for house in HOUSES:
                crest_path = get_asset_path(f"{house.lower()}_crest.png")
                if os.path.exists(crest_path):
                    img = Image.open(crest_path).convert("RGBA") # Ensure RGBA for transparency
                    self.house_crests_pil[house] = img.resize((70,70), Image.Resampling.LANCZOS)
            self.house_crests_photoimages = {} # PhotoImages will be created in apply_theme
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.bg_image_pil = self.logo_photoimage = None
            self.house_crests_pil, self.house_crests_photoimages = {}, {}

        # Define fonts
        try:
            self.title_font = font.Font(family="Georgia", size=26, weight="bold")
            self.header_font = font.Font(family="Georgia", size=18)
            self.body_font = font.Font(family="Arial", size=12)
            self.small_body_font = font.Font(family="Arial", size=10)
            self.button_font = font.Font(family="Arial", size=11, weight="bold")
            self.student_list_header_font = font.Font(family="Arial", size=10, weight="bold")
            try: self.thematic_title_font = font.Font(family="Harry P", size=30, weight="bold") # Custom font
            except: self.thematic_title_font = self.title_font # Fallback
            try: self.thematic_header_font = font.Font(family="Lumos", size=22) # Custom font
            except: self.thematic_header_font = self.header_font # Fallback
        except tk.TclError: # Fallback if custom fonts fail
            df = font.nametofont("TkDefaultFont").actual()
            self.title_font, self.header_font, self.body_font, self.small_body_font, self.button_font = \
                (font.Font(family=df["family"], size=s) for s in [26,18,12,10,11])
            self.student_list_header_font = font.Font(family=df["family"], size=10, weight="bold")
            self.thematic_title_font, self.thematic_header_font = self.title_font, self.header_font

    def setup_styles(self):
        self.style = ttk.Style(); self.style.theme_use("clam"); tc = self.theme_colors
        self.style.configure("TFrame", background=tc["bg"])
        self.style.configure("TLabel", background=tc["bg"], foreground=tc["fg"], font=self.body_font)
        self.style.configure("TButton", font=self.button_font, padding=(10,6), borderwidth=1)
        self.style.map("TButton", relief=[('pressed','sunken'),('!pressed','raised')], background=[('active',tc["accent_bg"])])
        self.style.configure("TNotebook", background=tc["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=tc["accent_bg"], foreground=tc["fg"], padding=[12,8], font=self.body_font, borderwidth=1)
        self.style.map("TNotebook.Tab", background=[("selected",tc["selected_tab_bg"])], foreground=[("selected",tc["gold_fg"])])
        self.style.configure("TEntry", fieldbackground=tc["entry_bg"], foreground=tc["entry_fg"], insertcolor=tc["fg"], font=self.body_font, padding=5)
        self.style.configure("TCombobox", fieldbackground=tc["entry_bg"], foreground=tc["entry_fg"], selectbackground=tc["accent_bg"],selectforeground=tc["fg"],arrowcolor=tc["fg"],font=self.body_font)
        self.style.map("TCombobox", background=[('readonly',tc["entry_bg"])]) # Ensure readonly combobox also gets styled
        self.style.configure("Section.TFrame", background=tc["frame_bg"], borderwidth=1, relief="solid")
        self.style.configure("Scrollable.TFrame", background=tc["bg"])
        self.style.configure("ScrollableContent.TFrame", background=tc["bg"])
        self.style.configure("Vertical.TScrollbar", troughcolor=tc["bg"], background=tc["accent_bg"], arrowcolor=tc["fg"], borderwidth=0)
        self.style.map("Vertical.TScrollbar", background=[('active',tc["selected_tab_bg"])])

        for h,d in HOUSES.items():
            self.style.configure(f"{h}.TButton", foreground=tc["button_fg"], background=d["color"], font=self.button_font, padding=(12,8))
            self.style.map(f"{h}.TButton", background=[("active",d["secondary"]),("disabled","#666666")], foreground=[("active",get_contrasting_text_color(d["secondary"])),("disabled","#AAAAAA")])
        self.style.configure("Golden.TButton", foreground=get_contrasting_text_color(tc["gold_fg"]), background=tc["gold_fg"], font=self.button_font)
        self.style.map("Golden.TButton", background=[("active",HOUSES["Hufflepuff"]["color"])])
        self.style.configure("Destructive.TButton", foreground=tc["button_fg"], background=HOUSES["Gryffindor"]["color"], font=self.button_font)
        self.style.map("Destructive.TButton", background=[("active","#D32F2F")])

        self.style.configure("Title.TLabel", font=self.thematic_title_font, foreground=tc["header_fg"])
        self.style.configure("Header.TLabel", font=self.thematic_header_font, foreground=tc["header_fg"])
        self.style.configure("SubHeader.TLabel", font=self.header_font, foreground=tc["fg"])
        self.style.configure("StudentColumn.TLabel", font=self.student_list_header_font, foreground=tc["silver_fg"], background=tc["frame_bg"])
        self.style.configure("Body.TLabel", font=self.body_font, foreground=tc["fg"])
        self.style.configure("Small.TLabel", font=self.small_body_font, foreground=tc["silver_fg"])
        self.style.configure("Gold.TLabel", font=self.body_font, foreground=tc["gold_fg"])
        self.style.configure("HistoryDate.TLabel", font=self.small_body_font, foreground=tc["history_date_fg"])
        self.style.configure("HistoryAction.TLabel", font=self.body_font, foreground=tc["fg"])
        self.style.configure("HistoryReason.TLabel", font=self.small_body_font, foreground=tc["history_reason_fg"], wraplength=500) # Wraplength for long reasons

        for h,d in HOUSES.items(): self.style.configure(f"{h}.Horizontal.TProgressbar", thickness=25, troughcolor=tc["frame_bg"], background=d["color"], bordercolor=d["secondary"], lightcolor=d["color"], darkcolor=d["color"])
        self.style.configure("TRadiobutton", background=tc["bg"], foreground=tc["fg"], font=self.body_font, indicatorrelief="flat", indicatormargin=5,padding=5)
        self.style.map("TRadiobutton", background=[('active',tc["accent_bg"])], indicatorbackground=[('selected',tc["gold_fg"]),('!selected',tc["entry_bg"])])
        self.style.configure("DuelLog.TLabel", font=self.small_body_font, foreground=tc["fg"], background=tc["entry_bg"])


    def apply_theme(self):
        self.root.configure(bg=self.theme_colors["bg"])
        self.setup_styles() # Re-apply styles based on current theme_colors
        if self.bg_image_pil:
            try:
                if hasattr(self, 'main_container'): # Ensure main_container exists
                    win_w, win_h = self.root.winfo_width(), self.root.winfo_height()
                    if win_w <=1 or win_h <=1: win_w, win_h = 1280, 960 # Default if window not drawn
                    rs_bg = self.bg_image_pil.resize((win_w,win_h), Image.Resampling.LANCZOS)
                    self.bg_photoimage = ImageTk.PhotoImage(rs_bg)
                    if hasattr(self,'background_label'): self.background_label.configure(image=self.bg_photoimage); self.background_label.image=self.bg_photoimage
            except Exception as e: print(f"Error resizing background image: {e}"); self._clear_bg_image()
        elif hasattr(self,'background_label'): self._clear_bg_image()

        # Regenerate PhotoImages for crests (necessary if theme changes affect image processing)
        self.house_crests_photoimages.clear()
        for h,p_img in self.house_crests_pil.items(): self.house_crests_photoimages[h] = ImageTk.PhotoImage(p_img)

        # Regenerate House Banners
        self.house_banners_photoimages.clear()
        if hasattr(self, 'banner_frame_content'):
            for w in self.banner_frame_content.winfo_children(): w.destroy() # Clear old banners
            for h in HOUSES:
                b_img = generate_house_banner(h, width=250, height=120) # Use the generation function
                self.house_banners_photoimages[h] = b_img
                b_lbl = tk.Label(self.banner_frame_content, image=b_img, bg=self.theme_colors["frame_bg"], relief="flat", bd=0)
                b_lbl.pack(side="left", expand=True, fill="x", padx=10, pady=5)
                b_lbl.bind("<Button-1>", lambda e, house_name=h: self.show_house_details(house_name))
                b_lbl.bind("<Enter>", lambda e,b=b_lbl: b.config(relief="solid",bd=2,borderwidth=2)) # Hover effect
                b_lbl.bind("<Leave>", lambda e,b=b_lbl: b.config(relief="flat",bd=0,borderwidth=0))  # No hover effect

        self.update_widget_themes(self.root) # Recursively update widget styles
        if hasattr(self,'main_canvas_scrollable_area'): self.main_canvas_scrollable_area.configure(bg=self.theme_colors["canvas_bg"])
        self.update_display() # Refresh data displays

    def _clear_bg_image(self):
        if hasattr(self, 'background_label'): self.background_label.configure(image=None, bg=self.theme_colors["bg"])

    def update_widget_themes(self, parent_widget): # Helper to recursively apply theme to basic tk widgets
        for child in parent_widget.winfo_children():
            widget_class = child.winfo_class()
            # Apply to basic tk widgets that don't use ttk styles directly for bg/fg
            if isinstance(child, (tk.Label, tk.Frame, tk.Canvas, tk.Toplevel, tk.Text, tk.Listbox)):
                try: # Some widgets might not have 'style' cget option
                    cs = child.cget("style")
                    if "TFrame" in cs: # If it's a ttk.Frame with a style
                        if cs=="Section.TFrame": child.configure(bg=self.theme_colors["frame_bg"])
                        elif cs=="ScrollableContent.TFrame": child.configure(bg=self.theme_colors["bg"])
                        # else: let ttk handle it
                    else: # Not a TFrame or no specific style, assume basic tk widget
                        child.configure(bg=self.theme_colors["bg"])
                except tk.TclError: # If cget("style") fails, it's likely a basic tk widget
                     try: child.configure(bg=self.theme_colors["bg"])
                     except tk.TclError: pass # Some widgets like Toplevel might not have bg
                # Set foreground for labels if not an image label
                if not isinstance(child, tk.Canvas) and not (isinstance(child, tk.Label) and child.cget("image")):
                    try: child.configure(fg=self.theme_colors["fg"])
                    except tk.TclError: pass

            if "ttk" in widget_class.lower(): # If it's a ttk widget, ensure its style is reapplied
                cs = child.cget("style")
                if cs:
                    try: child.configure(style=cs) # Reapply its own style
                    except tk.TclError: pass # Style might not be applicable in some contexts

            # Special handling for specific styled ttk widgets if needed
            if widget_class == 'TNotebook': child.configure(style="TNotebook")
            elif widget_class == 'TEntry' or widget_class == 'TCombobox': child.configure(style=widget_class) # Reapply base style

            # Special handling for student display list items background
            if hasattr(self,'student_display_content_frame') and parent_widget == self.student_display_content_frame:
                if isinstance(child, ttk.Frame): # Each row is a TFrame
                    child.configure(style="Section.TFrame") # Ensure row frame has correct bg
                    for gc in child.winfo_children(): # Grandchildren (labels, buttons in the row)
                        if isinstance(gc, tk.Label) and not gc.cget("image"): # If it's a text tk.Label
                            is_house_label = False # Check if it's the special house label
                            try:
                                parts = gc.cget("text").split(" ", 1)
                                if len(parts)==2 and parts[0]==HOUSES[parts[1]]["animal"]: is_house_label=True
                            except: pass
                            if not is_house_label: gc.configure(bg=self.theme_colors["frame_bg"], fg=self.theme_colors["fg"])
                            else: gc.configure(bg=self.theme_colors["frame_bg"]) # House label color is set separately
                        elif isinstance(gc, ttk.Label) and gc.cget("style") != "StudentColumn.TLabel": # ttk.Labels in row
                             gc.configure(style=gc.cget("style"), background=self.theme_colors["frame_bg"])


            self.update_widget_themes(child) # Recurse

    def create_main_frame(self):
        self.root.configure(bg=self.theme_colors["bg"])
        self.main_container = ttk.Frame(self.root, style="TFrame")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Background Image Label (placed first, then lowered)
        self.background_label = tk.Label(self.main_container) # No bg initially, will be set by theme
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.lower() # Send to back

        # Header Frame
        header_frame = ttk.Frame(self.main_container, style="Section.TFrame", padding=(10,5))
        header_frame.pack(fill="x", pady=(0, 10)) # Place header above scrollable content

        if self.logo_photoimage:
            logo_lbl = tk.Label(header_frame, image=self.logo_photoimage, bg=self.theme_colors["frame_bg"])
            logo_lbl.pack(side="left", padx=(0,20), pady=5)
        ttk.Label(header_frame, text="Hogwarts House Cup Tracker", style="Title.TLabel").pack(side="left", padx=10)

        # Control frame for buttons on the right of header
        ctrl_frame = ttk.Frame(header_frame, style="Section.TFrame") # Use Section.TFrame for consistent bg
        ctrl_frame.pack(side="right", padx=5)

        self.music_button = ttk.Button(ctrl_frame, text="🎵 Mute", command=self.toggle_music, style="TButton", width=8)
        self.music_button.pack(side="left", padx=(0,10), pady=5)
        if not PYGAME_AVAILABLE or not os.path.exists(get_asset_path(THEME_SONG_FILE)): self.music_button.configure(text="🎵 N/A", state=tk.DISABLED)

        ttk.Button(ctrl_frame, text="⚔️ Dueling Club", command=self.start_duel_setup, style="Golden.TButton", width=15).pack(side="left", padx=(0,10), pady=5)
        ttk.Button(ctrl_frame, text="🔮 Cast Spell", command=self.cast_spell, style="Golden.TButton", width=12).pack(side="left", padx=(0,10), pady=5)
        ttk.Label(ctrl_frame, text=f"v{VERSION}", style="Small.TLabel", padding=(10,0)).pack(side="left", pady=5)


        # Main Scrollable Area
        self.main_content_scrollable_frame, self.main_canvas_scrollable_area, _ = create_scrollable_frame(self.main_container, self.theme_colors)

        # Sections within the scrollable area
        self.create_points_display(self.main_content_scrollable_frame)
        self.create_action_buttons(self.main_content_scrollable_frame)
        self.create_student_section(self.main_content_scrollable_frame)
        self.create_banners_section(self.main_content_scrollable_frame) # Banners below students

        # Footer (outside scrollable area)
        footer = ttk.Frame(self.main_container, style="Section.TFrame", padding=5)
        footer.pack(fill="x", pady=(10,0))
        ttk.Button(footer, text="ℹ️ Help & About", command=self.show_help, style="TButton").pack(side="right", padx=5, pady=5)

        # Mousewheel binding for main scroll area
        self.main_canvas_scrollable_area.bind_all("<MouseWheel>", self._on_mousewheel_main) # Windows/macOS
        self.main_canvas_scrollable_area.bind_all("<Button-4>", lambda e: self._on_mousewheel_main(e,-1)) # Linux scroll up
        self.main_canvas_scrollable_area.bind_all("<Button-5>", lambda e: self._on_mousewheel_main(e,1))  # Linux scroll down


    def _on_mousewheel_main(self, event, direction=None): # Handles mousewheel scrolling for main canvas
        if not hasattr(self,'main_canvas_scrollable_area'): return
        delta = 0
        if direction is not None: # Linux Button-4/5 events
            delta = direction
        elif platform.system() == 'Windows':
            delta = -1 * (event.delta // 120)
        elif platform.system() == 'Darwin': # macOS
            delta = event.delta
        else: # Other systems might need different handling or might not provide event.delta
            delta = -1*(event.delta//120) if hasattr(event, 'delta') else 0

        self.main_canvas_scrollable_area.yview_scroll(int(delta), "units")


    def start_duel_setup(self):
        if not self.student_data or len(self.student_data) < 2:
            messagebox.showerror("Dueling Club Error", "You need at least two students in the roster to start a duel.", parent=self.root)
            play_sound(SOUNDS["error"])
            return

        if self.dueling_club_window and self.dueling_club_window.winfo_exists():
            self.dueling_club_window.lift() # Bring to front if already open
            messagebox.showinfo("Dueling Club", "A duel is already in progress or set up. Close the current duel window to start a new one.", parent=self.root)
            return

        play_sound(SOUNDS["duel_start"])
        self.dueling_club_window = DuelingClubWindow(self.root, self, self.theme_colors, self.student_data, SPELL_DETAILS, POTIONS, SPELL_INTERACTIONS, SOUNDS)


    def create_points_display(self, parent):
        po_frame = ttk.Frame(parent, style="Section.TFrame", padding=10)
        po_frame.pack(fill="x", pady=10, padx=5)
        ttk.Label(po_frame, text="House Points Standings", style="Header.TLabel").pack(pady=(0,15))
        self.house_displays_elements = {} # To store references to UI elements for each house
        pg_frame = ttk.Frame(po_frame, style="Section.TFrame") # Inner frame for grid layout
        pg_frame.pack(fill="x", expand=True)

        for i,(h,d) in enumerate(HOUSES.items()):
            h_frame = ttk.Frame(pg_frame, style="Section.TFrame", padding=10)
            h_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ewns")
            pg_frame.grid_columnconfigure(i%2, weight=1) # Make columns expand equally

            cn_frame = ttk.Frame(h_frame, style="Section.TFrame") # Frame for crest and name
            cn_frame.pack(fill="x", pady=(0,5))

            icon_lbl = None
            if h in self.house_crests_photoimages: # Use loaded crest image
                icon_lbl = tk.Label(cn_frame, image=self.house_crests_photoimages[h], bg=self.theme_colors["frame_bg"])
            else: # Fallback to animal emoji
                icon_lbl = ttk.Label(cn_frame, text=d["animal"], style="Header.TLabel", foreground=d["color"], background=self.theme_colors["frame_bg"])
            icon_lbl.pack(side="left", padx=(0,10))

            n_lbl = ttk.Label(cn_frame, text=h, style="SubHeader.TLabel", foreground=d["color"])
            n_lbl.pack(side="left", anchor="w")

            pv_lbl = ttk.Label(h_frame, text=str(d["points"]), style="Title.TLabel", foreground=self.theme_colors["gold_fg"])
            pv_lbl.pack(pady=(0,5))
            p_bar = ttk.Progressbar(h_frame, orient="horizontal", length=300, mode="determinate", style=f"{h}.Horizontal.TProgressbar")
            p_bar.pack(fill="x", pady=(0,5))
            t_lbl = ttk.Label(h_frame, text=d["traits"], style="Small.TLabel", wraplength=280, justify="center")
            t_lbl.pack(pady=(5,0))
            self.house_displays_elements[h] = {"frame":h_frame,"icon":icon_lbl,"name":n_lbl,"points_value":pv_lbl,"progress":p_bar,"traits":t_lbl}

    def create_action_buttons(self, parent):
        btn_frame = ttk.Frame(parent, style="Section.TFrame", padding=10)
        btn_frame.pack(fill="x", pady=10, padx=5)
        ttk.Label(btn_frame, text="Magical Actions", style="Header.TLabel").pack(pady=(0,15))
        btn_cont = ttk.Frame(btn_frame, style="Section.TFrame") # Container for button grid
        btn_cont.pack(fill="x")
        actions = [("🏆 Award/Deduct Points",self.award_points_dialog,"Golden.TButton"),("🌟 Award Achievement",self.award_achievement_dialog,"Golden.TButton"),("🎩 Assign Houses",self.assign_houses_ceremony,"Golden.TButton"),("🎲 Random Event",self.trigger_random_event,"TButton"),("📜 House Details",lambda: self.show_house_details(),"TButton"),("🔄 Reset Points",self.confirm_reset_points,"Destructive.TButton")]
        for i,(txt,cmd,st) in enumerate(actions):
            r,c = divmod(i,3) # Arrange in 2 rows, 3 columns
            act_btn = ttk.Button(btn_cont,text=txt,command=cmd,style=st,width=25)
            act_btn.grid(row=r,column=c,padx=5,pady=5,sticky="ew")
        for i in range(3): btn_cont.columnconfigure(i,weight=1) # Make columns responsive

    def create_student_section(self, parent):
        so_frame = ttk.Frame(parent, style="Section.TFrame", padding=10)
        so_frame.pack(fill="both", expand=True, pady=10, padx=5)
        sh_frame = ttk.Frame(so_frame, style="Section.TFrame") # Header for student section
        sh_frame.pack(fill="x", pady=(0,10))
        ttk.Label(sh_frame, text="Student Parchments", style="Header.TLabel").pack(side="left",pady=(0,5))
        ttk.Button(sh_frame,text="➕ Edit Students",command=self.edit_students_dialog,style="TButton").pack(side="right",padx=5)
        ttk.Button(sh_frame,text="⏳ View History Log",command=self.show_history_log,style="TButton").pack(side="right",padx=5)

        self.student_notebook = ttk.Notebook(so_frame, style="TNotebook")
        self.student_notebook.pack(fill="both", expand=True, pady=(5,0))

        # Student Points Tab
        self.points_tab_content = ttk.Frame(self.student_notebook, style="TFrame", padding=10)
        self.student_notebook.add(self.points_tab_content, text="🎓 Student Points")
        self.student_display_scrollable_frame, self.student_display_canvas, _ = create_scrollable_frame(self.points_tab_content, self.theme_colors)
        self.student_display_content_frame = self.student_display_scrollable_frame # This is the frame to add student rows to
        self.student_display_content_frame.configure(style="Section.TFrame") # Style the content frame itself

        # Achievements List Tab
        self.achievements_tab_content = ttk.Frame(self.student_notebook, style="TFrame", padding=10)
        self.student_notebook.add(self.achievements_tab_content, text="🌟 Achievements List")
        self.achievements_display_scrollable_frame, self.achievements_display_canvas, _ = create_scrollable_frame(self.achievements_tab_content, self.theme_colors)
        self.achievements_display_content_frame = self.achievements_display_scrollable_frame
        self.achievements_display_content_frame.configure(style="Section.TFrame")

        self.update_student_points_display() # Initial population
        self.update_achievements_list_display() # Initial population

    def create_banners_section(self, parent):
        bo_frame = ttk.Frame(parent, style="Section.TFrame", padding=10)
        bo_frame.pack(fill="x", pady=10, padx=5)
        ttk.Label(bo_frame, text="House Banners", style="Header.TLabel").pack(pady=(0,10))
        self.banner_frame_content = ttk.Frame(bo_frame, style="Section.TFrame")
        self.banner_frame_content.pack(fill="x")
        # Banners are populated in apply_theme

    def update_display(self):
        if not hasattr(self,'house_displays_elements'): return # Not initialized yet
        max_pts = max(max(d["points"] for d in HOUSES.values()),1) # Avoid division by zero if all points are 0 or negative
        for h,d in HOUSES.items():
            els = self.house_displays_elements[h]
            els["points_value"].configure(text=str(d["points"]))
            prog_val = (d["points"]/max_pts)*100 if d["points"]>=0 else 0 # Progress bar only for positive points
            els["progress"]["value"] = prog_val
            els["progress"].configure(style=f"{h}.Horizontal.TProgressbar") # Re-apply style for color
            if h in self.house_crests_photoimages and isinstance(els["icon"],tk.Label): # Update crest image if it's a tk.Label
                els["icon"].configure(image=self.house_crests_photoimages[h],bg=self.theme_colors["frame_bg"])
                els["icon"].image = self.house_crests_photoimages[h] # Keep reference
            elif isinstance(els["icon"],ttk.Label): # Ensure ttk.Label bg is correct
                els["icon"].configure(background=self.theme_colors["frame_bg"])

        self.update_student_points_display()
        self.update_achievements_list_display()

        # Ensure canvas backgrounds are correct after theme changes
        if hasattr(self,'main_canvas_scrollable_area'): self.main_canvas_scrollable_area.configure(bg=self.theme_colors["canvas_bg"])
        if hasattr(self,'student_display_canvas'):
            self.student_display_canvas.configure(bg=self.theme_colors["canvas_bg"])
            self.student_display_content_frame.configure(style="Section.TFrame") # Re-apply style
        if hasattr(self,'achievements_display_canvas'):
            self.achievements_display_canvas.configure(bg=self.theme_colors["canvas_bg"])
            self.achievements_display_content_frame.configure(style="Section.TFrame") # Re-apply style


    def update_student_points_display(self):
        if not hasattr(self,'student_display_content_frame'): return
        for w in self.student_display_content_frame.winfo_children(): w.destroy() # Clear previous entries

        if not self.current_assignments:
            ttk.Label(self.student_display_content_frame,text="No house assignments yet. Use 'Assign Houses'!",style="Body.TLabel",wraplength=400,justify="center").pack(pady=20)
            return

        # Header row for student list
        header = ttk.Frame(self.student_display_content_frame, style="Section.TFrame", padding=(5,3))
        header.pack(fill="x", pady=(0,5), padx=2)
        header.columnconfigure(0, weight=3, uniform="student_col", minsize=150) # Student Name
        header.columnconfigure(1, weight=2, uniform="student_col", minsize=100) # House
        header.columnconfigure(2, weight=1, uniform="student_col", minsize=60)  # Points
        header.columnconfigure(3, weight=2, uniform="student_col", minsize=120) # Actions

        cols_cfg = [("Student Name",0),("House",1),("Points",2),("Actions",3)]
        for txt,col_idx in cols_cfg:
            ttk.Label(header,text=txt,style="StudentColumn.TLabel").grid(row=0,column=col_idx,sticky="nsew",padx=5, pady=2)

        sorted_students = sorted(self.student_data.keys())
        for s_name in sorted_students:
            s_data = self.student_data[s_name]
            h_name = self.current_assignments.get(s_name,"N/A")
            h_data = HOUSES.get(h_name,{"color":self.theme_colors["fg"],"animal":"❓"}) # Fallback data

            row_f = ttk.Frame(self.student_display_content_frame,style="Section.TFrame",padding=(5,4))
            row_f.pack(fill="x",pady=1, padx=2) # padx to align with header
            row_f.columnconfigure(0, weight=3, uniform="student_col", minsize=150)
            row_f.columnconfigure(1, weight=2, uniform="student_col", minsize=100)
            row_f.columnconfigure(2, weight=1, uniform="student_col", minsize=60)
            row_f.columnconfigure(3, weight=2, uniform="student_col", minsize=120)


            ttk.Label(row_f,text=s_name,style="Body.TLabel",anchor="w").grid(row=0,column=0,sticky="nsew",padx=5)
            h_lbl_txt = f"{h_data['animal']} {h_name}"
            # Use tk.Label for house name to allow direct fg color setting based on house
            s_h_lbl = tk.Label(row_f,text=h_lbl_txt,font=self.body_font,fg=h_data["color"],bg=self.theme_colors["frame_bg"],anchor="w")
            s_h_lbl.grid(row=0,column=1,sticky="nsew",padx=5)
            ttk.Label(row_f,text=str(s_data.get("points",0)),style="Gold.TLabel",anchor="e").grid(row=0,column=2,sticky="nsew",padx=5)

            acts_sub_f = ttk.Frame(row_f,style="Section.TFrame") # Frame for action buttons in the cell
            acts_sub_f.grid(row=0,column=3,sticky="nsew",padx=5)
            acts_sub_f.columnconfigure(0, weight=1) # Allow buttons to expand
            acts_sub_f.columnconfigure(1, weight=1)
            ttk.Button(acts_sub_f,text="👤 Profile",command=lambda s=s_name:self.show_student_profile_dialog(s),style="TButton",width=8).pack(side="left",padx=2, expand=True, fill="x")
            ttk.Button(acts_sub_f,text="✨ +/-",command=lambda s=s_name:self.quick_points_adjust_dialog(s),style="TButton",width=6).pack(side="left",padx=2, expand=True, fill="x")


    def update_achievements_list_display(self):
        if not hasattr(self, 'achievements_display_content_frame'): return
        for widget in self.achievements_display_content_frame.winfo_children(): widget.destroy()
        ttk.Label(self.achievements_display_content_frame, text="Scroll of Esteemed Accomplishments", style="Header.TLabel").pack(pady=(0,15), anchor="center")

        ach_grid = ttk.Frame(self.achievements_display_content_frame, style="Section.TFrame")
        ach_grid.pack(fill="x")

        for i, (achievement_name, data) in enumerate(ACHIEVEMENTS.items()):
            row, col = divmod(i, 2) # 2 achievements per row
            ach_frame = ttk.Frame(ach_grid, style="Section.TFrame", padding=10, borderwidth=1, relief="groove")
            ach_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            ach_grid.columnconfigure(col, weight=1) # Make columns expand

            icon_label = tk.Label(ach_frame, text=data["icon"], bg=data["color"], fg=get_contrasting_text_color(data["color"]), font=(self.body_font.cget("family"), 20, "bold"), width=2, height=1, relief="raised", bd=2)
            icon_label.pack(side="left", padx=(0, 10))

            info_frame = ttk.Frame(ach_frame, style="Section.TFrame")
            info_frame.pack(side="left", fill="x", expand=True)
            ttk.Label(info_frame, text=achievement_name, style="SubHeader.TLabel", foreground=data["color"]).pack(anchor="w")
            ttk.Label(info_frame, text=data["description"], style="Small.TLabel", wraplength=250).pack(anchor="w", pady=(2,0))

            ttk.Label(ach_frame, text=f"+{data['points']} pts", style="Gold.TLabel", font=self.header_font).pack(side="right", padx=(10,0))


    def show_student_profile_dialog(self, student_name):
        profile_win = tk.Toplevel(self.root)
        profile_win.title(f"{student_name}'s Profile")
        profile_win.geometry("750x700") # Slightly larger for more content
        profile_win.configure(bg=self.theme_colors["bg"])
        profile_win.resizable(True, True)
        profile_win.grab_set()
        profile_win.transient(self.root)

        main_profile_frame, profile_canvas, _ = create_scrollable_frame(profile_win, self.theme_colors)
        profile_canvas.configure(bg=self.theme_colors["frame_bg"]) # Content area background

        # Header Section (Avatar, Name, House, Points, HP/MP)
        header_section = ttk.Frame(main_profile_frame, style="Section.TFrame", padding=15)
        header_section.pack(fill="x", pady=10, padx=10)

        avatar_frame = ttk.Frame(header_section, style="Section.TFrame")
        avatar_frame.pack(side="left", padx=(0, 20))
        avatar_path = get_avatar_path(student_name)
        avatar_photo = None
        try:
            if os.path.exists(avatar_path):
                img = Image.open(avatar_path)
                img = ImageOps.fit(img, (120, 120), Image.Resampling.LANCZOS) # Fit and crop
                avatar_photo = ImageTk.PhotoImage(img)
        except Exception as e: print(f"Error loading avatar for {student_name}: {e}")

        if avatar_photo:
            avatar_label = tk.Label(avatar_frame, image=avatar_photo, bg=self.theme_colors["frame_bg"], relief="solid", borderwidth=1)
            avatar_label.image = avatar_photo # Keep reference
        else: # Fallback avatar
            house_animal = HOUSES.get(self.current_assignments.get(student_name, ""), {}).get("animal", "👤")
            avatar_label = tk.Label(avatar_frame, text=house_animal, font=("Arial", 60), bg=self.theme_colors["accent_bg"], fg=self.theme_colors["gold_fg"], width=2, height=1, relief="groove", borderwidth=2)
        avatar_label.pack(pady=(0,5))
        ttk.Button(avatar_frame, text="🖼️ Change Avatar", command=lambda s=student_name, w=profile_win: self.upload_avatar_for_student(s, w), style="TButton", width=15).pack()

        info_section = ttk.Frame(header_section, style="Section.TFrame")
        info_section.pack(side="left", fill="x", expand=True)
        student_house = self.current_assignments.get(student_name, "Unsorted")
        house_data = HOUSES.get(student_house, {"animal": "", "traits": "N/A", "color": self.theme_colors["fg"]})
        ttk.Label(info_section, text=student_name, style="Title.TLabel", foreground=house_data.get("color", self.theme_colors["gold_fg"])).pack(anchor="w")
        ttk.Label(info_section, text=f"{house_data['animal']} {student_house}", style="Header.TLabel", foreground=house_data["color"]).pack(anchor="w", pady=(0,5))
        s_data = self.student_data.get(student_name, {})
        ttk.Label(info_section, text=f"Points: {s_data.get('points', 0)}", style="SubHeader.TLabel", foreground=self.theme_colors["gold_fg"]).pack(anchor="w", pady=(0,2))
        ttk.Label(info_section, text=f"HP: {s_data.get('hp', DEFAULT_HP)} / {DEFAULT_HP}", style="Body.TLabel").pack(anchor="w") # Show max HP
        ttk.Label(info_section, text=f"MP: {s_data.get('mp', DEFAULT_MP)} / {DEFAULT_MP}", style="Body.TLabel").pack(anchor="w", pady=(0,5)) # Show max MP
        ttk.Label(info_section, text=f"Traits: {house_data['traits']}", style="Body.TLabel", wraplength=300).pack(anchor="w")


        # Achievements Section
        ach_section = ttk.Frame(main_profile_frame, style="Section.TFrame", padding=10)
        ach_section.pack(fill="x", pady=10, padx=10)
        ttk.Label(ach_section, text="🌟 Earned Achievements", style="Header.TLabel").pack(pady=(0,10))
        student_achievements_list = s_data.get("achievements", [])
        if not student_achievements_list: ttk.Label(ach_section, text="No achievements earned yet.", style="Body.TLabel").pack(pady=10)
        else:
            for ach_name in student_achievements_list:
                ach_data = ACHIEVEMENTS.get(ach_name, {})
                if not ach_data: continue # Skip if achievement definition is missing
                ach_item_frame = ttk.Frame(ach_section, style="Section.TFrame", padding=5)
                ach_item_frame.pack(fill="x", pady=3)
                tk.Label(ach_item_frame, text=ach_data.get("icon", "🏆"), font=("Arial", 16), bg=ach_data.get("color", "#CCCCCC"), fg=get_contrasting_text_color(ach_data.get("color", "#CCCCCC")), width=2).pack(side="left", padx=(0,10))
                ttk.Label(ach_item_frame, text=f"{ach_name} (+{ach_data.get('points',0)} pts)", style="Body.TLabel").pack(side="left", anchor="w")

        # History Section for the student
        history_section = ttk.Frame(main_profile_frame, style="Section.TFrame", padding=10)
        history_section.pack(fill="both", expand=True, pady=10, padx=10)
        ttk.Label(history_section, text="📜 Student's Chronicle", style="Header.TLabel").pack(pady=(0,10))
        student_history_content, student_history_canvas, _ = create_scrollable_frame(history_section, self.theme_colors)
        student_history_canvas.configure(bg=self.theme_colors["frame_bg"], height=150) # Limit initial height

        filtered_student_history = [entry for entry in reversed(self.history) if entry.get("student") == student_name or student_name.lower() in entry.get("action", "").lower() or student_name.lower() in entry.get("reason","").lower()]
        if not filtered_student_history: ttk.Label(student_history_content, text="No specific history entries for this student.", style="Body.TLabel", padding=10).pack()
        else:
            for entry in filtered_student_history[:15]: # Show last 15 relevant entries
                entry_frame = ttk.Frame(student_history_content, style="Section.TFrame", padding=5, relief="groove", borderwidth=1)
                entry_frame.pack(fill="x", pady=3, padx=2)
                ttk.Label(entry_frame, text=entry.get('date', 'N/A'), style="HistoryDate.TLabel").pack(anchor="w")
                ttk.Label(entry_frame, text=entry.get('action', 'Activity'), style="HistoryAction.TLabel", wraplength=650).pack(anchor="w", pady=(2,0))
                if entry.get('reason'): ttk.Label(entry_frame, text=f"Details: {entry['reason']}", style="HistoryReason.TLabel", wraplength=650).pack(anchor="w", pady=(2,0))

        ttk.Button(main_profile_frame, text="Done", command=profile_win.destroy, style="Golden.TButton").pack(pady=15)


    def quick_points_adjust_dialog(self, student_name):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Adjust Points: {student_name}")
        dialog.geometry("350x250")
        dialog.configure(bg=self.theme_colors["bg"])
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)

        ttk.Label(dialog, text=f"Adjust Points for {student_name}", style="Header.TLabel").pack(pady=10)
        points_frame = ttk.Frame(dialog, style="TFrame")
        points_frame.pack(pady=10)
        ttk.Label(points_frame, text="Points:", style="Body.TLabel").pack(side="left", padx=5)
        points_entry = ttk.Entry(points_frame, font=self.body_font, width=8)
        points_entry.pack(side="left")
        points_entry.insert(0, "10")
        points_entry.focus()

        action_var = tk.StringVar(value="add")
        radio_frame = ttk.Frame(dialog, style="TFrame")
        radio_frame.pack(pady=5)
        ttk.Radiobutton(radio_frame, text="Add", variable=action_var, value="add", style="TRadiobutton").pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame, text="Deduct", variable=action_var, value="deduct", style="TRadiobutton").pack(side="left", padx=10)

        reason_entry = ttk.Entry(dialog, font=self.body_font, width=30)
        reason_entry.pack(pady=5)
        reason_entry.insert(0, "Quick adjustment")

        def apply_quick_points():
            try:
                points_val = int(points_entry.get())
                reason_val = reason_entry.get() or "Quick adjustment"
                if action_var.get() == "deduct": points_val = -points_val

                student_house = self.current_assignments.get(student_name)
                if not student_house:
                    messagebox.showerror("Error", f"{student_name} is not assigned to a house.", parent=dialog)
                    return

                HOUSES[student_house]["points"] += points_val
                s_data = self.student_data.get(student_name, self._get_default_student_data())
                s_data["points"] = s_data.get("points", 0) + points_val
                self.student_data[student_name] = s_data # Ensure update

                self.history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"{'Added' if points_val > 0 else 'Deducted'} {abs(points_val)} points for {student_name} ({student_house})", "reason": reason_val, "student": student_name})
                self.save_progress(); self.update_display(); play_sound(SOUNDS["points"]); dialog.destroy()
            except ValueError: messagebox.showerror("Error", "Invalid points value.", parent=dialog); play_sound(SOUNDS["error"])

        ttk.Button(dialog, text="Apply", command=apply_quick_points, style="Golden.TButton").pack(pady=10)


    def upload_avatar_for_student(self, student_name, parent_window):
        file_path = filedialog.askopenfilename(parent=parent_window, title=f"Select Avatar for {student_name}", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not file_path: return
        try:
            ensure_directory(AVATAR_DIR)
            avatar_save_path = get_avatar_path(student_name)
            img = Image.open(file_path)
            img = ImageOps.fit(img, (200, 200), Image.Resampling.LANCZOS) # Standard size
            img.save(avatar_save_path, "PNG") # Save as PNG for consistency
            play_sound(SOUNDS["points"])
            messagebox.showinfo("Success", f"Avatar updated for {student_name}.", parent=parent_window)
            if parent_window.winfo_exists(): # If profile window is open, refresh it
                 parent_window.destroy(); self.show_student_profile_dialog(student_name)
            self.update_student_points_display() # Update main list if needed
        except Exception as e: messagebox.showerror("Error", f"Failed to upload avatar: {e}", parent=parent_window); play_sound(SOUNDS["error"])

    def award_points_dialog(self):
        if not self.current_assignments: messagebox.showerror("Error", "Assign houses to students first!", parent=self.root); play_sound(SOUNDS["error"]); return
        dialog = tk.Toplevel(self.root); dialog.title("Award/Deduct Points"); dialog.geometry("500x450")
        dialog.configure(bg=self.theme_colors["bg"]); dialog.resizable(False, False); dialog.grab_set(); dialog.transient(self.root)

        ttk.Label(dialog, text="Modify House & Student Points", style="Header.TLabel").pack(pady=10)

        student_frame = ttk.Frame(dialog, style="TFrame"); student_frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(student_frame, text="Target Student (Optional):", style="Body.TLabel").pack(side="left", padx=(0,5))
        student_var = tk.StringVar(); student_names = ["(Whole House)"] + sorted(list(self.current_assignments.keys()))
        student_dropdown = ttk.Combobox(student_frame, textvariable=student_var, values=student_names, font=self.body_font, state="readonly", width=25)
        student_dropdown.pack(side="left", expand=True, fill="x"); student_dropdown.set("(Whole House)")

        house_frame = ttk.Frame(dialog, style="TFrame"); house_frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(house_frame, text="Target House:", style="Body.TLabel").pack(side="left", padx=(0,5))
        house_var = tk.StringVar()
        house_dropdown = ttk.Combobox(house_frame, textvariable=house_var, values=sorted(list(HOUSES.keys())), font=self.body_font, state="readonly", width=25)
        house_dropdown.pack(side="left", expand=True, fill="x")
        if self.current_assignments: # Pre-select house if possible
            first_student = student_names[1] if len(student_names) > 1 else None
            if first_student and self.current_assignments.get(first_student): house_dropdown.set(self.current_assignments.get(first_student))
            elif HOUSES: house_dropdown.set(sorted(list(HOUSES.keys()))[0])

        points_action_frame = ttk.Frame(dialog, style="TFrame"); points_action_frame.pack(pady=10, fill="x", padx=20)
        ttk.Label(points_action_frame, text="Points:", style="Body.TLabel").pack(side="left", padx=(0,5))
        points_entry = ttk.Entry(points_action_frame, font=self.body_font, width=8)
        points_entry.pack(side="left", padx=(0,10)); points_entry.insert(0, "10"); points_entry.focus()
        action_var = tk.StringVar(value="add")
        ttk.Radiobutton(points_action_frame, text="Add", variable=action_var, value="add", style="TRadiobutton").pack(side="left", padx=5)
        ttk.Radiobutton(points_action_frame, text="Deduct", variable=action_var, value="deduct", style="TRadiobutton").pack(side="left", padx=5)

        reason_frame = ttk.Frame(dialog, style="TFrame"); reason_frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(reason_frame, text="Reason:", style="Body.TLabel").pack(side="left", padx=(0,5))
        reason_entry = ttk.Entry(reason_frame, font=self.body_font, width=35)
        reason_entry.pack(side="left", expand=True, fill="x"); reason_entry.insert(0, "House/Student performance")

        def apply_points_change():
            try:
                points_val = int(points_entry.get()); reason_val = reason_entry.get() or "No reason provided"
                selected_student = student_var.get(); selected_house = house_var.get()
                if not selected_house: messagebox.showerror("Error", "Please select a target house.", parent=dialog); return
                if action_var.get() == "deduct": points_val = -points_val

                target_student_name = None
                if selected_student != "(Whole House)":
                    target_student_name = selected_student
                    if self.current_assignments.get(target_student_name) != selected_house: messagebox.showerror("Error", f"{target_student_name} is not in {selected_house}.", parent=dialog); return

                HOUSES[selected_house]["points"] = HOUSES[selected_house].get("points",0) + points_val
                history_action = f"{'Added' if points_val > 0 else 'Deducted'} {abs(points_val)} points to {selected_house}"

                if target_student_name: # Points for a specific student
                    s_data = self.student_data.get(target_student_name, self._get_default_student_data())
                    s_data["points"] = s_data.get("points", 0) + points_val
                    self.student_data[target_student_name] = s_data; history_action += f" (specifically for {target_student_name})"
                elif selected_student == "(Whole House)": # Points for all students in the house
                    for s_name, s_house in self.current_assignments.items():
                        if s_house == selected_house:
                            s_data = self.student_data.get(s_name, self._get_default_student_data())
                            s_data["points"] = s_data.get("points", 0) + points_val
                            self.student_data[s_name] = s_data
                    history_action += " (applied to all house members)"

                self.history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": history_action, "reason": reason_val, "student": target_student_name})
                self.save_progress(); self.update_display(); play_sound(SOUNDS["points"]); dialog.destroy()
            except ValueError: messagebox.showerror("Error", "Invalid points value.", parent=dialog); play_sound(SOUNDS["error"])
        ttk.Button(dialog, text="✨ Apply Changes", command=apply_points_change, style="Golden.TButton").pack(pady=15)


    def award_achievement_dialog(self):
        if not self.current_assignments: messagebox.showerror("Error", "Assign houses to students first!", parent=self.root); play_sound(SOUNDS["error"]); return
        dialog = tk.Toplevel(self.root); dialog.title("Award Special Achievement"); dialog.geometry("600x550")
        dialog.configure(bg=self.theme_colors["bg"]); dialog.resizable(False, False); dialog.grab_set(); dialog.transient(self.root)

        ttk.Label(dialog, text="Grant an Esteemed Accomplishment", style="Header.TLabel").pack(pady=10)

        student_frame = ttk.Frame(dialog, style="TFrame"); student_frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(student_frame, text="Select Student:", style="Body.TLabel").pack(side="left", padx=(0,5))
        student_var = tk.StringVar()
        student_dropdown = ttk.Combobox(student_frame, textvariable=student_var, values=sorted(list(self.student_data.keys())), font=self.body_font, state="readonly", width=30)
        student_dropdown.pack(side="left", expand=True, fill="x");
        if self.student_data: student_dropdown.current(0) # Pre-select first student

        ach_select_frame = ttk.Frame(dialog, style="TFrame"); ach_select_frame.pack(pady=10, fill="both", expand=True, padx=20)
        ttk.Label(ach_select_frame, text="Select Achievement:", style="Body.TLabel").pack(anchor="w", pady=(0,5))
        ach_scroll_content, ach_canvas, _ = create_scrollable_frame(ach_select_frame, self.theme_colors)
        ach_canvas.configure(height=200); achievement_var = tk.StringVar() # To hold selected achievement
        for ach_name, ach_data in ACHIEVEMENTS.items():
            rb_frame = ttk.Frame(ach_scroll_content, style="TFrame"); rb_frame.pack(fill="x", pady=2)
            rb = ttk.Radiobutton(rb_frame, text=f"{ach_data['icon']} {ach_name} (+{ach_data['points']} pts)", variable=achievement_var, value=ach_name, style="TRadiobutton")
            rb.pack(side="left", anchor="w")

        reason_frame = ttk.Frame(dialog, style="TFrame"); reason_frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(reason_frame, text="Reason for Award:", style="Body.TLabel").pack(side="left", padx=(0,5))
        reason_entry = ttk.Entry(reason_frame, font=self.body_font, width=35)
        reason_entry.pack(side="left", expand=True, fill="x"); reason_entry.insert(0, "Exceptional deed")

        def apply_achievement_award():
            s_name_val, ach_name_val, reason_val = student_var.get(), achievement_var.get(), reason_entry.get() or "No reason provided"
            if not s_name_val: messagebox.showerror("Error", "Please select a student.", parent=dialog); return
            if not ach_name_val: messagebox.showerror("Error", "Please select an achievement.", parent=dialog); return

            ach_data_val = ACHIEVEMENTS[ach_name_val]; s_house_val = self.current_assignments.get(s_name_val)
            if not s_house_val: messagebox.showerror("Error", f"{s_name_val} is not assigned to a house.", parent=dialog); return

            HOUSES[s_house_val]["points"] += ach_data_val["points"]
            s_data = self.student_data.get(s_name_val, self._get_default_student_data())
            s_data["points"] = s_data.get("points", 0) + ach_data_val["points"]
            if ach_name_val not in s_data.get("achievements", []): s_data.setdefault("achievements", []).append(ach_name_val)
            self.student_data[s_name_val] = s_data # Ensure update

            self.history.append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"action":f"Awarded '{ach_name_val}' to {s_name_val}","reason":reason_val,"student":s_name_val})
            self.save_progress(); self.update_display(); play_sound(SOUNDS["achievement"]); dialog.destroy()
            self.show_achievement_celebration(s_name_val, ach_name_val) # Show celebration window
        ttk.Button(dialog, text="🌟 Grant Achievement", command=apply_achievement_award, style="Golden.TButton").pack(pady=15)


    def show_achievement_celebration(self, student_name, achievement_name):
        celeb_win = tk.Toplevel(self.root); celeb_win.title("Achievement Unlocked!"); celeb_win.geometry("550x350")
        student_house = self.current_assignments.get(student_name, "")
        house_main_color = HOUSES.get(student_house, {}).get("color", self.theme_colors["accent_bg"])
        house_secondary_color = HOUSES.get(student_house, {}).get("secondary", self.theme_colors["gold_fg"])
        celeb_win.configure(bg=house_main_color); celeb_win.resizable(False, False); celeb_win.grab_set(); celeb_win.transient(self.root)
        # Center celebration window
        self.root.update_idletasks(); x = self.root.winfo_x()+(self.root.winfo_width()//2)-(celeb_win.winfo_reqwidth()//2)
        y = self.root.winfo_y()+(self.root.winfo_height()//2)-(celeb_win.winfo_reqheight()//2); celeb_win.geometry(f"+{x}+{y}")

        canvas = tk.Canvas(celeb_win, bg=house_main_color, highlightthickness=0); canvas.pack(fill="both", expand=True, padx=10, pady=10)
        ach_data = ACHIEVEMENTS[achievement_name]
        canvas.create_text(275,50,text="✨ Achievement Unlocked! ✨",font=self.thematic_title_font,fill=house_secondary_color)
        canvas.create_text(275,100,text=f"{student_name} of {student_house}",font=self.header_font,fill=get_contrasting_text_color(house_main_color))
        canvas.create_text(275,150,text=f"{ach_data['icon']} {achievement_name} {ach_data['icon']}",font=self.thematic_header_font,fill=house_secondary_color)
        canvas.create_text(275,200,text=ach_data['description'],font=self.body_font,fill=get_contrasting_text_color(house_main_color),width=480,justify="center")
        canvas.create_text(275,250,text=f"+{ach_data['points']} Points!",font=self.header_font,fill=self.theme_colors["gold_fg"])

        for _ in range(15): # Add some sparkles
            sx,sy = random.randint(50,500),random.randint(280,330)
            create_animated_sparkles(canvas,sx,sy,color=self.theme_colors["gold_fg"],size=20,count=5,duration_ms=800)
        play_sound(SOUNDS["celebration"])
        ttk.Button(celeb_win,text="Excellent!",command=celeb_win.destroy,style=f"{student_house}.TButton" if student_house else "Golden.TButton").pack(pady=15)


    def show_history_log(self):
        if not self.history: messagebox.showinfo("History Log","No historical events recorded yet.", parent=self.root); return
        hist_win = tk.Toplevel(self.root); hist_win.title("Enchanted History Log"); hist_win.geometry("800x650")
        hist_win.configure(bg=self.theme_colors["bg"]); hist_win.resizable(True,True); hist_win.grab_set(); hist_win.transient(self.root)

        ttk.Label(hist_win,text="Chronicles of Hogwarts",style="Title.TLabel").pack(pady=10)
        flt_bar = ttk.Frame(hist_win,style="TFrame",padding=(0,5)); flt_bar.pack(fill="x",padx=10)
        ttk.Label(flt_bar,text="Filter by:",style="Body.TLabel").pack(side="left",padx=(0,10))
        flt_var = tk.StringVar(value="All Events")
        flt_opts = ["All Events","Points Changes","Achievements","House Assignments","Student Edits","Random Events", "Duels"]
        flt_menu = ttk.Combobox(flt_bar,textvariable=flt_var,values=flt_opts,state="readonly",font=self.body_font,width=20)
        flt_menu.pack(side="left",padx=(0,10)); flt_menu.current(0)
        ttk.Label(flt_bar,text="Search:",style="Body.TLabel").pack(side="left",padx=(10,5))
        srch_var = tk.StringVar(); srch_entry = ttk.Entry(flt_bar,textvariable=srch_var,font=self.body_font,width=25)
        srch_entry.pack(side="left",expand=True,fill="x")

        hist_content_f,hist_canvas,_ = create_scrollable_frame(hist_win,self.theme_colors)
        hist_canvas.configure(bg=self.theme_colors["frame_bg"]) # Background for the history list area

        def populate_hist_display():
            for w in hist_content_f.winfo_children(): w.destroy() # Clear old entries
            cur_flt,s_term = flt_var.get(),srch_var.get().lower(); disp_hist = []
            for entry in reversed(self.history): # Show newest first
                act,rsn,std = entry.get("action","").lower(),entry.get("reason","").lower(),entry.get("student","")
                match_srch = (not s_term or s_term in act or s_term in rsn or (std and s_term in std.lower()))
                if not match_srch: continue

                cat_match = False
                if cur_flt=="All Events": cat_match=True
                elif cur_flt=="Points Changes" and ("points" in act or "deducted" in act): cat_match=True
                elif cur_flt=="Achievements" and "awarded" in act: cat_match=True
                elif cur_flt=="House Assignments" and ("assignment" in act or "sorting" in act or "assignments:" in act): cat_match=True
                elif cur_flt=="Student Edits" and ("student" in act and ("added" in act or "removed" in act or "updated" in act or "imported" in act or "renamed" in act)): cat_match=True
                elif cur_flt=="Random Events" and "random event" in act: cat_match=True
                elif cur_flt=="Duels" and ("duel" in act or "dueling" in act or "defeated" in act): cat_match=True # Added "defeated"
                if cat_match: disp_hist.append(entry)

            if not disp_hist: ttk.Label(hist_content_f,text="No matching history entries.",style="Body.TLabel",padding=20).pack(); return

            for entry in disp_hist:
                entry_f = ttk.Frame(hist_content_f,style="Section.TFrame",padding=8,relief="groove",borderwidth=1); entry_f.pack(fill="x",pady=4,padx=5)
                ttk.Label(entry_f,text=entry.get('date','N/A'),style="HistoryDate.TLabel").pack(anchor="w")
                act_txt = entry.get('action','Activity recorded')
                act_lbl = ttk.Label(entry_f,text=act_txt,style="HistoryAction.TLabel",wraplength=700,justify="left"); act_lbl.pack(anchor="w",pady=(2,0))
                if entry.get('student'): ttk.Label(entry_f,text=f"Student(s): {entry['student']}",style="Small.TLabel").pack(anchor="w")
                if entry.get('reason'): ttk.Label(entry_f,text=f"Details: {entry['reason']}",style="HistoryReason.TLabel").pack(anchor="w",pady=(2,0))

        flt_var.trace_add("write",lambda *a: populate_hist_display()); srch_var.trace_add("write",lambda *a: populate_hist_display())
        populate_hist_display(); ttk.Button(hist_win,text="Close",command=hist_win.destroy,style="Golden.TButton").pack(pady=10)


    def confirm_reset_points(self):
        if messagebox.askyesno("Confirm Reset","Reset ALL house and student points, HP, and MP to defaults?\nThis cannot be undone!",icon="warning",default="no", parent=self.root):
            for h_key in HOUSES: HOUSES[h_key]["points"]=0
            for s_name in self.student_data: self.student_data[s_name] = self._get_default_student_data() # Reset to defaults
            self.history.append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"action":"All house and student data (points, HP, MP) reset.","reason":"Manual reset."})
            self.save_progress(); self.update_display(); play_sound(SOUNDS["error"]); messagebox.showinfo("Reset Complete","All data reset.", parent=self.root)

    def _get_default_student_data(self): # Helper to get fresh student data structure
        return {"points":0,"achievements":[],"hp":DEFAULT_HP,"mp":DEFAULT_MP, "status_effects": {}}

    def edit_students_dialog(self):
        dialog = tk.Toplevel(self.root); dialog.title("Manage Students Roster"); dialog.geometry("700x600")
        dialog.configure(bg=self.theme_colors["bg"]); dialog.resizable(False, False); dialog.grab_set(); dialog.transient(self.root)
        self.current_edit_dialog_refresh_func = lambda: populate_student_list_for_edit(dialog) # For refreshing list in dialog

        ttk.Label(dialog, text="Student Roster Management", style="Header.TLabel").pack(pady=10)
        top_actions_frame = ttk.Frame(dialog, style="TFrame", padding=(0,10)); top_actions_frame.pack(fill="x", padx=20)
        self.new_student_entry_for_dialog = ttk.Entry(top_actions_frame, font=self.body_font, width=25)
        self.new_student_entry_for_dialog.pack(side="left", padx=(0,5), expand=True, fill="x"); self.new_student_entry_for_dialog.insert(0, "New Student Name")
        ttk.Button(top_actions_frame, text="➕ Add Student", command=lambda d=dialog: self.add_new_student_from_dialog(d), style="Golden.TButton").pack(side="left", padx=(0,10))
        ttk.Button(top_actions_frame, text="📥 Import", command=lambda d=dialog: self.import_students_list(d), style="TButton").pack(side="left", padx=5)
        ttk.Button(top_actions_frame, text="📤 Export", command=lambda d=dialog: self.export_students_list(d), style="TButton").pack(side="left", padx=5)

        list_frame_outer = ttk.Frame(dialog, style="Section.TFrame", padding=5); list_frame_outer.pack(fill="both", expand=True, padx=20, pady=10)
        student_list_content, student_list_canvas, _ = create_scrollable_frame(list_frame_outer, self.theme_colors)
        student_list_canvas.configure(bg=self.theme_colors["frame_bg"]); student_entries_in_dialog = {} # To store Entry widgets

        def populate_student_list_for_edit(current_dialog):
            if not current_dialog.winfo_exists(): return
            for widget in student_list_content.winfo_children(): widget.destroy()
            student_entries_in_dialog.clear()
            if not self.student_data: ttk.Label(student_list_content, text="No students on record.", style="Body.TLabel", padding=15).pack(); return

            for student_name_key in sorted(self.student_data.keys()):
                item_frame = ttk.Frame(student_list_content, style="Section.TFrame", padding=5); item_frame.pack(fill="x", pady=3)
                name_entry = ttk.Entry(item_frame, font=self.body_font); name_entry.insert(0, student_name_key)
                name_entry.pack(side="left", expand=True, fill="x", padx=(0,5)); student_entries_in_dialog[student_name_key] = name_entry
                remove_button = ttk.Button(item_frame, text="🗑️ Remove", style="Destructive.TButton", width=10)
                remove_button.configure(command=lambda s=student_name_key, d=current_dialog: self.remove_student_from_dialog(s, lambda: populate_student_list_for_edit(d), d))
                remove_button.pack(side="left", padx=2)
        populate_student_list_for_edit(dialog)

        save_and_close_button = ttk.Button(dialog, text="Done & Save Changes", style="Golden.TButton")
        save_and_close_button.configure(command=lambda d=dialog, entries=student_entries_in_dialog: self.save_all_student_name_changes_from_dialog(lambda: populate_student_list_for_edit(d), entries, d))
        save_and_close_button.pack(pady=10)


    def save_all_student_name_changes_from_dialog(self, refresh_callback, entry_widgets_map, dialog_window):
        changes_made = False; original_names_in_dialog = list(entry_widgets_map.keys()) # Names at dialog open
        for old_name in original_names_in_dialog:
            entry_widget = entry_widgets_map.get(old_name)
            if not entry_widget or not entry_widget.winfo_exists(): continue # Widget gone
            new_name = entry_widget.get().strip()
            if not new_name: # Name cannot be empty
                messagebox.showwarning("Input Error", f"Student name for '{old_name}' cannot be empty. Reverted.", parent=dialog_window)
                entry_widget.delete(0, tk.END); entry_widget.insert(0, old_name); continue
            if new_name != old_name: # If name actually changed
                if new_name in self.student_data and new_name not in original_names_in_dialog: # Check if new name conflicts with existing non-edited student
                    messagebox.showerror("Error", f"Student '{new_name}' already exists. Cannot rename '{old_name}'.", parent=dialog_window)
                    entry_widget.delete(0, tk.END); entry_widget.insert(0, old_name); continue
                self._rename_student_data(old_name, new_name); changes_made = True
        if changes_made: self.save_progress(); self.update_display(); play_sound(SOUNDS["points"])
        if dialog_window.winfo_exists(): refresh_callback() # Refresh list in dialog
        # Dialog is closed by the caller or another button, this just saves.
        # Let's make it close the dialog after saving.
        if dialog_window.winfo_exists(): dialog_window.destroy()


    def _rename_student_data(self, old_name, new_name): # Internal helper for renaming
        if old_name == new_name: return
        # Rename avatar if exists
        old_avatar_path, new_avatar_path = get_avatar_path(old_name), get_avatar_path(new_name)
        if os.path.exists(old_avatar_path):
            try: os.rename(old_avatar_path, new_avatar_path)
            except OSError as e: print(f"Could not rename avatar for {old_name}: {e}")

        if old_name in self.student_data: self.student_data[new_name] = self.student_data.pop(old_name)
        if old_name in self.current_assignments: self.current_assignments[new_name] = self.current_assignments.pop(old_name)
        # Update history log (simple replacement, might not be perfect for all cases)
        for entry in self.history:
            if entry.get("student") == old_name: entry["student"] = new_name
            if "action" in entry and old_name in entry["action"]: entry["action"] = entry["action"].replace(old_name, new_name)
        self.history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Student '{old_name}' renamed to '{new_name}'.", "reason": "Manual edit via roster."})


    def add_new_student_from_dialog(self, dialog_instance):
        if not hasattr(self, 'new_student_entry_for_dialog') or not self.new_student_entry_for_dialog.winfo_exists(): return
        new_name = self.new_student_entry_for_dialog.get().strip()
        if not new_name or new_name == "New Student Name": messagebox.showwarning("Input Error", "Please enter a valid student name.", parent=dialog_instance); return
        if new_name in self.student_data: messagebox.showerror("Error", f"Student '{new_name}' already exists.", parent=dialog_instance); return

        self.student_data[new_name] = self._get_default_student_data()
        self.new_student_entry_for_dialog.delete(0, tk.END); self.new_student_entry_for_dialog.insert(0, "New Student Name") # Reset entry
        self.history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added new student: {new_name}", "reason": "Manual addition via roster."})
        self.save_progress(); self.update_display(); play_sound(SOUNDS["points"])
        if hasattr(self, 'current_edit_dialog_refresh_func') and callable(self.current_edit_dialog_refresh_func): self.current_edit_dialog_refresh_func()


    def remove_student_from_dialog(self, student_name, refresh_callback, dialog_instance):
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove {student_name}?", icon="warning", default="no", parent=dialog_instance):
            if student_name in self.student_data: del self.student_data[student_name]
            if student_name in self.current_assignments: del self.current_assignments[student_name]
            avatar_p = get_avatar_path(student_name) # Remove avatar too
            if os.path.exists(avatar_p):
                try: os.remove(avatar_p)
                except OSError: print(f"Could not remove avatar for {student_name}")

            self.history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Removed student: {student_name}", "reason": "Manual removal."})
            self.save_progress(); self.update_display(); play_sound(SOUNDS["error"])
            if dialog_instance.winfo_exists(): refresh_callback() # Refresh list in dialog


    def import_students_list(self, dialog_instance):
        file_path = filedialog.askopenfilename(parent=dialog_instance, title="Import Roster", filetypes=[("Text","*.txt"),("JSON","*.json"),("All","*.*")])
        if not file_path: return; added_count = 0
        try:
            imp_students = []
            if file_path.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
                if isinstance(data,list): imp_students = data # Simple list of names
                elif isinstance(data,dict) and "students" in data and isinstance(data["students"],list): imp_students = data["students"] # From our export format
                else: raise ValueError("JSON not recognized.")
            else: # Assume text file, one name per line
                with open(file_path, "r", encoding="utf-8") as f: imp_students = [ln.strip() for ln in f if ln.strip()]

            for name in imp_students:
                if name not in self.student_data: self.student_data[name] = self._get_default_student_data(); added_count += 1
            if added_count > 0 or imp_students: # If any students processed or new ones added
                self.history.append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"action":f"Imported {len(imp_students)} students ({added_count} new).","reason":f"File: {os.path.basename(file_path)}"})
                self.save_progress(); self.update_display(); play_sound(SOUNDS["points"])
                messagebox.showinfo("Import OK", f"{len(imp_students)} processed. {added_count} new students added.", parent=dialog_instance)
                if hasattr(self,'current_edit_dialog_refresh_func') and callable(self.current_edit_dialog_refresh_func): self.current_edit_dialog_refresh_func()
            else: messagebox.showinfo("Import Info", "No new students found in the selected file.", parent=dialog_instance)
        except Exception as e: messagebox.showerror("Import Error", f"Failed: {e}", parent=dialog_instance); play_sound(SOUNDS["error"])


    def export_students_list(self, dialog_instance):
        file_path = filedialog.asksaveasfilename(parent=dialog_instance, title="Export Roster", defaultextension=".json", filetypes=[("JSON","*.json"),("Text","*.txt")])
        if not file_path: return
        try:
            exp_students = sorted(list(self.student_data.keys()))
            if file_path.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f: json.dump({"students":exp_students,"export_date":datetime.now().isoformat()},f,indent=2)
            else: # Text file
                with open(file_path, "w", encoding="utf-8") as f:
                    for name in exp_students: f.write(f"{name}\n")
            messagebox.showinfo("Export OK", f"Roster exported to {os.path.basename(file_path)}.", parent=dialog_instance); play_sound(SOUNDS["points"])
        except Exception as e: messagebox.showerror("Export Error", f"Failed: {e}", parent=dialog_instance); play_sound(SOUNDS["error"])


    def assign_houses_ceremony(self):
        if not self.student_data: messagebox.showerror("Error", "No students to sort!", parent=self.root); play_sound(SOUNDS["error"]); return
        ceremony_win = tk.Toplevel(self.root); ceremony_win.title("The Sorting Ceremony"); ceremony_win.geometry("600x450")
        ceremony_win.configure(bg=self.theme_colors["accent_bg"]); ceremony_win.resizable(False, False); ceremony_win.grab_set(); ceremony_win.transient(self.root)
        # Center window
        self.root.update_idletasks(); x,y = self.root.winfo_x()+(self.root.winfo_width()//2)-(ceremony_win.winfo_reqwidth()//2), self.root.winfo_y()+(self.root.winfo_height()//2)-(ceremony_win.winfo_reqheight()//2)
        ceremony_win.geometry(f"+{x}+{y}"); canvas = tk.Canvas(ceremony_win, bg=self.theme_colors["accent_bg"], highlightthickness=0); canvas.pack(fill="both", expand=True)

        hat_txt = canvas.create_text(300,120,text="🎩",font=("Arial",120),fill=self.theme_colors["gold_fg"])
        status_txt = canvas.create_text(300,250,text="The Sorting Hat considers...",font=self.header_font,fill=self.theme_colors["fg"])
        play_sound(SOUNDS["sorting"]); students_to_sort = list(self.student_data.keys()); random.shuffle(students_to_sort)
        shuffled_houses = list(HOUSES.keys()); random.shuffle(shuffled_houses); new_assignments = {}

        def sort_next_student(idx=0):
            if idx < len(students_to_sort):
                std = students_to_sort[idx]; assigned_h = shuffled_houses[idx % len(shuffled_houses)]; new_assignments[std] = assigned_h
                canvas.itemconfig(status_txt, text=f"{std} is thinking...")
                for i in range(5): canvas.move(hat_txt,0,-5 if i%2==0 else 5); ceremony_win.update_idletasks(); ceremony_win.after(80) # Hat "thinking" animation
                canvas.itemconfig(status_txt, text=f"{std} is... {HOUSES[assigned_h]['animal']} {assigned_h}!", fill=HOUSES[assigned_h]["color"])
                play_sound([random.randint(300,700)],150); ceremony_win.after(1500, lambda: sort_next_student(idx+1))
            else: finish_ceremony()

        def finish_ceremony():
            self.current_assignments = new_assignments; assign_details = "Sorting Ceremony complete. Assignments:\n"
            for std,h in self.current_assignments.items(): assign_details += f"- {std}: {HOUSES[h]['animal']} {h}\n"
            self.history.append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"action":assign_details.strip()})
            self.save_progress(); self.update_display(); play_sound(SOUNDS["celebration"]); canvas.delete(hat_txt)
            canvas.itemconfig(status_txt,text="The Sorting is Done!",fill=self.theme_colors["gold_fg"],font=self.thematic_title_font)
            canvas.create_text(300,320,text="Close this window to see results.",font=self.body_font,fill=self.theme_colors["fg"])
            ttk.Button(ceremony_win,text="Done!",command=ceremony_win.destroy,style="Golden.TButton").place(relx=0.5,rely=0.85,anchor="center")
        ceremony_win.after(1000, lambda: sort_next_student(0)) # Start sorting after a delay


    def show_house_details(self, house_to_show=None):
        if not house_to_show: # If no house specified, show selection dialog
            sel_win = tk.Toplevel(self.root); sel_win.title("Select House"); sel_win.geometry("350x300")
            sel_win.configure(bg=self.theme_colors["bg"]); sel_win.resizable(False,False); sel_win.grab_set(); sel_win.transient(self.root)
            ttk.Label(sel_win,text="View Details For:",style="Header.TLabel").pack(pady=15)
            for h_name in HOUSES: ttk.Button(sel_win,text=f"{HOUSES[h_name]['animal']} {h_name}",command=lambda name=h_name:(sel_win.destroy(),self.show_house_details(name)),style=f"{h_name}.TButton",width=20).pack(pady=5,padx=20,fill="x")
            return

        det_win = tk.Toplevel(self.root); det_win.title(f"{house_to_show} House Details"); det_win.geometry("600x500")
        det_win.configure(bg=self.theme_colors["bg"]); det_win.resizable(True,True); det_win.grab_set(); det_win.transient(self.root)
        h_data = HOUSES[house_to_show]; main_det_f,det_canvas,_ = create_scrollable_frame(det_win,self.theme_colors)
        det_canvas.configure(bg=self.theme_colors["frame_bg"]) # Content area background

        hdr_f = ttk.Frame(main_det_f,style="Section.TFrame",padding=15); hdr_f.pack(fill="x",pady=10,padx=10)
        if house_to_show in self.house_crests_photoimages:
            cr_lbl = tk.Label(hdr_f,image=self.house_crests_photoimages[house_to_show],bg=self.theme_colors["frame_bg"]); cr_lbl.pack(side="left",padx=(0,20))
        else: tk.Label(hdr_f,text=h_data["animal"],font=("Arial",48),fg=h_data["color"],bg=self.theme_colors["frame_bg"]).pack(side="left",padx=(0,20))

        info_f = ttk.Frame(hdr_f,style="Section.TFrame"); info_f.pack(side="left",fill="x",expand=True)
        ttk.Label(info_f,text=house_to_show,style="Title.TLabel",foreground=h_data["color"]).pack(anchor="w")
        ttk.Label(info_f,text=f"Total Points: {h_data['points']}",style="Header.TLabel",foreground=self.theme_colors["gold_fg"]).pack(anchor="w",pady=(0,5))
        ttk.Label(info_f,text=f"Core Traits: {h_data['traits']}",style="Body.TLabel",wraplength=350).pack(anchor="w")

        mem_f = ttk.Frame(main_det_f,style="Section.TFrame",padding=10); mem_f.pack(fill="x",pady=10,padx=10)
        ttk.Label(mem_f,text=f"{h_data['animal']} House Members",style="Header.TLabel").pack(pady=(0,10))
        h_mems = [s for s,h_asgn in self.current_assignments.items() if h_asgn==house_to_show]
        if not h_mems: ttk.Label(mem_f,text="No assigned members.",style="Body.TLabel",padding=10).pack()
        else:
            for m_name in sorted(h_mems):
                m_item_f = ttk.Frame(mem_f,style="Section.TFrame",padding=5); m_item_f.pack(fill="x",pady=2)
                ttk.Label(m_item_f,text=m_name,style="Body.TLabel").pack(side="left",padx=(0,10))
                ttk.Label(m_item_f,text=f"({self.student_data.get(m_name,{}).get('points',0)} pts)",style="Small.TLabel",foreground=self.theme_colors["gold_fg"]).pack(side="left")
        ttk.Button(main_det_f,text="Close",command=det_win.destroy,style="Golden.TButton").pack(pady=15)


    def trigger_random_event(self):
        event_list = [
            ("Quidditch Practice Pays Off!", "Extra training shows on the pitch!", 10, 5),("Minor Potion Spill", "A small accident in Potions class.", -5, 0),
            ("Helpful Library Research", "A student found a crucial piece of information.", 10, 0),("Successful Group Study", "Students from two houses collaborated well.", 5, 5),
            ("Impeccable Uniforms Noted", "Ministry officials were impressed by student presentation.", 5, 0),("Friendly Care of Magical Creatures", "A student showed kindness to a Bowtruckle.", 5, 0),
            ("Lost Item Returned", "A student returned a valuable lost item.", 10, 0),("Messy Common Room", "Points deducted for an untidy common room.", -5, 0),
            ("Perfectly Executed Charm", "A student performed a charm flawlessly in class.", 10, 0),("Herbology Harvest Success", "Bountiful harvest from the greenhouses!", 5, 5),
            ("Filch in a Good Mood!", "Surprisingly, Filch let a minor infraction slide.", 3, 0),("Peeves Causes Minor Mayhem", "Peeves swapped potion ingredients.", -3, -3),
            ("Excellent Transfiguration", "A student perfectly transfigured a teacup into a tortoise.", 8, 0),("Forgotten Homework", "A student forgot their homework, losing house points.", -5, 0),
            ("Successful Owl Post Delivery", "Important news arrives, boosting morale.", 2, 2),("Charity Bake Sale Success", "Raised a good sum for St. Mungo's!", 7, 7),
            ("Solution to a Riddle", "A clever student solved a Sphinx's riddle.", 8, 0),("Late Night Study Session", "Caught studying after hours (minor deduction).", -2, 0),
            ("Brave Act in the Forbidden Forest", "A student showed courage facing a minor forest creature.", 10, 0),("Assisting a Professor", "A student offered valuable help to a professor.", 6, 0)]
        event_name, event_desc, p1_change, p2_change = random.choice(event_list)
        if len(HOUSES)<2: messagebox.showinfo("Random Event","Not enough houses for a two-house event!",parent=self.root); return
        h1_name,h2_name = random.sample(list(HOUSES.keys()),2) # Pick two distinct houses

        if p1_change!=0: HOUSES[h1_name]["points"] += p1_change
        if p2_change!=0: HOUSES[h2_name]["points"] += p2_change
        hist_act = f"Random Event: {event_name} - {h1_name}: {p1_change:+} pts"
        if p2_change!=0: hist_act += f", {h2_name}: {p2_change:+} pts."
        else: hist_act += "."
        self.history.append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"action":hist_act,"reason":event_desc})
        self.save_progress(); self.update_display()

        evt_win = tk.Toplevel(self.root); evt_win.title("⚡ A Magical Event Occurred! ⚡"); evt_win.geometry("500x350")
        evt_win.configure(bg=self.theme_colors["accent_bg"]); evt_win.resizable(False,False); evt_win.grab_set(); evt_win.transient(self.root)
        self.root.update_idletasks(); x,y=self.root.winfo_x()+(self.root.winfo_width()//2)-(evt_win.winfo_reqwidth()//2), self.root.winfo_y()+(self.root.winfo_height()//2)-(evt_win.winfo_reqheight()//2)
        evt_win.geometry(f"+{x}+{y}"); canvas = tk.Canvas(evt_win,bg=self.theme_colors["accent_bg"],highlightthickness=0); canvas.pack(fill="both",expand=True,padx=10,pady=10)
        canvas.create_text(250,50,text=event_name,font=self.thematic_header_font,fill=self.theme_colors["gold_fg"],justify="center",width=480)
        canvas.create_text(250,110,text=event_desc,font=self.body_font,fill=self.theme_colors["fg"],justify="center",width=480)
        y_pos = 170
        if p1_change!=0: canvas.create_text(250,y_pos,text=f"{HOUSES[h1_name]['animal']} {h1_name}: {p1_change:+} points",font=self.header_font,fill=HOUSES[h1_name]["color"]); y_pos+=40
        if p2_change!=0: canvas.create_text(250,y_pos,text=f"{HOUSES[h2_name]['animal']} {h2_name}: {p2_change:+} points",font=self.header_font,fill=HOUSES[h2_name]["color"])
        for _ in range(10):
            sx,sy = random.randint(30,470),random.randint(250,300)
            create_animated_sparkles(canvas,sx,sy,color=self.theme_colors["gold_fg"],size=15,count=4,duration_ms=700)
        play_sound(SOUNDS["celebration"] if p1_change>0 or p2_change>0 else SOUNDS["points"])
        ttk.Button(evt_win,text="Noted!",command=evt_win.destroy,style="Golden.TButton").pack(pady=20)


    def cast_spell(self): # Visual effect on main screen
        if not hasattr(self,'main_canvas_scrollable_area') or not self.main_canvas_scrollable_area.winfo_exists(): messagebox.showinfo("Spell Failed","Canvas not ready.",parent=self.root); return
        spell_name = random.choice(SPELLS); canvas_w = self.main_canvas_scrollable_area.winfo_width()
        if canvas_w<=1: canvas_w=800 # Default if not drawn
        start_x,start_y = random.randint(int(canvas_w*0.2),int(canvas_w*0.8)), self.main_canvas_scrollable_area.winfo_height()-30
        if start_y<=1: start_y=500 # Default if not drawn
        spell_id = self.main_canvas_scrollable_area.create_text(start_x,start_y,text=f"✨ {spell_name} ✨",font=self.thematic_header_font,fill=self.theme_colors["gold_fg"],anchor="s")
        self.spell_effects.append((spell_id,60,random.uniform(-0.5,0.5),-3)); play_sound(SOUNDS["spell_cast_ui"])
        tmp_lbl = ttk.Label(self.root,text=f"Cast: {spell_name}!",style="Gold.TLabel",background=self.theme_colors["accent_bg"],padding=5)
        tmp_lbl.place(relx=0.5,rely=0.95,anchor="center"); self.root.after(2500,tmp_lbl.destroy)


    def show_help(self):
        help_win = tk.Toplevel(self.root); help_win.title("Help & About"); help_win.geometry("650x550")
        help_win.configure(bg=self.theme_colors["bg"]); help_win.resizable(False,False); help_win.grab_set(); help_win.transient(self.root)
        scroll_content,help_canvas,_ = create_scrollable_frame(help_win,self.theme_colors)
        help_canvas.configure(bg=self.theme_colors["frame_bg"]) # Background for help content

        ttk.Label(scroll_content,text=f"Hogwarts House Cup Tracker - {VERSION}",style="Title.TLabel").pack(pady=15)
        txt_content = [
            ("Welcome, Headmaster!","Header.TLabel"),("This enchanted ledger helps manage the House Cup...","Body.TLabel"),("Key Features:","Header.TLabel"),
            ("- Dynamic House Point Tracking\n- Student Management (Points, HP/MP, Avatars, History)\n- Achievement System\n- Sorting Hat Ceremony\n- Dueling Club Minigame (with Potions & HP/MP Restore!)\n- Detailed History Log\n- Import/Export Students\n- Random Magical Events\n- Spell Casting Effects\n- Looping Theme Song (Optional)\n- Immersive Dark Theme","Body.TLabel"),
            ("Support:","Header.TLabel"),("Contact support@hogwartsdev.wiz or visit github.com/HogwartsTracker.","Body.TLabel"),("Save progress regularly.","Small.TLabel")]
        for txt,st_name in txt_content:
            if st_name=="Body.TLabel": ttk.Label(scroll_content,text=txt,style=st_name,wraplength=580,justify="left",padding=(0,5)).pack(anchor="w",padx=20)
            else: ttk.Label(scroll_content,text=txt,style=st_name,padding=(0,5)).pack(anchor="w",padx=20,pady=(5 if "Header" in st_name else 0,0))

        repo_f = ttk.Frame(scroll_content,style="Section.TFrame"); repo_f.pack(anchor="w",padx=20,pady=5)
        ttk.Label(repo_f,text="Visit Repository:",style="Body.TLabel").pack(side="left")
        repo_link = ttk.Label(repo_f,text="github.com/HogwartsTracker",style="Body.TLabel",foreground="blue",cursor="hand2")
        repo_link.pack(side="left",padx=5); repo_link.bind("<Button-1>",lambda e:webbrowser.open("https://github.com/HogwartsTracker"))
        ttk.Button(scroll_content,text="Close",command=help_win.destroy,style="Golden.TButton").pack(pady=20)


    def save_progress(self):
        data_to_save = {"version":VERSION,"houses_points":{h:d["points"] for h,d in HOUSES.items()},"student_data":self.student_data,"history_log":self.history,"current_assignments":self.current_assignments}
        try:
            with open(SAVE_FILE,"w",encoding="utf-8") as f: json.dump(data_to_save,f,indent=2)
        except IOError as e: messagebox.showerror("Save Error",f"Failed to save: {e}",parent=self.root); play_sound(SOUNDS["error"])


    def load_progress(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE,"r",encoding="utf-8") as f: loaded_data = json.load(f)
                loaded_hp = loaded_data.get("houses_points",{})
                for h,p in loaded_hp.items():
                    if h in HOUSES: HOUSES[h]["points"]=p

                # Migration from old student_points/student_achievements structure if present
                old_sp = loaded_data.get("student_points")
                if old_sp is not None: # Old structure detected
                    self.student_data = {}
                    old_sa = loaded_data.get("student_achievements",{})
                    for name,pts in old_sp.items(): self.student_data[name]={"points":pts,"achievements":old_sa.get(name,[]),"hp":DEFAULT_HP,"mp":DEFAULT_MP, "status_effects": {}}
                    print("Migrated old student data to new student_data structure.")
                else: # Use new student_data structure
                    self.student_data = loaded_data.get("student_data",{name:self._get_default_student_data() for name in DEFAULT_STUDENTS}) # Fallback if not found

                # Ensure all students have HP, MP, and status_effects fields
                for name in list(self.student_data.keys()): # Iterate over a copy of keys for safe modification
                    s_dat = self.student_data.get(name)
                    if not s_dat: # If a student name was somehow None or entry was missing
                        self.student_data[name] = self._get_default_student_data()
                        s_dat = self.student_data[name]
                    if "hp" not in s_dat: s_dat["hp"] = DEFAULT_HP
                    if "mp" not in s_dat: s_dat["mp"] = DEFAULT_MP
                    if "status_effects" not in s_dat: s_dat["status_effects"] = {}

                self.history = loaded_data.get("history_log",[])
                self.current_assignments = loaded_data.get("current_assignments",{})
        except (FileNotFoundError,json.JSONDecodeError) as e:
            print(f"Save file issue: {e}. Defaults used.")
            self.student_data = {name:self._get_default_student_data() for name in DEFAULT_STUDENTS} # Default students if no save
        except Exception as e: print(f"Unexpected load error: {e}")


# ==== DUELING CLUB CLASSES ====
class DuelistState:
    def __init__(self, name, house, initial_hp, initial_mp, spell_details_ref, potions_config_ref):
        self.name = name
        self.house = house
        self.initial_hp = initial_hp # Store initial max for reset
        self.initial_mp = initial_mp
        self.max_hp = initial_hp # Current max_hp for the duel
        self.max_mp = initial_mp # Current max_mp for the duel
        self.spell_details = spell_details_ref
        self.potions_config_ref = potions_config_ref
        self.reset_for_new_duel() # Initialize HP, MP, status, potions

    def reset_for_new_duel(self):
        self.hp = self.initial_hp
        self.mp = self.initial_mp
        self.status_effects = {} # e.g., {"boils": {"duration": 2}, "pain_dot": {"duration": 3, "dmg": 5}}
        self.shield_active = None # e.g., {"name": "Protego", "strength": 20, "duration": 1}
        self.selected_spell = None # Spell chosen for the current round by this duelist
        self.potions_available = {name: data["uses_per_duel"] for name, data in self.potions_config_ref.items()}


    def apply_damage(self, amount, incoming_spell_type="unknown"):
        actual_damage_taken = amount
        log_msg_parts = []

        if self.shield_active and self.shield_active["strength"] > 0:
            # Sectumsempra might ignore or partially ignore shields
            if incoming_spell_type == "offensive_dark" and self.shield_active["name"] != "Expecto Patronum":
                blocked = min(self.shield_active["strength"], amount // 2) # Dark magic cuts through normal shields better
                log_msg_parts.append(f"{self.name}'s {self.shield_active['name']} struggles against dark magic...")
            else:
                blocked = min(self.shield_active["strength"], amount)

            self.shield_active["strength"] -= blocked
            actual_damage_taken -= blocked
            log_msg_parts.append(f"{self.name}'s {self.shield_active['name']} blocks {blocked} damage!")

            if self.shield_active["strength"] <= 0:
                log_msg_parts.append(f"{self.name}'s {self.shield_active['name']} broke!")
                self.shield_active = None
                play_sound(SOUNDS.get("shield_break", [300,200]))
            else:
                play_sound(SOUNDS.get("duel_block", [400,400]))

        self.hp = max(0, self.hp - actual_damage_taken)
        return actual_damage_taken, " ".join(log_msg_parts)


    def apply_heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def consume_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def add_status_effect(self, effect_name, duration, details=None):
        self.status_effects[effect_name] = {"duration": duration}
        if details: self.status_effects[effect_name].update(details)
        play_sound(SOUNDS.get("status_inflict", [400,300]))

    def has_status(self, effect_name):
        return effect_name in self.status_effects and self.status_effects[effect_name]["duration"] > 0

    def tick_status_effects(self): # Called at the start of each duelist's turn or round phase
        log_entries = []
        if self.has_status("pain_dot"):
            dot_dmg = self.status_effects["pain_dot"].get("dmg", 5)
            actual_dmg, shield_log = self.apply_damage(dot_dmg, "status_effect_dot") # Apply to shield first
            if actual_dmg > 0: log_entries.append(f"{self.name} takes {actual_dmg} damage from persistent pain! {shield_log}")
            if shield_log and actual_dmg <=0 : log_entries.append(shield_log) # if only shield log matters
            play_sound(SOUNDS.get("duel_hit",[600,400]))
        if self.has_status("slug_vomit"):
            slug_dmg = 3 # Small constant damage
            actual_dmg, shield_log = self.apply_damage(slug_dmg, "status_effect_dot")
            if actual_dmg > 0: log_entries.append(f"{self.name} is ill from slug-vomiting, taking {actual_dmg} damage! {shield_log}")
            if shield_log and actual_dmg <=0 : log_entries.append(shield_log)
            play_sound(SOUNDS.get("status_inflict",[300,250]))


        for effect in list(self.status_effects.keys()): # Iterate over keys copy for safe deletion
            self.status_effects[effect]["duration"] -= 1
            if self.status_effects[effect]["duration"] <= 0:
                log_entries.append(f"{self.name} is no longer affected by {effect.replace('_',' ')}.")
                del self.status_effects[effect]
                play_sound(SOUNDS.get("status_cure", [500,600]))
        # Shield duration tick
        if self.shield_active:
            self.shield_active["duration"] -=1
            if self.shield_active["duration"] <= 0:
                log_entries.append(f"{self.name}'s {self.shield_active['name']} fades.")
                self.shield_active = None
        return log_entries

    def can_cast_spell(self, spell_name):
        spell_info = self.spell_details.get(spell_name)
        if not spell_info: return False
        if self.has_status("silence") or self.has_status("tongue_tie") or self.has_status("tongue_lock"):
            return False # Cannot cast if silenced or tongue-tied/locked
        return self.mp >= spell_info.get("mp", 0)

    def choose_random_spell(self):
        """Chooses a random spell the duelist can cast."""
        eligible_spells = [s_name for s_name, s_info in self.spell_details.items()
                           if self.can_cast_spell(s_name) and s_info.get("type") != "utility_flavor"]
        if not eligible_spells:
            return None # Cannot cast anything
        return random.choice(eligible_spells)


    def activate_shield(self, spell_name):
        spell_info = self.spell_details.get(spell_name)
        if spell_info and spell_info["type"] in ["shield", "shield_special", "shield_area"]:
            self.shield_active = {"name": spell_name, "strength": spell_info["strength"], "duration": spell_info.get("duration", 1)}
            return f"{self.name} casts {spell_name}!"
        return ""

class DuelingClubWindow(tk.Toplevel):
    def __init__(self, parent, app_ref, theme_colors, student_data, spell_details, potions_config, spell_interactions, sounds_ref): # Added potions_config
        super().__init__(parent)
        self.app_ref = app_ref
        self.theme_colors = theme_colors
        self.all_student_data_ref = student_data # This is a reference to app_ref.student_data
        self.spell_details = spell_details
        self.potions_config = potions_config # Store potion configurations
        self.spell_interactions = spell_interactions
        self.sounds = sounds_ref

        self.title("⚔️ Hogwarts Dueling Club - Simultaneous Spellcraft ⚔️")
        self.geometry("1000x800") # Increased height for potion buttons
        self.configure(bg=self.theme_colors["bg"])
        self.resizable(True, True)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close_duel_window)

        self.duelist1_state = None
        self.duelist2_state = None
        self.round_count = 0
        self.duel_log_texts = [] # For storing log strings if needed beyond display
        self.game_over = False

        self._setup_ui()

    def _on_close_duel_window(self):
        if not self.game_over: # If duel is active
            if messagebox.askyesno("Flee Duel?", "The duel is not over. Are you sure you want to flee? Stats will not be restored.", parent=self):
                self.app_ref.history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "action": "Duel ended: Window closed prematurely by user.",
                    "reason": f"Duel between {self.duelist1_state.name if self.duelist1_state else 'P1'} and {self.duelist2_state.name if self.duelist2_state else 'P2'}."})
                self.app_ref.save_progress() # Save history
                self.destroy()
                self.app_ref.dueling_club_window = None # Clear reference in main app
            else: return # Don't close
        else: # Duel is over, safe to close
            self.destroy()
            self.app_ref.dueling_club_window = None

    def _setup_ui(self):
        main_duel_frame = ttk.Frame(self, style="TFrame", padding=10)
        main_duel_frame.pack(fill="both", expand=True)

        # Top: Duelist Selection
        selection_frame = ttk.Frame(main_duel_frame, style="Section.TFrame", padding=10)
        selection_frame.pack(fill="x", pady=(0,10))
        student_names = sorted(list(self.all_student_data_ref.keys()))
        self.duelist1_var = tk.StringVar(); self.duelist2_var = tk.StringVar()
        ttk.Label(selection_frame, text="Duelist 1:", style="Body.TLabel", background=self.theme_colors["frame_bg"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.duelist1_combo = ttk.Combobox(selection_frame, textvariable=self.duelist1_var, values=student_names, state="readonly", width=20, font=self.app_ref.body_font)
        self.duelist1_combo.grid(row=0, column=1, padx=5, pady=5)
        if student_names: self.duelist1_combo.current(0)
        ttk.Label(selection_frame, text="VS", style="Header.TLabel", background=self.theme_colors["frame_bg"]).grid(row=0, column=2, padx=10, pady=5)
        ttk.Label(selection_frame, text="Duelist 2:", style="Body.TLabel", background=self.theme_colors["frame_bg"]).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.duelist2_combo = ttk.Combobox(selection_frame, textvariable=self.duelist2_var, values=student_names, state="readonly", width=20, font=self.app_ref.body_font)
        self.duelist2_combo.grid(row=0, column=4, padx=5, pady=5)
        if len(student_names) > 1: self.duelist2_combo.current(1)
        elif student_names: self.duelist2_combo.current(0)
        self.start_duel_button = ttk.Button(selection_frame, text="📜 Start Duel!", command=self._initialize_duel, style="Golden.TButton")
        self.start_duel_button.grid(row=0, column=5, padx=10, pady=5)

        # Middle: Arena (Duelist Panels and Log)
        self.arena_frame = ttk.Frame(main_duel_frame, style="TFrame")
        self.arena_frame.pack(fill="both", expand=True, pady=10)
        self.arena_frame.columnconfigure(0, weight=2); self.arena_frame.columnconfigure(1, weight=1); self.arena_frame.columnconfigure(2, weight=2)
        self.arena_frame.rowconfigure(0, weight=1) # Panels and log share the same row

        self.p1_panel = self._create_duelist_panel_ui_elements(self.arena_frame, 1)
        self.p1_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5); self.p1_panel.grid_remove() # Initially hidden

        log_outer_frame = ttk.Frame(self.arena_frame, style="Section.TFrame", padding=5)
        log_outer_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ttk.Label(log_outer_frame, text="📜 Duel Log 📜", style="Header.TLabel", background=self.theme_colors["frame_bg"]).pack(pady=(0,5))
        log_content_frame, log_canvas, _ = create_scrollable_frame(log_outer_frame, self.theme_colors)
        log_canvas.configure(bg=self.theme_colors["entry_bg"], height=300) # Set a fixed height or make it expand
        self.duel_log_display_frame = log_content_frame # This is the frame where log entries are packed
        self.duel_log_display_frame.configure(style="ScrollableContent.TFrame", padding=5) # Style the inner frame

        self.p2_panel = self._create_duelist_panel_ui_elements(self.arena_frame, 2)
        self.p2_panel.grid(row=0, column=2, sticky="nsew", padx=5, pady=5); self.p2_panel.grid_remove() # Initially hidden

        # Bottom: Round Actions
        self.round_action_frame = ttk.Frame(main_duel_frame, style="Section.TFrame", padding=10)
        self.round_indicator_label = ttk.Label(self.round_action_frame, text="Round: 0", style="Header.TLabel", background=self.theme_colors["frame_bg"])
        self.round_indicator_label.pack(side="left", padx=10)
        self.next_round_button = ttk.Button(self.round_action_frame, text="⚡ Next Round! ⚡", command=self._process_round, style="Golden.TButton", state=tk.DISABLED)
        self.next_round_button.pack(side="right", padx=10)
        self.round_action_frame.pack_forget() # Initially hidden


    def _create_duelist_panel_ui_elements(self, parent, player_num_display):
        panel = ttk.Frame(parent, style="Section.TFrame", padding=15)
        panel.columnconfigure(0, weight=1) # Make content expand

        name_label = ttk.Label(panel, text=f"Duelist {player_num_display}", style="Header.TLabel", background=self.theme_colors["frame_bg"])
        name_label.grid(row=0, column=0, pady=(0,10), sticky="ew")
        setattr(self, f"p{player_num_display}_name_label", name_label)

        hp_label = ttk.Label(panel, text="HP: ???/???", style="Body.TLabel", background=self.theme_colors["frame_bg"])
        hp_label.grid(row=1, column=0, pady=2, sticky="w")
        setattr(self, f"p{player_num_display}_hp_label", hp_label)

        mp_label = ttk.Label(panel, text="MP: ???/???", style="Body.TLabel", background=self.theme_colors["frame_bg"])
        mp_label.grid(row=2, column=0, pady=2, sticky="w")
        setattr(self, f"p{player_num_display}_mp_label", mp_label)

        status_label = ttk.Label(panel, text="Status: Normal", style="Small.TLabel", background=self.theme_colors["frame_bg"], foreground=self.theme_colors["gold_fg"])
        status_label.grid(row=3, column=0, pady=(2,10), sticky="w")
        setattr(self, f"p{player_num_display}_status_label", status_label)

        # Potion Button Section
        potion_button_frame = ttk.Frame(panel, style="Section.TFrame") # Use Section.TFrame for consistent bg
        potion_button_frame.grid(row=4, column=0, pady=5, sticky="ew")
        
        # Example for Wiggenweld Potion
        wiggenweld_button = ttk.Button(potion_button_frame, text="Use Wiggenweld (X)", style="TButton") # Text updated in _update_ui
        wiggenweld_button.pack(fill="x", expand=True)
        setattr(self, f"p{player_num_display}_wiggenweld_button", wiggenweld_button)
        # The command will be set in _initialize_duel or _update_ui to pass correct duelist_state

        return panel

    def _add_to_duel_log(self, message, color=None, style="DuelLog.TLabel"):
        log_entry_label = ttk.Label(self.duel_log_display_frame, text=message, style=style, wraplength=self.arena_frame.winfo_width()//3 - 40) # Adjust wraplength as needed
        if color: log_entry_label.configure(foreground=color)
        log_entry_label.pack(anchor="w", pady=1)
        self.duel_log_texts.append(message) # Store for potential future use

        # Auto-scroll to bottom
        log_canvas = self.duel_log_display_frame.master # The canvas containing the scrollable frame
        log_canvas.update_idletasks() # Ensure layout is updated
        log_canvas.yview_moveto(1.0) # Scroll to the end

    def _initialize_duel(self):
        d1_name = self.duelist1_var.get(); d2_name = self.duelist2_var.get()
        if not d1_name or not d2_name: messagebox.showerror("Selection Error", "Please select both duelists.", parent=self); return
        if d1_name == d2_name: messagebox.showerror("Selection Error", "Duelists cannot be the same student.", parent=self); return

        d1_base_data = self.all_student_data_ref.get(d1_name, self.app_ref._get_default_student_data())
        d2_base_data = self.all_student_data_ref.get(d2_name, self.app_ref._get_default_student_data())

        # Create DuelistState instances, passing all necessary configs
        self.duelist1_state = DuelistState(d1_name, self.app_ref.current_assignments.get(d1_name, "N/A"), d1_base_data.get("hp", DEFAULT_HP), d1_base_data.get("mp", DEFAULT_MP), self.spell_details, self.potions_config)
        self.duelist2_state = DuelistState(d2_name, self.app_ref.current_assignments.get(d2_name, "N/A"), d2_base_data.get("hp", DEFAULT_HP), d2_base_data.get("mp", DEFAULT_MP), self.spell_details, self.potions_config)
        
        # Set commands for potion buttons now that states exist
        self.p1_wiggenweld_button.configure(command=lambda: self._use_potion(self.duelist1_state, "Wiggenweld Potion"))
        self.p2_wiggenweld_button.configure(command=lambda: self._use_potion(self.duelist2_state, "Wiggenweld Potion"))


        # Show arena elements
        self.p1_panel.grid(); self.p2_panel.grid()
        self.round_action_frame.pack(fill="x", pady=10)
        self.start_duel_button.configure(state=tk.DISABLED)
        self.duelist1_combo.configure(state=tk.DISABLED); self.duelist2_combo.configure(state=tk.DISABLED)
        self.next_round_button.configure(state=tk.NORMAL, text="⚡ Next Round! ⚡") # Ensure text is reset

        self.game_over = False; self.round_count = 0
        # Clear previous duel log visually (or add a separator)
        for widget in self.duel_log_display_frame.winfo_children(): widget.destroy()
        self.duel_log_texts.clear()

        self._add_to_duel_log(f"A duel begins between {d1_name} and {d2_name}!", self.theme_colors["gold_fg"])
        play_sound(self.sounds.get("duel_start"))
        self._update_ui_for_current_state()
        self._process_round() # Start the first round automatically


    def _update_ui_for_current_state(self):
        if not self.duelist1_state or not self.duelist2_state: return
        for p_num_display, duelist in [(1, self.duelist1_state), (2, self.duelist2_state)]:
            name_label = getattr(self, f"p{p_num_display}_name_label")
            hp_label = getattr(self, f"p{p_num_display}_hp_label")
            mp_label = getattr(self, f"p{p_num_display}_mp_label")
            status_label = getattr(self, f"p{p_num_display}_status_label")
            wiggenweld_button = getattr(self, f"p{p_num_display}_wiggenweld_button")

            house_color = HOUSES.get(duelist.house, {}).get("color", self.theme_colors["fg"])
            name_label.configure(text=f"{HOUSES.get(duelist.house,{}).get('animal','')} {duelist.name} ({duelist.house})", foreground=house_color)
            hp_label.configure(text=f"HP: {duelist.hp}/{duelist.max_hp}")
            mp_label.configure(text=f"MP: {duelist.mp}/{duelist.max_mp}")
            status_text = "Status: Normal"
            if duelist.status_effects:
                effects = [f"{name.replace('_',' ').title()} ({val['duration']})" for name, val in duelist.status_effects.items()]
                status_text = "Status: " + ", ".join(effects)
            if duelist.shield_active: status_text += f" | Shielded ({duelist.shield_active['strength']})"
            status_label.configure(text=status_text)

            # Update Potion Button
            potion_uses = duelist.potions_available.get("Wiggenweld Potion", 0)
            wiggenweld_button.configure(text=f"Use Wiggenweld ({potion_uses})", state=tk.NORMAL if potion_uses > 0 and not self.game_over else tk.DISABLED)


        self.round_indicator_label.configure(text=f"Round: {self.round_count}")
        self.next_round_button.configure(state=tk.NORMAL if not self.game_over else tk.DISABLED)


    def _use_potion(self, duelist_state, potion_name):
        if self.game_over: return
        potion_data = self.potions_config.get(potion_name)
        if not potion_data or duelist_state.potions_available.get(potion_name, 0) <= 0:
            self._add_to_duel_log(f"{duelist_state.name} has no {potion_name} left!", "orange")
            return

        duelist_state.potions_available[potion_name] -= 1
        if potion_data["type"] == "heal":
            duelist_state.apply_heal(potion_data["amount"])
            self._add_to_duel_log(f"{duelist_state.name} uses {potion_name}, healing {potion_data['amount']} HP!", "green")
            play_sound(self.sounds.get(potion_data.get("sound", "potion_use"))) # Use specific or generic potion sound
        
        self._update_ui_for_current_state() # Refresh UI, including potion button count and HP


    def _process_round(self):
        if self.game_over: return
        self.next_round_button.configure(state=tk.DISABLED) # Disable while processing
        self.round_count += 1
        self._add_to_duel_log(f"\n--- Round {self.round_count} ---", self.theme_colors["silver_fg"])

        # Tick status effects for both at start of round
        for duelist_state in [self.duelist1_state, self.duelist2_state]:
            if duelist_state:
                log_updates = duelist_state.tick_status_effects()
                for log_msg in log_updates: self._add_to_duel_log(log_msg)
        if self._check_game_over(): self.next_round_button.configure(state=tk.NORMAL); return # Game might end from status ticks

        # Determine spells (auto-cast for now)
        p1_spell_name = self.duelist1_state.choose_random_spell()
        p2_spell_name = self.duelist2_state.choose_random_spell()

        self.duelist1_state.selected_spell = p1_spell_name
        self.duelist2_state.selected_spell = p2_spell_name

        log_p1_action = f"{self.duelist1_state.name} prepares to cast {p1_spell_name}!" if p1_spell_name else f"{self.duelist1_state.name} cannot find a spell to cast!"
        log_p2_action = f"{self.duelist2_state.name} prepares to cast {p2_spell_name}!" if p2_spell_name else f"{self.duelist2_state.name} is unable to cast!"
        self._add_to_duel_log(log_p1_action, HOUSES.get(self.duelist1_state.house,{}).get("color"))
        self._add_to_duel_log(log_p2_action, HOUSES.get(self.duelist2_state.house,{}).get("color"))

        # Resolve Simultaneous Spells
        self._resolve_simultaneous_spells(self.duelist1_state, self.duelist2_state)

        # Regenerate some MP at end of round
        self.duelist1_state.mp = min(self.duelist1_state.max_mp, self.duelist1_state.mp + 5)
        self.duelist2_state.mp = min(self.duelist2_state.max_mp, self.duelist2_state.mp + 5)

        self._update_ui_for_current_state()
        if not self.game_over: self.next_round_button.configure(state=tk.NORMAL)
        # If game over, button state handled by _check_game_over's call to _schedule_stats_restoration


    def _resolve_simultaneous_spells(self, d1, d2):
        s1_name, s2_name = d1.selected_spell, d2.selected_spell
        s1_info, s2_info = self.spell_details.get(s1_name), self.spell_details.get(s2_name)

        if not s1_info and not s2_info: self._add_to_duel_log("Both duelists fumble their spells!", "grey"); return
        if not s1_info: self._execute_spell(d2, d1, s2_name); self._check_game_over(); return
        if not s2_info: self._execute_spell(d1, d2, s1_name); self._check_game_over(); return

        interaction_key = tuple(sorted((s1_name, s2_name)))
        interaction_details = self.spell_interactions.get(interaction_key)

        if interaction_details:
            self._add_to_duel_log(f"✨ Interaction! {interaction_details['log']} ✨", self.theme_colors["gold_fg"])
            play_sound(self.sounds.get(interaction_details.get("sound", "generic_spell_clash")))
            self._resolve_interaction_outcome(interaction_details["resolve"], d1, d2, s1_info, s2_info)
        else: # Default: both spells attempt to execute
            self._add_to_duel_log("Spells fly simultaneously!")
            self._execute_spell(d1, d2, s1_name)
            if self._check_game_over(): return # Check immediately after first spell
            self._execute_spell(d2, d1, s2_name)
            self._check_game_over()


    def _resolve_interaction_outcome(self, resolution_type, d1, d2, s1_info, s2_info):
        # Custom resolution logic based on resolution_type string
        # Determine which duelist cast which spell for asymmetric interactions
        caster_of_s1 = d1 if d1.selected_spell == s1_info.get("name", d1.selected_spell) else d2 # Crude way if names aren't in info
        target_of_s1 = d2 if caster_of_s1 == d1 else d1
        caster_of_s2 = d2 if d2.selected_spell == s2_info.get("name", d2.selected_spell) else d1
        target_of_s2 = d1 if caster_of_s2 == d2 else d2

        if resolution_type == "priori_incantatem":
            self._add_to_duel_log("The wands connect! A bead of light forms...", "yellow")
            d1.consume_mp(s1_info.get("mp",0)//2); d2.consume_mp(s2_info.get("mp",0)//2) # MP drain
            dmg, log = d1.apply_damage(5,"interaction"); self._add_to_duel_log(f"{d1.name} takes 5 feedback! {log}")
            dmg, log = d2.apply_damage(5,"interaction"); self._add_to_duel_log(f"{d2.name} takes 5 feedback! {log}")
        elif resolution_type == "custom:steam_cloud_miss_both":
            self._add_to_duel_log("A thick steam cloud erupts, obscuring vision!", "grey")
            d1.add_status_effect("blinded", 1); d2.add_status_effect("blinded", 1)
        elif resolution_type == "custom:protego_deflects_projectile": # Generic shield vs projectile
            protego_caster, projectile_caster = (d1, d2) if d1.selected_spell.startswith("Protego") else (d2, d1)
            self._add_to_duel_log(f"{projectile_caster.name}'s spell is deflected by {protego_caster.name}'s {protego_caster.selected_spell}!")
            protego_caster.activate_shield(protego_caster.selected_spell)
        elif resolution_type == "custom:protego_vs_ak":
            ak_caster, protego_caster = (d1, d2) if d1.selected_spell == "Avada Kedavra" else (d2, d1)
            self._add_to_duel_log(f"{protego_caster.name}'s Protego bravely meets the Killing Curse!")
            protego_caster.activate_shield(protego_caster.selected_spell)
            ak_spell_info = self.spell_details.get("Avada Kedavra")
            dmg, log = protego_caster.apply_damage(ak_spell_info.get("base_dmg",80)//2, "offensive_dark_unforgivable")
            self._add_to_duel_log(f"The shield shatters, but absorbs some dark energy! {protego_caster.name} takes {dmg} damage! {log}")
        elif resolution_type == "custom:sectumsempra_hinders_episkey":
            heal_caster, dark_caster = (d1,d2) if s1_info.get("type") == "heal" else (d2,d1)
            heal_amount = heal_caster.spell_details[heal_caster.selected_spell].get("base_heal",0) // 2
            heal_caster.apply_heal(heal_amount)
            self._add_to_duel_log(f"{dark_caster.name}'s dark magic interferes! {heal_caster.name}'s Episkey only heals for {heal_amount} HP.", "magenta")
            self._execute_spell(dark_caster, heal_caster, dark_caster.selected_spell)
        elif resolution_type == "custom:finite_breaks_bind": # e.g. Finite vs Petrificus
            finite_caster, bound_caster = (d1,d2) if d1.selected_spell == "Finite Incantatem" else (d2,d1)
            if bound_caster.has_status("stun") or bound_caster.has_status("leg_lock"):
                if bound_caster.has_status("stun"): del bound_caster.status_effects["stun"]
                if bound_caster.has_status("leg_lock"): del bound_caster.status_effects["leg_lock"]
                self._add_to_duel_log(f"{finite_caster.name}'s Finite Incantatem frees {bound_caster.name}!", "cyan")
            else: self._execute_spell(finite_caster, bound_caster, finite_caster.selected_spell)
        elif resolution_type == "custom:finite_lessens_crucio":
            finite_caster, cursed_caster = (d1,d2) if d1.selected_spell == "Finite Incantatem" else (d2,d1)
            if cursed_caster.has_status("pain_dot"):
                cursed_caster.status_effects["pain_dot"]["duration"] = 0
                self._add_to_duel_log(f"{finite_caster.name}'s Finite Incantatem ends the Cruciatus on {cursed_caster.name}!", "cyan")
            else: self._execute_spell(finite_caster, cursed_caster, finite_caster.selected_spell)
        elif resolution_type == "both_fizzle":
             self._add_to_duel_log("The spells collide and fizzle out harmlessly.", "grey")
        elif resolution_type == "custom:fire_vs_ice_steam":
            self._add_to_duel_log("Incendio and Glacius clash! A blast of hot steam and freezing mist!", "orange")
            dmg1, log1 = d1.apply_damage(5, "interaction_aoe"); self._add_to_duel_log(f"{d1.name} is caught in the chaotic energy! {log1}")
            dmg2, log2 = d2.apply_damage(5, "interaction_aoe"); self._add_to_duel_log(f"{d2.name} is caught in the chaotic energy! {log2}")
        elif resolution_type == "custom:expelliarmus_vs_protego":
            protego_caster, exp_caster = (d1,d2) if d1.selected_spell == "Protego" else (d2,d1)
            protego_caster.activate_shield("Protego")
            self._add_to_duel_log(f"{exp_caster.name}'s Expelliarmus is blocked by {protego_caster.name}'s Protego! The wand stays put.", "cyan")
        elif resolution_type == "custom:double_incendio":
            self._add_to_duel_log("Twin Incendios merge into a fierce conflagration!", "red")
            dmg, log = d1.apply_damage(8, "fire_burst"); self._add_to_duel_log(f"{d1.name} is singed for {dmg} damage! {log}")
            dmg, log = d2.apply_damage(8, "fire_burst"); self._add_to_duel_log(f"{d2.name} is singed for {dmg} damage! {log}")
        elif resolution_type == "custom:bind_vs_shield": # e.g. Petrificus vs Protego
            protego_caster, bind_caster = (d1,d2) if d1.selected_spell == "Protego" else (d2,d1)
            protego_caster.activate_shield("Protego")
            self._add_to_duel_log(f"{bind_caster.name}'s {bind_caster.selected_spell} is blocked by {protego_caster.name}'s Protego!", "cyan")
        elif resolution_type == "custom:confound_vs_shield": # Confundo vs Protego
            protego_caster, conf_caster = (d1,d2) if d1.selected_spell == "Protego" else (d2,d1)
            protego_caster.activate_shield("Protego")
            self._add_to_duel_log(f"{conf_caster.name}'s Confundus Charm is repelled by {protego_caster.name}'s Protego!", "cyan")

        else: # Fallback for unhandled custom or generic types
            self._add_to_duel_log(f"Spells interact: {resolution_type}. Defaulting to standard execution.", "grey")
            self._execute_spell(d1, d2, d1.selected_spell)
            if not self._check_game_over(): self._execute_spell(d2, d1, d2.selected_spell)

        self._check_game_over()


    def _execute_spell(self, caster, target, spell_name):
        spell = self.spell_details.get(spell_name)
        if not spell: self._add_to_duel_log(f"{caster.name} fumbles!", "red"); return

        if caster.has_status("stun") or caster.has_status("dance") or caster.has_status("leg_lock") or caster.has_status("blinded") or caster.has_status("confuse") or caster.has_status("worms"):
            if random.random() < 0.5: # 50% chance to fail if affected by these
                self._add_to_duel_log(f"{caster.name} is {list(caster.status_effects.keys())[0]} and the spell fails!", "orange"); return
        if caster.has_status("silence") or caster.has_status("tongue_tie") or caster.has_status("tongue_lock"):
             self._add_to_duel_log(f"{caster.name} is silenced/tongue-tied and cannot cast!", "orange"); return

        # MP cost is handled by choose_random_spell or player choice (if implemented)
        if "unforgivable" in spell.get("type",""): play_sound(self.sounds.get("unforgivable_cast"))
        else: play_sound(self.sounds.get("spell_cast_ui"))

        roll = random.randint(1, 20)
        target_to_hit = spell.get("accuracy", 10)
        is_crit_hit = roll >= spell.get("crit_chance", 20)
        is_crit_miss = roll == 1
        self._add_to_duel_log(f"{caster.name}'s d20 roll for {spell_name}: {roll} (needs >={target_to_hit})", "darkgrey")


        if is_crit_miss:
            self._add_to_duel_log(f"Critical Fail! {caster.name}'s {spell_name} backfires!", "red"); play_sound(self.sounds.get("duel_crit_miss"))
            dmg,log = caster.apply_damage(spell.get("base_dmg",5)//2 + 3, spell.get("type")); self._add_to_duel_log(f"{caster.name} takes {dmg} from backfire! {log}"); return

        if roll < target_to_hit and "offensive" in spell.get("type",""): # Non-offensive spells might not "miss" in the same way
            self._add_to_duel_log(f"{caster.name}'s {spell_name} misses {target.name}!", "grey"); play_sound(self.sounds.get("duel_miss")); return

        if is_crit_hit: self._add_to_duel_log(f"Critical Hit!", self.theme_colors["gold_fg"]); play_sound(self.sounds.get("duel_crit_hit"))

        spell_type = spell.get("type")
        if spell_type == "heal":
            heal = spell.get("base_heal",0) * (1.5 if is_crit_hit else 1)
            caster.apply_heal(int(heal)); self._add_to_duel_log(f"{caster.name} heals for {int(heal)} HP.", "green"); play_sound(self.sounds.get("heal_sound"))
        elif spell_type in ["shield", "shield_special", "shield_area"]:
            log = caster.activate_shield(spell_name); self._add_to_duel_log(log, "cyan"); play_sound(self.sounds.get("duel_block"))
        elif "offensive" in spell_type:
            dmg = spell.get("base_dmg",0) * (1.5 if is_crit_hit else 1)
            actual_dmg, shield_log = target.apply_damage(int(dmg), spell_type)
            if shield_log: self._add_to_duel_log(shield_log, "cyan")
            if actual_dmg > 0: self._add_to_duel_log(f"{spell_name} hits {target.name} for {actual_dmg} damage!", "red"); play_sound(self.sounds.get("duel_hit"))
            elif not shield_log : self._add_to_duel_log(f"{target.name} seems unaffected by {spell_name}!", "grey")

            if "effect" in spell and (is_crit_hit or random.randint(1,20) >= spell.get("effect_chance",15)):
                details = {"dmg": spell.get("dot_dmg")} if spell["effect"] == "pain_dot" else {}
                target.add_status_effect(spell["effect"], spell.get("duration",1), details)
                self._add_to_duel_log(f"{target.name} is now {spell['effect'].replace('_',' ')}!", "magenta")
        elif spell_type == "counter_utility" and spell_name == "Finite Incantatem":
            dispelled = False
            for effect in list(target.status_effects.keys()):
                del target.status_effects[effect]; dispelled=True
                self._add_to_duel_log(f"Finite Incantatem dispels {effect.replace('_',' ')} from {target.name}!", "cyan")
            if target.shield_active : target.shield_active = None; dispelled=True; self._add_to_duel_log(f"Finite Incantatem dispels {target.name}'s shield!", "cyan")
            if not dispelled: self._add_to_duel_log("Finite Incantatem has no current effects to dispel on target.", "grey")
            play_sound(self.sounds.get("status_cure"))
        elif spell_type == "summon_snake":
             target.add_status_effect("snake_attack_pending", 1, {"caster": caster.name})
             self._add_to_duel_log(f"{caster.name} summons a venomous snake that eyes {target.name} menacingly!", "green")
        elif spell_type == "summon_birds":
             target.add_status_effect("birds_circling", 2, {"caster": caster.name})
             self._add_to_duel_log(f"{caster.name} conjures a flock of agitated birds around {target.name}!", "yellow")


    def _check_game_over(self):
        winner, loser = None, None
        if self.duelist1_state.hp <= 0: winner, loser = self.duelist2_state, self.duelist1_state
        elif self.duelist2_state.hp <= 0: winner, loser = self.duelist1_state, self.duelist2_state

        if winner:
            self.game_over = True
            self._add_to_duel_log(f"--- DUEL OVER! ---", self.theme_colors["gold_fg"])
            self._add_to_duel_log(f"{loser.name} has been defeated!", "red")
            self._add_to_duel_log(f"{winner.name} of House {winner.house} is victorious!", self.theme_colors["gold_fg"])
            play_sound(self.sounds.get("celebration"))

            # Update student data in main app for history (current HP/MP at end of duel)
            winner_main_data = self.all_student_data_ref.get(winner.name)
            if winner_main_data: winner_main_data["hp"] = winner.hp; winner_main_data["mp"] = winner.mp
            loser_main_data = self.all_student_data_ref.get(loser.name)
            if loser_main_data: loser_main_data["hp"] = loser.hp; loser_main_data["mp"] = loser.mp
            
            self.app_ref.history.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action": f"Dueling Club: {winner.name} ({winner.house}) defeated {loser.name} ({loser.house}).",
                "reason": f"Final HP: {winner.name} ({winner.hp}), {loser.name} ({loser.hp}) after {self.round_count} rounds.",
                "student": f"{winner.name}, {loser.name}"})
            
            winner_house_data = HOUSES.get(winner.house)
            if winner_house_data:
                winner_house_data["points"] += 10 # Award points for winning
                self._add_to_duel_log(f"House {winner.house} gains 10 points for the victory!", self.theme_colors["gold_fg"])
            
            self.app_ref.save_progress(); self.app_ref.update_display()
            self.next_round_button.configure(text="Duel Ended. Restoring...", state=tk.DISABLED) # Indicate restoration
            self._schedule_stats_restoration(winner.name, loser.name) # Schedule HP/MP restoration
            return True
        return False

    def _schedule_stats_restoration(self, winner_name, loser_name):
        self.after(3000, lambda: self._restore_duelists_stats(winner_name, loser_name))

    def _restore_duelists_stats(self, winner_name, loser_name):
        self._add_to_duel_log(f"Restoring HP/MP for {winner_name} and {loser_name}...", self.theme_colors["silver_fg"])
        
        for student_name in [winner_name, loser_name]:
            student_data = self.all_student_data_ref.get(student_name)
            if student_data:
                student_data["hp"] = DEFAULT_HP
                student_data["mp"] = DEFAULT_MP
                student_data["status_effects"] = {} # Clear any lingering duel status effects
                self._add_to_duel_log(f"{student_name}: HP set to {DEFAULT_HP}, MP set to {DEFAULT_MP}.", "grey")

        self.app_ref.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": f"Post-Duel: HP/MP restored for {winner_name} and {loser_name}.",
            "reason": "Automatic restoration after duel completion."
        })
        self.app_ref.save_progress()
        self.app_ref.update_display() # Update main app's display of student stats

        self._add_to_duel_log("HP/MP restored. Ready for a new duel!", self.theme_colors["gold_fg"])
        
        # Reset Duel Window UI for a new duel
        self.duelist1_combo.configure(state="readonly")
        self.duelist2_combo.configure(state="readonly")
        self.start_duel_button.configure(state=tk.NORMAL)
        self.next_round_button.configure(text="⚡ Next Round! ⚡", state=tk.DISABLED) # Reset button text
        self.round_action_frame.pack_forget() # Hide round actions
        self.p1_panel.grid_remove() # Hide duelist panels
        self.p2_panel.grid_remove()
        self.round_count = 0
        self.round_indicator_label.configure(text="Round: 0")
        
        # Add a separator or clear log for the next duel
        self._add_to_duel_log("\n------------------------------------", "grey")
        self._add_to_duel_log("Select duelists to begin a new duel.", self.theme_colors["gold_fg"])
        
        self.game_over = False # Reset game_over flag for the window state itself


# ==== MAIN EXECUTION ====
if __name__ == "__main__":
    ensure_directory(AVATAR_DIR); ensure_directory(ASSETS_DIR)
    main_window = tk.Tk()
    try:
        icon_path = get_asset_path("hogwarts.ico") # Ensure you have this icon file
        if os.path.exists(icon_path): main_window.iconbitmap(icon_path)
    except tk.TclError: print("Note: Could not set window icon (hogwarts.ico not found or platform issue).")
    except Exception as e: print(f"Error setting icon: {e}")

    app_instance = HogwartsTracker(main_window)
    main_window.mainloop()

    if PYGAME_AVAILABLE and pygame.mixer.get_init(): pygame.mixer.quit() # Clean up pygame mixer

