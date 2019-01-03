import gamelib
import random
import math
import queue
import warnings
from sys import maxsize

class Objectives:
    def __init__(self, gs):
        self.objectives = []
        self.gs = gs
    
    def add(self, priority, unit, location):
        objective = (priority, unit, location)
        if self.check_objective(objective):
            self.objectives.append(objective)
    
    def get_top_objective(self):
        if len(self.objectives) == 0:
            return None
        else:
            self.objectives.sort()
            return self.objectives[0]
    
    def check_objective(self, objective):
        return self.gs.can_spawn(objective[1], objective[2])
    
    def execute_objective(self, objective):
        if objective == None:
            return False
        else:
            self.gs.attempt_spawn(objective[1], objective[2])
            return True

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        #random.seed()

    def on_game_start(self, config):
        gamelib.debug_write('Configuring...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

        #self.defensive_wall_row = None

    def on_turn(self, turn_state):
        game_state = gamelib.AdvancedGameState(self.config, turn_state)
        gamelib.debug_write('Turn {}, health {}'.format(game_state.turn_number, game_state.my_health))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.main_strategy(game_state)

        game_state.submit_turn()

    def main_strategy(self, gs):
        # self.detect_enemy_strategy(gs)
        # if False: #True: #and self.defensive_wall_row == None:
        #     WALL_FRONT = []
        #     for i in range(0, 4):
        #         WALL_FRONT.append([i, 13])
        #         WALL_FRONT.append([27 - i, 13])
        #     WALL_BACK = []
        #     for i in range(0, 4):
        #         WALL_BACK.append([1 + i, 12])
        #         WALL_BACK.append([26 - i, 12])
        # else:
        WALL_FRONT = []
        for i in range(5, 28):
            WALL_FRONT.append([i, 13])
        WALL_BACK = []
        for i in range(5, 27):
            WALL_BACK.append([i, 13 - 1])
        WALL_EDGE = [[0,13],[1,12],[2,11],[3,10],[4,9],[27,13],[26,12],[25,11],[24,10],[23,9]]
        TOWERS = [[4,12],[23,12],[10,10],[18,11],[7,8],[21,9],[14,7]]

        ENCRYPTOR_LOC = []
        for i in range(7, 10):
            for j in range(10, 13):
                ENCRYPTOR_LOC.append([i, j])

        BOTTOM_LEFT = gs.game_map.get_edges()[2]
        BOTTOM_RIGHT = gs.game_map.get_edges()[3]
        
        while True:
            objectives = Objectives(gs)
            for i in WALL_BACK:
                attackers = len(gs.get_attackers(i, 1))
                if attackers < 2:
                    objectives.add([4, attackers], DESTRUCTOR, i)
            for i in WALL_FRONT:
                priority = [5]
                if gs.game_map.in_arena_bounds([i[0], 12]):
                    above = gs.game_map[[i[0], 12]]
                    if any(j.unit_type == DESTRUCTOR for j in above):
                        priority = [1]
                objectives.add(priority, FILTER, i)
            for i in WALL_EDGE:
                objectives.add([1, i[1]], DESTRUCTOR, i)
            for i in TOWERS:
                objectives.add([6, 1], DESTRUCTOR, i)
                objectives.add([6, 2], FILTER, [i[0]-1,i[1]+1])
                objectives.add([6, 2], FILTER, [i[0]+1,i[1]+1])
            for i in ENCRYPTOR_LOC:
                objectives.add([10], ENCRYPTOR, i)
            # if self.defensive_wall_row != None:
            #     for i in range(0, 28):
            #         x = [i, self.defensive_wall_row]
            #         if gs.game_map.in_arena_bounds(x) and gs.can_spawn(FILTER, x):
            #             objectives.append(([0], 'filter', x))
            #if gs.can_spawn(PING, [14, 0]):
            #    objectives.append(([1], 'ping', [14, 0]))
            objective = objectives.get_top_objective()
            objective_executed = objectives.execute_objective(objective)
            if not objective_executed:
                break
        
        if gs.get_resource(gs.BITS) >= random.uniform(5, 10):
            objectives = Objectives(gs)
            for i in BOTTOM_LEFT:
                if gs.can_spawn(PING, i):
                    quantity = gs.number_affordable(PING)
                    evaluation = self.evaluate_attack(gs, 0, i, PING, quantity)
                    objectives.add(-evaluation, PING, i)
                if gs.can_spawn(EMP, i):
                    quantity = gs.number_affordable(EMP)
                    evaluation = self.evaluate_attack(gs, 0, i, EMP, quantity)
                    objectives.add(-evaluation, EMP, i)
            for i in BOTTOM_RIGHT:
                if gs.can_spawn(PING, i):
                    quantity = gs.number_affordable(PING)
                    evaluation = self.evaluate_attack(gs, 1, i, PING, quantity)
                    objectives.add(-evaluation, PING, i)
                if gs.can_spawn(EMP, i):
                    quantity = gs.number_affordable(EMP)
                    evaluation = self.evaluate_attack(gs, 1, i, EMP, quantity)
                    objectives.add(-evaluation, EMP, i)
            objective = objectives.get_top_objective()
            for i in range(3):
                if objectives.objectives[i] != None:
                    gamelib.debug_write(objectives.objectives[i])
            while objectives.check_objective(objective):
                objectives.execute_objective(objective)
    
    def evaluate_attack(self, gs, edge, loc, unit, initial_quantity):
        if edge == 0:
            # bottom left
            path = gs.find_path_to_edge(loc, gs.game_map.TOP_RIGHT)
        else:
            # bottom right
            path = gs.find_path_to_edge(loc, gs.game_map.TOP_LEFT)
        if unit == PING:
            unit_stability = 15
            unit_damage = 1
            unit_speed = 2
        elif unit == EMP:
            unit_stability = 5
            unit_damage = 3
            unit_speed = 4
        score = 0
        path_completed = True
        total_stability = unit_stability * initial_quantity
        for i in path:
            target = gs.get_target(gamelib.unit.GameUnit(unit, self.config, x=i[0], y=i[1]))
            attackers = len(gs.get_attackers(i, 0))
            #gamelib.debug_write(unit_speed)
            for _ in range(unit_speed):
                if total_stability <= 0:
                    path_completed = False
                    break
                quantity = total_stability / unit_stability
                if target != None:
                    if target.unit_type == DESTRUCTOR:
                        score += 3 / 75 * quantity * unit_damage
                    elif target.unit_type == ENCRYPTOR:
                        score += 4 / 30 * quantity * unit_damage
                    elif target.unit_type == FILTER:
                        score += 1 / 60 * quantity * unit_damage
                total_stability -= attackers * 4
                if total_stability <= 0:
                    path_completed = False
                    break
        if path_completed:
            score += total_stability * 10000
        return score
    
    # def detect_enemy_strategy(self, gs):
    #     filter_freq = [0] * 28
    #     destr_freq = [0] * 28
    #     encr_count = 0
    #     for i in range(0, 28):
    #         for j in range(0, 28):
    #             if gs.game_map.in_arena_bounds([i, j]):
    #                 x = gs.game_map[i, j]
    #                 if len(x) > 0:
    #                     if x[0].unit_type == FILTER:
    #                         filter_freq[j] += 1
    #                     if x[0].unit_type == DESTRUCTOR:
    #                         destr_freq[j] += 1
    #                     if x[0].unit_type == ENCRYPTOR and j <=13:
    #                         encr_count += 1
    #     gamelib.debug_write(destr_freq)
    #     for i in range(17, 28):
    #         if destr_freq[i] > 5:
    #             # wall detected! destroy it with EMPs
    #             gamelib.debug_write('ENEMY WALL DETECTED!!')
    #             if self.defensive_wall_row == None:
    #                 self.defensive_wall_row = i - 4
    #     if encr_count > 2:
    #         self.encr_attack = True
    #     else:
    #         self.encr_attack = False

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
