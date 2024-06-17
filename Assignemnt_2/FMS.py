from random import uniform

class FMSPriority():
    def __init__(self, start_action):
        self.current_action = start_action
    
    def sample(self, distr):
        for prob in distr:
            random_val = uniform(0, 1)
            if random_val < prob[1]:
                print(prob)
                return prob[0]
        return distr[-1][0]

    def do(self):
        self.current_action.do(self)
        prob_distr = self.current_action.prob(self)
        new_action = self.sample(prob_distr)
        if new_action == self.current_action:
            self.current_action.switch(self)
            self.current_action = new_action

# def do_nothing(something):
#     something.check = 'doing nothing'
#     return ['say_hello']

# def say_hello(something):
#     something.check = 'hello world!'
#     return ['do_nothing']

# def prob_nothing(someting):
#     return {'say_hello': 1}

# def prob_hello(something):
#     return {'do_nothing': 1}

# tmp = FMS({'do_nothing': do_nothing, 'say_hello': say_hello}, {'do_nothing': prob_nothing, 'say_hello': prob_hello}, 'do_nothing')
# tmp.do()
# print(tmp.check)
# tmp.do()
# print(tmp.check)
