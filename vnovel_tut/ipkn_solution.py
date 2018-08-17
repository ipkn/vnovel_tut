script_lang = r'''\
indents = []
def stmts_cmd(s):
    cmds = []
    while 1:
        try:
            cmd, s = say_cmd(s)
            cmds.append(cmd)
            continue
        except:
            pass
        try:
            cmd, s = if_cmd(s)
            cmds.append(cmd)
            continue
        except:
            pass
        try:
            cmd, s = select_cmd(s)
            cmds.append(cmd)
            continue
        except:
            pass
        break
    return cmds, s

def white_cmd(s):
    for idx, c in enumerate(s):
        if not c in ' \t':
            return s[:idx], s[idx:]
    return s, ''

def const_str_cmd(sub, s):
    if s.startswith(sub):
        return s[len(sub):]
    raise SyntaxError

def const_char_cmd(ch, s):
    if s[0] == ch:
        return s[1:]
    raise SyntaxError

def str_cmd(s):
    s = const_char_cmd('"', s)
    if s.find('"') == -1:
        raise SyntaxError
    idx = s.find('"')
    msg = s[:idx]
    s = s[idx:]
    s = const_char_cmd('"', s)
    return msg, s

def who_cmd(s):
    idx = 0
    ch = s[idx]
    while '0' <= ch <= '9' or 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '가' <= ch <= '힣' or ch == '_':
        idx += 1
        ch = s[idx]
    return s[:idx], s[idx:]
    
def say_cmd(s):
    who, s = who_cmd(s)
    _, s = white_cmd(s)
    s = const_char_cmd(":", s)
    _, s = white_cmd(s)
    msg, s = str_cmd(s)
    _, s = white_cmd(s)
    s = newline_cmd(s)
    return ('say', who, msg), s

def indent_cmd(s):
    cnt = indents[-1]
    s = const_str_cmd('\n'+' '*cnt, s)
    ws, s = white_cmd(s)
    indents.append(cnt + len(ws))
    return s

def newline_cmd(s):
    if not s:
        return s
    cnt = indents[-1]
    s = const_char_cmd('\n', s)
    ws, s = white_cmd(s)
    if len(ws) < cnt:
        while indents and len(ws) != indents[-1]:
            indents.pop()
            s = chr(1) + s
        if not indents:
            raise SyntaxError
    return s

def dedent_cmd(s):
    if s[0] == chr(1):
        return s[1:]
    indents.pop()
    return s

def if_cmd(s):
    s = const_str_cmd("if",s)
    _, s = white_cmd(s)
    idx = s.find(':')
    cond = s[:idx].strip()
    s = s[idx+1:]
    _, s = white_cmd(s)
    s = indent_cmd(s)
    cmds, s = stmts_cmd(s)
    s = dedent_cmd(s)
    return ('if', cond, cmds), s

def select_item_cmd(s):
    item, s = str_cmd(s)
    _, s = white_cmd(s)
    s = const_char_cmd(":",s)
    s = indent_cmd(s)
    cmds, s = stmts_cmd(s)
    s = dedent_cmd(s)
    return (item, cmds), s

def select_cmd(s):
    s = const_str_cmd("선택지",s)
    _, s = white_cmd(s)
    s = const_char_cmd(":",s)
    _, s = white_cmd(s)
    s = indent_cmd(s)
    picks = []
    while 1:
        try:
            pick, s = select_item_cmd(s)
            picks.append(pick)
        except:
            break
    s = dedent_cmd(s)
    return ('select', picks), s

def execute(cmds):
    for c in cmds:
        if c[0] == 'select':
            items = c[1]
            args = [x[0] for x in items]
            r = select(*args)
            execute(items[r][1])
        elif c[0] == 'say':
            say(c[1], c[2])
        elif c[0] == 'if':
            truth = eval(c[1])
            if truth:
                execute(c[2])

def parse(s):
    global indents
    indents = [0]
    cmds, s = stmts_cmd(s)
    if s:
        raise SyntaxError
    execute(cmds)

allinput = ''
try:
    while 1:
        allinput += input() + '\n'
except EOFError:
    parse(allinput.strip())
'''
expr_lang = '''\
def factor(s):
    if s[0] == '(':
        v, s = expr(s[1:])
        if s[0] != ')':
            raise SyntaxError
        return v, s[1:]

    if '0' <= s[0] <= '9':
        value = int(s[0])
        return value, s[1:]
    raise SyntaxError

def term(s):
    v, s = factor(s)
    while s:
        if s[0] == '*':
            x, s = factor(s[1:])
            v *= x
        elif s[0] == '/':
            x, s = factor(s[1:])
            v /= x
        else:
            break
    return v, s

def expr(s):
    v, s = term(s)
    while s:
        if s[0] == '+':
            x, s = term(s[1:])
            v += x
        elif s[0] == '-':
            x, s = term(s[1:])
            v -= x
        else:
            break
    return v, s

def parse(s):
    v, _ = expr(s)
    return v

answer(parse(input()))
'''
