from django.db import models

# Player model to represent a user by name
class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class GameScenario(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    initial_prompt = models.TextField()

    def __str__(self):
        return self.title

class GameSession(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    scenario = models.ForeignKey(GameScenario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    current_plot_point_id = models.CharField(max_length=100, null=True, blank=True)
    player_state = models.JSONField(default=dict)

    class Meta:
        # A player can only have one session per scenario
        unique_together = ('player', 'scenario')

    def __str__(self):
        return f"{self.scenario.title} - {self.player.name} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class GameLog(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='logs')
    message = models.TextField()
    is_major_decision = models.BooleanField(default=False)
    is_sent_by_user = models.BooleanField(default=True) # True for user messages, False for AI/GM messages
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.session_id} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
