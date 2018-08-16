from .quizs import quizs
from .quiz import Example
from . import gui, verify
from urllib.request import urlopen

try:
    # Python 3
    import tkinter
    from tkinter import font, ttk, scrolledtext, _tkinter, messagebox

except ImportError:
    # Python 2
    import Tkinter as tkinter
    from Tkinter import ttk
    import tkFont as font
    import ScrolledText as scrolledtext

need_better_version = False
import sys
if sys.version_info < (3,0):
    need_better_version = True
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name

import json
from collections import defaultdict

console = None
class YameFile:
    def __init__(self,old):
        self.old = old
    def write(self, s):
        self.old.write(s)
        if console:
            console.insert(tkinter.END, s)
    def flush(self):
        self.old.flush()

sys.stdout = YameFile(sys.stdout)
sys.stderr = YameFile(sys.stderr)

db = defaultdict(int)
try:
    db.update(json.load(open('progress')))
except:
    pass

def save():
    json.dump(db, open('progress', 'w'))

class Window:
    def __init__(self, master):
        self.master = master
        self.master.title('프로그래밍 언어 만들기')
        self.master.config(bg='#fff')
        self.master.geometry('1024x768')
        self.lexer = PythonLexer(stripnl = False)
        self.AddWidgets()
        self.create_tags()

        self.current_level = db.get('level',0)
        self.set_level(self.current_level)

    def set_level(self, level):
        try:
            level = int(level)
        except:
            level = 0
        if level < 0:
            level = 0
        if level >= len(quizs):
            level = len(quizs)-1
        #if not ? and level > 
        self.set_quiz(level)

    def set_quiz(self, level):
        self.current_level = level
        q = quizs[level]
        self.title_var.set("언어 만들기 - " + q.title)
        self.text.delete("1.0", tkinter.END)
        self.text.insert(tkinter.END, db.setdefault('code'+str(level), ''))
        self.recolorize()
        if db['pass'+str(self.current_level)]:
            self.tutstatus.config(text='통과',fg='#adff2f')
        else:
            self.tutstatus.config(text='')

        self.desc.config(state=tkinter.NORMAL)
        self.desc.delete("1.0", tkinter.END)
        self.desc.insert(tkinter.END, '목표\n'+q.desc.replace('<code>','').replace('</code>',''))
                #''.join(''.join(escape(x) for x in y.split('</code>')) for y in q.desc.split('<code>')))
        self.desc.tag_add("BigTitle", "1.0", "2.0")
        self.desc.config(state=tkinter.DISABLED)

        self.examples.config(state=tkinter.NORMAL)
        self.examples.delete("1.0", tkinter.END)
        self.examples.insert(tkinter.END, '예제\n')
        self.examples.tag_add("BigTitle", "1.0", "2.0")
        if q.examples:
            self.examples.insert(tkinter.END, '   -----   \n'.join("입력 "+str(idx+1)+"\n"+x.generate_output() for idx, x in enumerate(q.examples)))
        else:
            self.examples.insert(tkinter.END, '(예제 없음)')
        self.examples.config(state=tkinter.DISABLED)

    def select_all(self, *args):
        self.text.tag_add("sel","1.0","end")
    def AddWidgets(self):
        global console
        self.master.configure(bg='white')
        self.master.grid_columnconfigure(0, weight = 1, uniform = 2)
        self.master.grid_columnconfigure(1, weight = 1, uniform = 2)
        self.master.grid_rowconfigure(0, minsize=50)
        self.master.grid_rowconfigure(1, weight = 1, uniform = 1)
        self.master.grid_rowconfigure(2, weight = 1, uniform = 1)
        self.master.grid_rowconfigure(3, weight = 1, uniform = 1)
        self.master.grid_rowconfigure(4, weight = 1, uniform = 1)

        console = scrolledtext.ScrolledText(master= self.master,
                )
        self.text = scrolledtext.ScrolledText(master=self.master, 
                bg='#272822',
                undo=True,
                exportselection=True,
                cursor='xterm',
                selectbackground='#ddd',
                insertbackground='#fff',
                insertwidth='3',
                )#, **self.uiopts)
        self.text.grid(column = 1, row = 1, rowspan=3, sticky = ('nsew'))
        console.grid(column = 1, row = 4, rowspan = 1,sticky = ('nsew'))

        for command, key in ('Copy', 'c'), ('Paste', 'v'), ('Cut', 'x'):
            self.text.event_add('<<'+command+'>>', '<Command-'+key+'>')
            self.text.event_add('<<'+command+'>>', '<Command-'+key.upper()+'>')
            self.text.event_add('<<'+command+'>>', '<Control-'+key+'>')
            self.text.event_add('<<'+command+'>>', '<Control-'+key.upper()+'>')
        self.text.bind("<Command-a>", self.select_all)
        self.text.bind("<Command-A>", self.select_all)
        self.text.bind("<Control-a>", self.select_all)
        self.text.bind("<Control-A>", self.select_all)

        self.desc = scrolledtext.ScrolledText(self.master
                #,highlightbackground="#7c7cfa", highlightcolor="#7c7cfa", highlightthickness=1, spacing1 = 5, spacing3 = 5, bg='#ddd'
                )
        self.desc.grid(column=0,row=1,rowspan=2,sticky=('nsew'),padx=5, pady=5)
        self.desc.bind("<1>", lambda event: self.desc.focus_set())

        self.examples = scrolledtext.ScrolledText( self.master,
                #highlightbackground="#7c7cfa", highlightcolor="#7c7cfa", highlightthickness=1, spacing1 = 5, spacing3 = 5, bg='#eee'
                )
        self.examples.grid(column=0,row=3,rowspan=2,sticky=('nsew'),padx=5,pady=5)
        self.examples.bind("<1>", lambda event: self.examples.focus_set())

        self.navbar = tkinter.Frame(self.master,height=50,bg='#7c7cfa',
                #highlightbackground="red", highlightcolor="red", highlightthickness=1
                )
        self.title_var = tkinter.StringVar()
        self.title1 = tkinter.Label(self.navbar, textvariable = self.title_var, bg='#7c7cfa',fg='white')
        self.title1.configure(font=('monaco', 27))
        self.title_var.set("언어 만들기 - ")
        self.title1.pack(side=tkinter.LEFT,padx=5)

        right_btn = tkinter.Button(self.navbar, text='→',highlightbackground='#7c7cfa',highlightcolor='#7c7cfa')
        right_btn.pack(side=tkinter.RIGHT)
        right_btn.configure(command = lambda: self.set_level(self.current_level+1))
        submit_btn = tkinter.Button(self.navbar, text="제출",highlightbackground='#7c7cfa',highlightcolor='#7c7cfa')
        submit_btn.pack(side=tkinter.RIGHT)
        submit_btn.configure(command = lambda: self.do_submit() )

        test_btn = tkinter.Button(self.navbar, text="테스트",highlightbackground='#7c7cfa',highlightcolor='#7c7cfa')
        test_btn.pack(side=tkinter.RIGHT)
        test_btn.configure(command = lambda: self.do_test() )

        left_btn = tkinter.Button(self.navbar, text='←',highlightbackground='#7c7cfa',highlightcolor='#7c7cfa')
        left_btn.pack(side=tkinter.RIGHT)
        left_btn.configure(command = lambda: self.set_level(self.current_level-1) )

        self.tutstatus = tkinter.Label(self.navbar, text='', fg='#adff2f', bg='#7c7cfa')
        self.tutstatus.pack(side=tkinter.RIGHT)
        self.tutstatus.configure(font=('monaco', 27))

        self.navbar.grid(column=0,row=0,columnspan=2,sticky = tkinter.W+tkinter.E+tkinter.N+tkinter.S)

        #self.examples.insert(tkinter.INSERT,'abc\n'*100)
        #self.desc.insert(tkinter.INSERT,'desc')
        #self.text.insert(tkinter.INSERT, 'code')
        # NORMAL

        self.examples.configure(font=('monaco', 14))
        self.desc.configure(font=('monaco', 14))
        self.text.configure(font=('monaco', 16))

        self.desc.config(state=tkinter.DISABLED)
        self.examples.config(state=tkinter.DISABLED)


        self.text.bind("<BackSpace>", self.do_backspace)

        self.master.bind('<Key>', self.event_key)
        self.text.bind('<Return>', self.autoindent)
        self.text.bind('<Tab>', self.tab2spaces4)
        self.recolorize()


    def do_backspace(self, event):
        lineindex, columnindex = self.text.index("insert").split(".")
        linetext = self.text.get(lineindex+".0", self.text.index('insert'))
        if int(columnindex) > 0 and all(x==' ' for x in linetext):
            self.text.delete("insert-%d chars" % min(int(columnindex), 4), "insert")
            return 'break'

    def autoindent(self, event):
        indentation = ""
        lineindex = self.text.index("insert").split(".")[0]
        linetext = self.text.get(lineindex+".0", lineindex+".end")

        for character in linetext:
            if character in [" ","\t"]:
                indentation += character
            else:
                break
                
        self.text.insert(self.text.index("insert"), "\n"+indentation)
        return "break"

    def tab2spaces4(self, event):
        #idx = self.text.index("insert")
        self.text.insert(self.text.index("insert"), "    ")
        return "break"

            #self.text.insert(tkinter.INSERT, text)
            #self.text.tag_remove(tkinter.SEL, '1.0', tkinter.END)
            #self.text.see(tkinter.INSERT)
    def event_key(self, event):
        keycode = event.keycode
        char = event.char
        self.recolorize()
        self.master.update()

    def event_mouse(self, event):
        pass
    
    def close(self):
        self.master.destroy()

    def recolorize(self):
        code = self.text.get("1.0", "end-1c")
        tokensource = self.lexer.get_tokens(code)
        start_line=1
        start_index = 0
        end_line=1
        end_index = 0
        
        for ttype, value in tokensource:
            if "\n" in value:
                end_line += value.count("\n")
                end_index = len(value.rsplit("\n",1)[1])
            else:
                end_index += len(value)
 
            if value not in (" ", "\n"):
                index1 = "%s.%s" % (start_line, start_index)
                index2 = "%s.%s" % (end_line, end_index)
 
                for tagname in self.text.tag_names(index1): 
                    if tagname == 'sel':
                        continue
                    self.text.tag_remove(tagname, index1, index2)
 
                self.text.tag_add(str(ttype), index1, index2)
 
            start_line = end_line
            start_index = end_index

    def do_test(self):
        code = self.text.get("1.0", "end")
        q = quizs[self.current_level]
        db['code'+str(self.current_level)] = code.rstrip('\n')
        save()
        examples = q.examples
        if not examples:
            examples = [Example("")]
        gui.run(code, self.master, str(examples[0]))

    def show_pass(self):
        messagebox.showinfo("성공", "통과하였습니다! 다음 레벨로 진행합니다.")
        self.set_level(self.current_level+1)

    def show_fail(self, hint):
        messagebox.showerror("실패", "실패하였습니다. 힌트를 참고하여 다시 작성해 보세요.\n\n"+hint)

    def do_submit(self):
        code = self.text.get("1.0", "end")
        q = quizs[self.current_level]
        db['code%s'%self.current_level] = code.rstrip('\n')
        pass_this_time = True
        examples = q.examples
        if not examples:
            examples = [Example("")]
        for idx,e in enumerate(examples):
            has_exception = False
            goal_has_exception = False
            my_exc = None
            goal_exc = None
            try:
                res = verify.run(code, str(e))
            except Exception as e:
                has_exception = True
                my_exc = e

            try:
                goal = verify.run(q.goal.goal, str(e))
            except Exception as e:
                goal_has_exception = True
                goal_exc = None
            if goal == res or goal_has_exception and has_exception and type(my_exc) is type(goal_exc):
                print('예제 %s 통과'%(idx+1) )
            else:
                print('예제 %s 실패'%(idx+1) )
                pass_this_time = False
        level = db.setdefault('level', 0)
        if pass_this_time:
            if level <= self.current_level:
                db['level'] = self.current_level+1
            print('통과했습니다!')
            self.tutstatus.config(text='통과',fg='#adff2f')
            if not db.setdefault('pass'+str(self.current_level), 0):
                db['pass'+str(self.current_level)] = 1
                res = urlopen('http://ipkn.me:4949/pass/'+str(self.current_level)).read()

            self.show_pass()
        else:
            print('통과하지 못했습니다.')
            if not db['pass'+str(self.current_level)]:
                self.tutstatus.config(text='실패',fg='#ff2f1f')
                res = urlopen('http://ipkn.me:4949/fail/'+str(self.current_level)).read()
            k = 'fail' + str(self.current_level)
            db[k] = db.get(k,0) + 1
            self.show_fail(q.hint.generate(db[k]))
        save()

    def create_tags(self):
        bold_font = font.Font(self.text, self.text.cget("font"))
        bold_font.configure(weight=font.BOLD)
        italic_font = font.Font(self.text, self.text.cget("font"))
        italic_font.configure(slant=font.ITALIC)
        bold_italic_font = font.Font(self.text, self.text.cget("font"))
        bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)
        style = get_style_by_name('monokai')
        self.desc.tag_configure('BigTitle', font=('monaca', 23))
        self.examples.tag_configure('BigTitle', font=('monaca', 23))
        
        for ttype, ndef in style:
            tag_font = None
        
            if ndef['bold'] and ndef['italic']:
                tag_font = bold_italic_font
            elif ndef['bold']:
                tag_font = bold_font
            elif ndef['italic']:
                tag_font = italic_font
 
            if ndef['color']:
                foreground = "#%s" % ndef['color'] 
            else:
                foreground = None
 
            self.text.tag_configure(str(ttype), foreground=foreground, font=tag_font) 



app = tkinter.Tk()
win = Window(app)
app.mainloop()
