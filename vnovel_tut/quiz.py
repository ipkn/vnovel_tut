import random

class Hint:
    def __init__(self, *args):
        self.hints = args

    def generate(self, idx):
        return '\n'.join('힌트%d: %s' % (i+1, v) for i, v in enumerate(self.hints[:idx]))

class Any:
    def __init__(self, *candidates):
        self.candidates = candidates
    def __str__(self):
        return ''.join(random.choice(c) for c in self.candidates)

class Example:
    def __init__(self, script, shadow = False):
        self.script = script
        self.shadow = shadow

    def generate_output(self):
        if self.shadow:
            return "(숨겨진 입력)"
        return self.script

    def __str__(self):
        return str(self.script)

class Goal:
    def __init__(self, goal):
        self.goal = goal

class Quiz:
    def __init__(self, *, title, desc, examples, goal, hint = Hint()):
        self.title = title
        self.desc = desc
        self.examples = examples
        self.goal = goal
        self.hint = hint

if __name__ == '__main__':
    print(str(Any('123456789','+*','123456789')))
