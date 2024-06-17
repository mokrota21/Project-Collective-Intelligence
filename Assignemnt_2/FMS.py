from random import uniform

class FMS():
    def __init__(self, actions, prob, start_action):
        self.actions = actions
        self.prob = prob
        self.current_action = start_action
    
    def sample(self, distr):
        random_val = uniform(0, 1)
        if abs(sum(distr.values())) > 1:
            raise Exception(f"Distribution {distr} exceed 1.")

        total = sum(distr.values())
        if total < 1:
            distr[self.current_action] = 1 - total
        
        for name, prob in distr.items():
            random_val -= prob
            if random_val <= 0:
                return name

    def do(self):
        candidate_actions = self.actions[self.current_action](self)
        
        prob_distr = self.prob[self.current_action](self)
        
        self.current_action = self.sample(prob_distr)

def do_nothing(something):
    something.check = 'doing nothing'
    return ['say_hello']

def say_hello(something):
    something.check = 'hello world!'
    return ['do_nothing']

def prob_nothing(someting):
    return {'say_hello': 1}

def prob_hello(something):
    return {'do_nothing': 1}

tmp = FMS({'do_nothing': do_nothing, 'say_hello': say_hello}, {'do_nothing': prob_nothing, 'say_hello': prob_hello}, 'do_nothing')
tmp.do()
print(tmp.check)
tmp.do()
print(tmp.check)
