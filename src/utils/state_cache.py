from collections import defaultdict
import pickle
import os

class StateCache:
    def __init__(self, cache_file='state_cache.pkl'):
        self.cache_file = cache_file
        self.cache = defaultdict(dict)
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)

    def save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
        self.save_cache()

    def clear(self):
        self.cache.clear()
        self.save_cache()