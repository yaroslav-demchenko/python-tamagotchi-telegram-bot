from models.pet import Pet

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.coins = 100
        self.inventory = {}
        self.pet = None  # Додаємо атрибут для збереження тварини

    def add_coins(self, amount):
        self.coins += amount

    def spend_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def ensure_attributes(self):
        if not hasattr(self, 'inventory'):
            self.inventory = {}
        if not hasattr(self, 'pet'):
            self.pet = None

    def add_to_inventory(self, item):
        if item in self.inventory:
            self.inventory[item] += 1
        else:
            self.inventory[item] = 1
