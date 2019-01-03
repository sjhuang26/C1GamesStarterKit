from copy import deepcopy

class PathMap:
    def __init__(self, game_state):
        self.game_state = game_state
        self.values = [[None for x in range(self.game_state.ARENA_SIZE)] for y in range(self.game_state.ARENA_SIZE)]
    
    def apply_game_state(self):
        for location in self.game_state.game_map:
            value = self.game_state.contains_stationary_unit(location)
            self.values[location[0]][location[1]] = value
    
    def clone_map(self):
        copied_values = deepcopy(self.values)
        copied_map = PathMap(self.game_state)
        copied_map.values = copied_values
        return copied_map
