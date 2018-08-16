from . import verify, quiz, gui
from .quizs import quizs
from browser.local_storage import storage 
from browser import document, window, timer
import html
import json
import sys
#import re
import asyncio
old_stdout = sys.stdout
console_div = document["console"]

class State:
    def __init__(self):
        super().__setattr__('_st', storage)

    def set(self, name, value):
        self._st[name] = json.dumps(value)

    def get(self, name, default=None):
        ret = self._st.get(name)
        if ret is None:
            return default
        return json.loads(ret)

    def __getattr__(self, name):
        if name == 'level':
            return self.get(name, 0)
        elif name in ():
            return self.get(name)
        else:
            super().__getattr__(self, name)

    def __setattr__(self, name, value):
        self.set(name, value)
        
st = State()

editor = None
current_level = -1


def escape(s, quote=True):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace('\'', "&#x27;")
    return s


def init(e):
    global editor
    editor = e
    print('Welcome to Pycon 2018')
    set_level(st.level)
    document['submit_code'].bind('click', lambda *args:do_submit())
    document['test_play'].bind('click', lambda *args:do_test())
    document['prev_level'].bind('click', lambda *args:set_level(current_level-1))
    document['next_level'].bind('click', lambda *args:set_level(current_level+1))

gui_env = {
    "say":gui.say,
    "select":gui.select,
    "_input":gui.input,
}

verify_env = {
    "say":verify.say,
    "select":verify.select,
    "_input":verify.input,
}

def step_for_level(current_level):
    # default: 1
    return 1

#def modify_code_for_run(code):
    #cs = []
    #base = 0
    #for m in re.finditer(r'\bsay\b|\bselect\b', code):
        #p = m.span()[0] - base
        #cs.append(code[:p])
        #code = code[p:]
        #base = m.span()[0]
    #cs.append(code)
    #code = 'yield '.join(cs)
    #ret = ('import asyncio\n@asyncio.coroutine\ndef run():\n'+'\n'.join('   '+x for x in code.split('\n')) +'\nasyncio.ensure_future(run())')
    ##print('*'*30)
    #print(ret)
    #print('='*30)
    #print(cs)
    #print('-'*30)
    #return ret

def run_gui(code):
    try:
        exec(code, gui_env.copy())
    except:
        pass
    #while not c_f.done():
        #asyncio.sleep(0.1)

def run_verify(code):
    try:
        exec(code, verify_env.copy(), genv)
    except:
        pass

def do_test(index = 0):
    code_prefix = "input = _input\n";
    code_postfix = "";
    code = editor.getValue()
    q = quizs[current_level]
    st.set(f'code{current_level}', code)
    gui.start(True, str(q.examples[0]) if q.examples else "")
    run_gui(code_prefix+code)
def do_submit():
    code_prefix = "input = _input\n";
    code_postfix = "";
    code = editor.getValue()
    q = quizs[current_level]
    st.set(f'code{current_level}', code)
    pass_this_time = True
    examples = q.examples
    if not examples:
        examples = [quiz.Example("")]
    for idx,e in enumerate(examples):
        verify.start(script=str(e))
        run_verify(code_prefix+code)
        res = verify.result()
        verify.start(script=str(e))
        run_verify(code_prefix+q.goal.goal)
        goal = verify.result()
        if goal == res:
            print(f'예제 {idx+1} 통과' )
        else:
            print(f'예제 {idx+1} 실패' )
        pass_this_time = pass_this_time and goal == res
    level = st.level
    if pass_this_time:
        if level <= current_level:
            st.level = current_level+step_for_level(current_level)
        print('통과하여 다음레벨로 진행할 수 있습니다!')
        document['tutstatus'].classList.remove('notpassed')
        document['tutstatus'].classList.add('passed')
        gui.show_pass()
    else:
        print('통과하지 못했습니다.')
        if current_level >= level:
            document['tutstatus'].classList.add('notpassed')
        gui.show_fail(q.hint)


def set_quiz(level):
    global current_level
    current_level = level
    q = quizs[level]
    editor.setValue(st.get(f'code{level}', ''))
    document['tutname'].text = q.title
    document['tutstatus'].classList.remove('passed', 'notpassed')
    if level < st.level:
        document['tutstatus'].classList.add('passed')

    document['tutdesc'].html = '<code>'.join('</code>'.join(escape(x) for x in y.split('</code>')) for y in q.desc.split('<code>'))

    if q.examples:
        document['tutexamples'].html = '<hr>'.join(f"<strong>입력 {idx+1}</strong><BR>"+str(x) for idx, x in enumerate(q.examples))
    else:
        document['tutexamples'].html = '<em>(예제 없음)</em>'
    gui.close()

def set_level(level):
    try:
        level = int(level)
    except:
        level = 0
    if level < 0:
        level = 0
    if level >= len(quizs):
        level = len(quizs)-1
    if not document["dev_check"].checked and level > st.level:
        level = st.level
    #if level >= 0 and level < len(quizs) and level <= st.level:
    set_quiz(level)
