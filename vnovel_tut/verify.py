commands = []
scripts = []
def start(script):
    global commands, scripts
    commands = []
    scripts = [x.strip() for x in script.strip().split('\n') if x.strip()]

def say(who, msg):
    commands.append(['Say', who, msg])

first_loop = False
select_vars = []
select_idx = 0

def decrease_select_var():
    if not select_vars:
        return False
    select_vars[-1] -= 1
    if select_vars[-1] < 0:
        select_vars.pop()
        return decrease_select_var()
    return True

def select(*args):
    global select_vars, select_idx
    if len(select_vars) > select_idx:
        ret = len(args)-1-select_vars[select_idx]
    else:
        assert len(select_vars) == select_idx
        select_vars.append(len(args)-1)
        ret = 0
    select_idx += 1
    return ret

def result():
    return commands


def branch():
    commands.append('Branch')

def run(code, script=''):
    global first_loop, select_idx
    env = dict(say=say, select=select)
    start(script)

    first_loop = True
    while True:
        select_idx = 0
        try:
            exec(code, env, globals().copy())
        except EOFError:
            pass
        if not decrease_select_var():
            break

        branch()
    return result()

def input():
    if not scripts:
        raise EOFError
    ret = scripts[0]
    scripts.pop(0)
    return ret
