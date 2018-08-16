script_lang = '''\
indents = []
def 명령들(s):
    cmds = []
    while 1:
        try:
            cmd, s = 대사(s)
            cmds.append(cmd)
            continue
        except:
            pass
        try:
            cmd, s = if문(s)
            cmds.append(cmd)
            continue
        except:
            pass
        try:
            cmd, s = 선택지(s)
            cmds.append(cmd)
            continue
        except:
            pass
        break
    return cmds, s

def 공백(s):
    for idx, c in enumerate(s):
        if not c in ' \t':
            return s[:idx], s[idx:]
    return s, ''

def 글(sub, s):
    if s.startswith(sub):
        return s[len(sub):]
    raise SyntaxError

def 글자(ch, s):
    if s[0] == ch:
        return s[1:]
    raise SyntaxError

def 문자열(s):
    s = 글자('"', s)
    if s.find('"') == -1:
        raise SyntaxError
    idx = s.find('"')
    msg = s[:idx]
    s = s[idx:]
    s = 글자('"', s)
    return msg, s

def 누구(s):
    idx = 0
    ch = s[idx]
    while '0' <= ch <= '9' or 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '가' <= ch <= '힣' or ch == '_':
        idx += 1
        ch = s[idx]
    return s[:idx], s[idx:]
    
def 대사(s):
    who, s = 누구(s)
    _, s = 공백(s)
    s = 글자(":", s)
    _, s = 공백(s)
    msg, s = 문자열(s)
    _, s = 공백(s)
    s = 줄바꿈(s)
    return ('say', who, msg), s

def 들여쓰기(s):
    cnt = indents[-1]
    s = 글('\n'+' '*cnt, s)
    ws, s = 공백(s)
    indents.append(cnt + len(ws))
    return s

def 줄바꿈(s):
    cnt = indents[-1]
    s = 글자('\n', s)
    ws, s = 공백(s)
    if len(ws) < cnt:
        while indents and len(ws) != indents[-1]:
            indents.pop()
            s = chr(1) + s
        if not indents:
            raise SyntaxError
    return s

def 내어쓰기(s):
    if s[0] == chr(1):
        return s[1:]
    indents.pop()
    return s

def if문(s):
    s = 글("if",s)
    _, s = 공백(s)
    idx = s.find(':')
    cond = s[:idx].strip()
    s = s[idx+1:]
    _, s = 공백(s)
    s = 들여쓰기(s)
    cmds, s = 명령들(s)
    s = 내어쓰기(s)
    return ('if', cond, cmds), s

def 선택항목(s):
    item, s = 문자열(s)
    _, s = 공백(s)
    s = 글자(":",s)
    s = 들여쓰기(s)
    cmds, s = 명령들(s)
    s = 내어쓰기(s)
    return (item, cmds), s

def 선택지(s):
    s = 글("선택지",s)
    _, s = 공백(s)
    s = 글자(":",s)
    _, s = 공백(s)
    s = 들여쓰기(s)
    picks = []
    while 1:
        try:
            pick, s = 선택항목(s)
            picks.append(pick)
        except:
            break
    s = 내어쓰기(s)
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
    cmds, s = 명령들(s)
    if s:
        raise SyntaxError
    execute(cmds)

allinput = ''
try:
    while 1:
        allinput += input() + '\n'
except EOFError:
    parse(allinput)
'''
expr_lang = '''\
def factor(s):
    print('factor',s)
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
    print('term',s)
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
    print('expr',s)
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

print(parse(input()))
'''
