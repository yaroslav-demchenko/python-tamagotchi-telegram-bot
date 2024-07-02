import pickle
import os


class Storage:
    def __init__(self):
        self.users_data_file = 'data/users_data.pkl'
        self.ensure_data_files_exist()
        self.users_data = self.load_users_data()

    def ensure_data_files_exist(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists(self.users_data_file):
            with open(self.users_data_file, 'wb') as f:
                pickle.dump({}, f, pickle.HIGHEST_PROTOCOL)

    def load_users_data(self):
        try:
            with open(self.users_data_file, 'rb') as f:
                users_data = pickle.load(f)
                # Ensure all users have the necessary attributes
                for user in users_data.values():
                    user.ensure_attributes()
                return users_data
        except (EOFError, FileNotFoundError):
            return {}

    def save_data(self):
        with open(self.users_data_file, 'wb') as f:
            pickle.dump(self.users_data, f, pickle.HIGHEST_PROTOCOL)

    def save_user(self, user_id, user):
        self.users_data[user_id] = user
        self.save_data()

    def add_item_to_inventory(self, user_id, item):
        user = self.users_data.get(user_id)
        if user:
            user.ensure_attributes()
            user.add_to_inventory(item)
            self.save_user(user_id, user)
