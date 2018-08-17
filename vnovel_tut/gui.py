DEBUG = 1
import threading
import ctypes
import time
import queue
try:
    # Python 3
    import tkinter
    from tkinter import font, ttk, _tkinter, messagebox

except ImportError:
    # Python 2
    import Tkinter as tkinter
    from Tkinter import ttk
    import tkFont as font

should_close = False
msg_q = queue.Queue()
def answer(x):
    pass
def dispatch(f):
    ev = threading.Event()
    def work():
        f()
        ev.set()
    msg_q.put(work)
    while not ev.is_set():
        ev.wait(0.05)
        if should_close:
            break

def post(f):
    msg_q.put(f)

cv = threading.Condition()

CHAR_DELAY = 0.055
scripts = []
master = None
def start(m, script = ""):
    global scripts, master
    master = m
    scripts = [x for x in script.split('\n') if x.strip()]

msgbox = None
namebox = None
def textbox(x,y,w,h,who,msg):
    global msgbox, namebox, msgbox_var, namebox_var, frame
    x/=100
    y/=100
    w/=100
    h/=100
    try:
        frame
    except:
        return
    def initboxes():
        global msgbox, namebox, msgbox_var, namebox_var, frame
        if msgbox:
            msgbox_var.set('')
        else:
            msgbox_var = tkinter.StringVar()
            msgbox = tkinter.Label(frame, textvariable = msgbox_var, font=('monaca',15), fg='white', padx=15,pady=15, anchor = tkinter.NW, justify = tkinter.LEFT,bg='#000064', bd=0, highlightcolor='white', highlightbackground='white', highlightthickness='3', )
            msgbox.place(relx = x, rely = y, relw = w, relh = h, anchor=tkinter.NW)
            msgbox.bindtags((frame,) + msgbox.bindtags())
        if namebox:
            pass
        else:
            namebox_var = tkinter.StringVar()
            namebox = tkinter.Label(frame, textvariable = namebox_var, font=('monaca',15), fg='white',  bg='#000064', bd=0, highlightcolor='white', highlightbackground='white', highlightthickness='3', padx=5, pady=5)
            namebox.place(relx = x, rely = y, anchor = tkinter.SW)
            namebox.bindtags((frame,) + namebox.bindtags())
            namebox_var.set(str(who))
        namebox_var.set(who)
    dispatch(initboxes)

    reset_key()
    for idx, ch in enumerate(msg):
        post(lambda idx=idx: msgbox_var.set(msg[:idx+1]))
        wait_key(CHAR_DELAY, False)
        
    wait_key()

key_pressed = False
def reset_key():
    global key_pressed
    key_pressed = False

def wait_until(cond, timeout = None):
    cv.acquire()
    if timeout is None:
        while not should_close and not cond():
            cv.wait(0.1)
    else:
        cv.wait(timeout)
    cv.release()

def wait_key(timeout = None, reset = True):
    if reset:
        reset_key()
    if key_pressed:
        return
    cv.acquire()
    if timeout is None:
        while not should_close and not key_pressed:
            cv.wait(0.1)
    else:
        cv.wait(timeout)
    cv.release()

def event_input(*args):
    global key_pressed
    key_pressed = True
    cv.acquire()
    cv.notify()
    cv.release()
    

def say(who, msg):
    textbox(10,70,80,20,who,msg)

def select(*args):
    args = [str(x) for x in args]
    global msgbox, namebox, sel_frame, sel_result
    if not frame:
        return
    if msgbox:
        msgbox.destroy()
        msgbox = None
    if namebox:
        namebox.destroy()
        namebox = None

    sel_result = None
    def initboxes():
        global sel_frame
        N = len(args)
        CN = (N+4)//5 # 1~5: 1, 6~10: 2
        RN = min(N, 5) # 1~5: N, else: 5
        sel_frame = tkinter.Frame(frame, bg='#000064')
        if CN == 1:
            sel_frame.place(relwidth=0.3, relheight=0.18*RN, relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        elif CN == 2:
            sel_frame.place(relwidth=0.6, relheight=0.9, relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        else:
            sel_frame.place(relwidth=0.9, relheight=0.9, relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        click_label.configure(fg='#000064')
        for x in range(CN):
            for y in range(RN):
                idx = y+x*5
                btn = tkinter.Frame(sel_frame, bg='#000064', bd=0, highlightcolor='white', highlightbackground='white', highlightthickness='3')
                btn.place(relwidth = 0.9/CN, relheight = 0.9/RN, relx = (x+0.5)/CN, rely = (y+0.5)/RN, anchor = tkinter.CENTER)

                lbl = tkinter.Label(btn, bg='#000064', text=args[idx], font = ('monaca', 23), fg='white')
                lbl.place(relx = 0.5, rely = 0.5, anchor = tkinter.CENTER)
                lbl.bindtags((btn,)+lbl.bindtags())

                def hover(e, btn=btn, lbl=lbl):
                    btn.configure(bg='white')
                    lbl.configure(fg='#000064',bg='white')

                def leave(e, btn=btn, lbl=lbl):
                    btn.configure(bg='#000064')
                    lbl.configure(fg='white',bg='#000064')

                def do_select(e, idx=idx):
                    global sel_result
                    sel_result = idx
                    cv.acquire()
                    cv.notify()
                    cv.release()

                btn.bind('<Button>',do_select)
                btn.bind('<Enter>', hover)
                btn.bind('<Leave>', leave)
                #btn.grid(column = x, row = y, sticky =tkinter.N+tkinter.E+tkinter.W+tkinter.S, padx=5,pady=5)
    dispatch(initboxes)
    wait_until(lambda : sel_result is not None)
    def cleanup():
        global sel_frame
        sel_frame.destroy()
        sel_frame = None
        click_label.configure(fg='white')
    post(cleanup)
    return sel_result

def input():
    if not scripts:
        raise EOFError
    ret = scripts[0]
    scripts.pop(0)
    return ret

env = dict(say = say, select = select, input=input, answer=answer)
frame = None
subthread = None

def ctype_async_raise(thread_obj, exception):
    found = False
    target_tid = 0
    for tid, tobj in threading._active.items():
        if tobj is thread_obj:
            found = True
            target_tid = tid
            break

    if not found:
        raise ValueError("Invalid thread object")

    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), ctypes.py_object(exception))
    # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    if ret == 0:
        raise ValueError("Invalid thread ID")
    elif ret > 1:
        # Huh? Why would we notify more than one threads?
        # Because we punch a hole into C level interpreter.
        # So it is better to clean up the mess.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def close():
    global frame, subthread, should_close
    should_close = True
    if subthread:
        t = subthread
        ctype_async_raise(t, SystemExit)
        try:
            cv.release()
        except:
            pass
        time.sleep(0.1)
        #t.join()
        subthread = None
    if frame:
        frame.destroy()
        frame = None

def mt_helper():
    done = False
    while not msg_q.empty() and not should_close:
        x = msg_q.get()
        if x == 'done':
            done = True
            break
        else:
            x()

    if not done and not should_close:
        master.after(50, mt_helper)

def run(code, m, script):
    global frame, subthread, master, should_close, click_label
    should_close = False
    master = m
    while True:
        try:
            msg_q.get_nowait()
        except:
            break
    def internal_run():
        global subthread
        try:
            exec(code, env)
        except:
            pass
        finally:
            msg_q.put('done')
            subthread = None
    subthread = threading.Thread(target=internal_run)
    subthread.start()
    start(master, script)

    bounds = master.bbox()
    frame = tkinter.Frame(master, bg='#000064', bd=0, highlightcolor='white', highlightbackground='white', highlightthickness='3', )
    frame.place(relwidth=0.8, relheight=0.8, relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    exit_button = tkinter.Button(frame, text='닫기', command=close)
    exit_button.place(relx=1,rely=0,anchor=tkinter.NE)

    click_label = tkinter.Label(frame, text="click to continue ...", bg='#000064', fg='white')
    click_label.pack(side="bottom", fill="x", pady=10)

    click_label.bindtags((frame,) + click_label.bindtags())
    frame.bind('<Button>', event_input)
    frame.bind('<Key>', event_input)
    mt_helper()
