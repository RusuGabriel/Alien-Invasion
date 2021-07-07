class GameStats():
    """Track statistics for The Empire Strikes Back."""

    def __init__(self, ai_settings):
        """Initialize statistics."""
        self.ai_settings = ai_settings
        self.reset_stats()
        self.score = 0
        #Start The Empire Strikes Back in an active state.
        self.game_active = False
        #High score should never be reset.
        self.high_score = 0
        

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.ai_settings.ships_limit
        self.score = 0
        self.level = 1
