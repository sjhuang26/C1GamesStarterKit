import gamelib
import random
import math
import queue
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

        self.defensive_wall_row = None

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.AdvancedGameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.main_strategy(game_state)

        game_state.submit_turn()
    
    def main_strategy(self, gs):
        if False: #True: #and self.defensive_wall_row == None:
            WALL_FRONT = []
            for i in range(0, 4):
                WALL_FRONT.append([i, 13])
                WALL_FRONT.append([27 - i, 13])
            WALL_BACK = []
            for i in range(0, 4):
                WALL_BACK.append([1 + i, 12])
                WALL_BACK.append([26 - i, 12])
        else:
            WALL_FRONT = []
            for i in range(5, 28):
                WALL_FRONT.append([i, 13])
            WALL_BACK = []
            for i in range(5, 28):
                WALL_BACK.append([i, 13 - 1])
        WALL_EDGE = [[0,13],[1,12],[2,11],[3,10],[4,9],[27,13],[26,12],[25,11],[24,10],[23,9]]
        TOWERS = [[4,12],[23,12],[10,10],[18,11],[7,8],[21,9],[14,7]]

        ENCRYPTOR_LOC = []
        for i in range(7, 10):
            for j in range(10, 13):
                ENCRYPTOR_LOC.append([i, j])

        BOTTOM_LEFT = gs.game_map.get_edges()[2]
        BOTTOM_RIGHT = gs.game_map.get_edges()[3]
        #gamelib.debug_write(BOTTOM_LEFT)

        self.detect_enemy_strategy(gs)
        
        keep_going = True
        while keep_going:
            #gamelib.debug_write('hi')
            keep_going = False
            objectives = []
            for i in WALL_BACK:
                attackers = len(gs.get_attackers(i, 1))
                if gs.can_spawn(DESTRUCTOR, i) and attackers < 2:
                    objectives.append(([4, attackers], 'destructor', i))
            for i in WALL_FRONT:
                if gs.can_spawn(FILTER, i):
                    if gs.game_map.in_arena_bounds([i[0], 12]):
                        above = gs.game_map[[i[0], 12]]
                        if any(j.unit_type == DESTRUCTOR for j in above):
                            objectives.append(([1], 'filter', i))
                        else:
                            objectives.append(([5], 'filter', i))
                    else:
                        objectives.append(([5], 'filter', i))
            for i in WALL_EDGE:
                if gs.can_spawn(DESTRUCTOR, i):
                    objectives.append(([1, i[1]], 'destructor', i))
            for i in TOWERS:
                if gs.can_spawn(DESTRUCTOR, i):
                    objectives.append(([6, 1], 'destructor', i))
                if gs.can_spawn(FILTER, [i[0]-1,i[1]+1]):
                    objectives.append(([6, 2], 'filter', [i[0]-1,i[1]+1]))
                if gs.can_spawn(FILTER, [i[0]+1,i[1]+1]):
                    objectives.append(([6, 2], 'filter', [i[0]+1,i[1]+1]))
            for i in ENCRYPTOR_LOC:
                if gs.can_spawn(ENCRYPTOR, i):
                    objectives.append(([10], 'encryptor', i))
            # if self.defensive_wall_row != None:
            #     for i in range(0, 28):
            #         x = [i, self.defensive_wall_row]
            #         if gs.game_map.in_arena_bounds(x) and gs.can_spawn(FILTER, x):
            #             objectives.append(([0], 'filter', x))
            #if gs.can_spawn(PING, [14, 0]):
            #    objectives.append(([1], 'ping', [14, 0]))
            objectives.sort()
            if len(objectives) > 0:
                for o in objectives:
                    if o[1] == 'destructor':
                        gs.attempt_spawn(DESTRUCTOR, o[2])
                        keep_going = True
                        break
                    if o[1] == 'filter':
                        gs.attempt_spawn(FILTER, o[2])
                        keep_going = True
                        break
                    if o[1] == 'encryptor':
                        gs.attempt_spawn(ENCRYPTOR, o[2])
                        keep_going = True
                        break
                    if o[1] == 'ping':
                        gs.attempt_spawn(PING, o[2])
                        keep_going = True
                        break
        # attack!!
        valuations = []
        for i in BOTTOM_LEFT:
            if gs.can_spawn(PING, i):
                # 0=right 1=left
                valuations.append((self.calc_valuation(gs, 0, i, 8, 2), i, PING))
        for i in BOTTOM_RIGHT:
            if gs.can_spawn(PING, i):
                valuations.append((self.calc_valuation(gs, 1, i, 8, 2), i, PING))
        #for i in BOTTOM_LEFT:
        #    if gs.can_spawn(EMP, i):
        #        # 0=right 1=left
        #        valuations.append((self.calc_valuation(gs, 0, i, 1, 3), i, EMP))
       # for i in BOTTOM_RIGHT:
        #    if gs.can_spawn(EMP, i):
        #        valuations.append((self.calc_valuation(gs, 1, i, 1, 3), i, EMP))
        valuations.sort(reverse=True)
        if gs.get_resource(gs.BITS) > 8:
            if self.encr_attack:
                while gs.can_spawn(PING, [14, 0]):
                    gs.attempt_spawn(PING, [14, 0])
            else:
                if random.uniform(0, 1) > 0.5:
                    while len(valuations) > 0 and gs.can_spawn(EMP, valuations[0][1]):
                        gs.attempt_spawn(EMP, valuations[0][1])
                else:
                    while len(valuations) > 0 and gs.can_spawn(PING, valuations[0][1]):
                        gs.attempt_spawn(PING, valuations[0][1])
    
    def calc_valuation(self, gs, edge, loc, initial_health, destruction_power):
        if edge == 0:
            # bottom left
            path = gs.find_path_to_edge(loc, gs.game_map.TOP_RIGHT)
        else:
            # bottom right
            path = gs.find_path_to_edge(loc, gs.game_map.TOP_LEFT)
        score = 10
        health = initial_health
        for i in path:
            target = gs.get_target(gamelib.unit.GameUnit(PING, self.config, x=i[0], y=i[1]))
            if target != None:
                if target.unit_type == DESTRUCTOR:
                    score += 3 * destruction_power
                elif target.unit_type == ENCRYPTOR:
                    score += 4 * destruction_power
                elif target.unit_type == FILTER:
                    score += 2 * destruction_power
                else:
                    score += 1 * destruction_power
            #gamelib.debug_write(gs.get_attackers(i, 0))
            health -= len(gs.get_attackers(i, 0))
            if health <= 0:
                score -= 10 # get rid of the initial bonus for damaging opponent
                break
        return score
    
    def detect_enemy_strategy(self, gs):
        filter_freq = [0] * 28
        destr_freq = [0] * 28
        encr_count = 0
        for i in range(0, 28):
            for j in range(0, 28):
                if gs.game_map.in_arena_bounds([i, j]):
                    x = gs.game_map[i, j]
                    if len(x) > 0:
                        if x[0].unit_type == FILTER:
                            filter_freq[j] += 1
                        if x[0].unit_type == DESTRUCTOR:
                            destr_freq[j] += 1
                        if x[0].unit_type == ENCRYPTOR and j <=13:
                            encr_count += 1
        gamelib.debug_write(destr_freq)
        for i in range(17, 28):
            if destr_freq[i] > 5:
                # wall detected! destroy it with EMPs
                gamelib.debug_write('ENEMY WALL DETECTED!!')
                if self.defensive_wall_row == None:
                    self.defensive_wall_row = i - 4
        if encr_count > 2:
            self.encr_attack = True
        else:
            self.encr_attack = False
        
if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
