import random


class Pet:
    def __init__(self):
        self.type = random.choice(['cat', 'dog', 'bird'])
        self.hunger = 100
        self.health = 100
        self.happiness = 100
        self.hunger_buff = [False, None]

    def feed(self):
        self.hunger = min(100, self.hunger + 10)

    def play(self):
        self.happiness = min(100, self.happiness + 10)

    def heal(self):
        self.health = min(100, self.health + 10)

    def status(self):
        return f"Type: {self.type}, Hunger: {self.hunger}, Health: {self.health}, Happiness: {self.happiness}, Buff: {self.hunger_buff[0]}"

    def degrade(self):
        if not self.hunger_buff[0]:
            if self.hunger > 0:
                self.hunger -= 1
        else:
            if self.hunger > 0:
                self.hunger -= 0.25
        if self.hunger < 70 and self.health > 0:
            self.health -= 1
        if self.hunger < 70 and self.health < 70 and self.happiness > 0:
            self.happiness -= 1
