from dataclasses import dataclass


@dataclass(frozen = True)

class ScreenConfig:

    width: int = 900
    height: int = 900
    fps: int = 120
    caption: str = "Breakout game"


@dataclass(frozen = True)

class BatConfig:

    width: int = 120
    height: int = 20
    speed: int = 9
    y_offset_from_bottom: int = 55  


@dataclass(frozen = True)

class BallConfig:

    speed: int = 4
    max_speed: int = 6
    fallback_size: tuple[int, int] = (18, 18)


@dataclass(frozen = True)

class BrickConfig:

    width: int = 80
    height: int = 50
    gap: int = 6
    top_margin: int = 50
    side_margin: int = 10
    rows: int = 7
    cols: int = 10
    power_chance: float = 0.10


@dataclass(frozen = True)

class AssetsConfig:

    bg_image: str = "breakout_game/assets/images/starsbg.png"
    ball_image_file: str = "breakout_game/assets/images/ball.png"
    brick_hit_sfx: str = "breakout_game/assets/sounds/bullet.mp3"
    bounce_sfx: str = "breakout_game/assets/sounds/hit.mp3"
    music_file: str = "breakout_game/assets/sounds/music.mp3"


@dataclass(frozen = True)

class AudioConfig:

    bounce_volume: float = 0.2
    music_volume: float = 0.1


@dataclass(frozen = True)

class RulesConfig:

    start_lives: int = 5
    force_ball_down_after_brick: bool = True


SCREEN = ScreenConfig()
BAT = BatConfig()
BALL = BallConfig()
BRICKS = BrickConfig()
ASSETS = AssetsConfig()
AUDIO = AudioConfig()
RULES = RulesConfig()