"""Inspectable feedback drafts: no network requests and no automatic submission."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from .feedback import CATEGORIES, diagnostics, compose_report, save_zip, email_url, github_url


class FeedbackDialog:
    def __init__(self,app):
        self.app=app
        self.win=tk.Toplevel(app.root)
        self.win.title('Report a Bug / Send Feedback')
        self.win.geometry('860x740')
        self.win.minsize(620,520)
        self.footer=ttk.Frame(self.win)
        self.footer.pack(side='bottom',fill='x')
        viewport=ttk.Frame(self.win)
        viewport.pack(fill='both',expand=True)
        self.content=app._scroll_panel(viewport)
        self.category=tk.StringVar(self.win,value=CATEGORIES[0])
        self.contact=tk.StringVar(self.win)
        self.reviewed=tk.BooleanVar(self.win,value=False)
        top=ttk.Frame(self.content,padding=12)
        top.pack(fill='x')
        ttk.Label(top,text='Feedback category').grid(row=0,column=0,sticky='w')
        ttk.Combobox(top,textvariable=self.category,values=CATEGORIES,state='readonly',width=32).grid(row=0,column=1,sticky='ew')
        ttk.Label(top,text='Your email (optional)').grid(row=1,column=0,sticky='w',pady=5)
        ttk.Entry(top,textvariable=self.contact).grid(row=1,column=1,sticky='ew')
        top.columnconfigure(1,weight=1)
        ttk.Label(top,text='No account is needed. Nothing is sent automatically. Your typed feedback and optional email will be included; review them before sharing.',wraplength=780).grid(row=2,column=0,columnspan=2,sticky='w',pady=6)
        self.description=self.text_field('Description',3)
        self.steps=self.text_field('Reproduction steps (optional)',2)
        ttk.Button(self.content,text='Update report preview',command=self.refresh).pack(anchor='w',padx=12,pady=5)
        self.preview=self.text_field('Report preview — editable; this exact text is copied, saved or placed in a draft',10,expand=True)
        ttk.Checkbutton(self.footer,text='I have inspected this report and intend to share its contents.',variable=self.reviewed).pack(anchor='w',padx=12,pady=5)
        actions=ttk.Frame(self.footer,padding=12)
        actions.pack(fill='x')
        for col,(name,command) in enumerate((('Copy Diagnostic Report',self.copy),('Save Diagnostic ZIP',self.save),
            ('Send Feedback by Email',self.email),('Report on GitHub',self.github))):
            ttk.Button(actions,text=name,command=command).grid(row=col//2,column=col%2,sticky='ew',padx=3,pady=3)
        actions.columnconfigure((0,1),weight=1)
        self.status=tk.StringVar(self.win,value='Attach a saved diagnostic ZIP manually in your mail app. No experimental files are included.')
        status_label=ttk.Label(self.footer,textvariable=self.status,wraplength=780,padding=12)
        status_label.pack(fill='x')
        self.footer.bind('<Configure>',lambda e:status_label.configure(wraplength=max(200,e.width-30)))
        self.content.bind('<Configure>',self.reflow,add='+')
        for variable in (self.category,self.contact):
            variable.trace_add('write',lambda *_:self.invalidate())
        for widget in (self.description,self.steps):
            widget.bind('<<Modified>>',lambda event:self.modified(event))
        self.refresh()

    def text_field(self,label,height,expand=False):
        ttk.Label(self.content,text=label,padding=(12,2)).pack(anchor='w')
        frame=ttk.Frame(self.content)
        frame.pack(fill='both' if expand else 'x',expand=expand,padx=12)
        text=tk.Text(frame,height=height,wrap='word',font=('Segoe UI',10))
        scroll=ttk.Scrollbar(frame,command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side='left',fill='both',expand=True)
        scroll.pack(side='right',fill='y')
        return text

    def reflow(self,event):
        def labels(parent):
            for child in parent.winfo_children():
                if isinstance(child,ttk.Label):
                    child.configure(wraplength=max(180,event.width-50))
                labels(child)
        labels(self.content)

    def invalidate(self):
        self.fields_dirty=True
        self.reviewed.set(False)
        self.status.set('Feedback fields changed. Update the report preview, then inspect it before sharing.')

    def modified(self,event):
        if event.widget.edit_modified():
            self.invalidate()
            event.widget.edit_modified(False)

    def guard(self,action):
        try:
            return action()
        except ValueError as exc:
            self.status.set(str(exc))
            return None
        except Exception:
            self.status.set('This feedback action could not be completed. Your text is still available; copy it manually or try another action.')
            return None

    def refresh(self):
        def update():
            try:
                data=diagnostics(self.app)
            except Exception:
                data={'diagnostics':'Unavailable; manual feedback remains usable.'}
            text=compose_report(self.category.get(),self.description.get('1.0','end'),self.steps.get('1.0','end'),self.contact.get(),data)
            self.preview.delete('1.0','end')
            self.preview.insert('end',text)
            self.description.edit_modified(False)
            self.steps.edit_modified(False)
            self.fields_dirty=False
            self.reviewed.set(False)
            self.status.set('Inspect and edit the preview below. Only this text is included; no files are attached.')
        return self.guard(update)

    def report(self):
        if self.fields_dirty:
            raise ValueError('Feedback fields changed. Click Update report preview before copying, saving or opening a draft.')
        return self.preview.get('1.0','end-1c')

    def copy(self):
        def action():
            report=self.report()
            self.win.clipboard_clear()
            self.win.clipboard_append(report)
            self.status.set('Report copied. Paste it into an email or message after reviewing it.')
        return self.guard(action)

    def save(self):
        def action():
            path=filedialog.asksaveasfilename(parent=self.win,title='Save reviewed diagnostic report',defaultextension='.zip',initialfile='tpd-feedback.zip',filetypes=[('Diagnostic ZIP','*.zip')])
            if path:
                save_zip(path,self.report())
                self.status.set('Diagnostic ZIP saved. Review it, then attach it manually to your email; no files were sent.')
        return self.guard(action)

    def share(self,kind):
        def action():
            if not self.reviewed.get():
                self.status.set('Inspect the preview and check the review box before opening a draft.')
                return
            report=self.report()
            url=(email_url if kind=='email' else github_url)(report)
            if len(url)>7500:
                self.copy()
                url=(email_url if kind=='email' else github_url)('The reviewed report is on my clipboard. I will paste it here and optionally attach my diagnostic ZIP.')
                instruction='The report is long: paste the copied report into the draft. '
            else:
                instruction=''
            if not webbrowser.open(url):
                self.status.set('Could not open a default app. Use Copy Diagnostic Report or Save Diagnostic ZIP and email karol.j.cieslik@gmail.com.')
                return
            self.status.set(instruction+('Mail draft opened; attach the ZIP manually if wanted. You decide whether to send it.' if kind=='email' else 'GitHub draft opened. Issues are public; review before submitting.'))
        return self.guard(action)

    def email(self):
        return self.share('email')

    def github(self):
        return self.share('github')


def open_feedback(app):
    try:
        dialog=FeedbackDialog(app)
        return dialog
    except Exception:
        try:
            messagebox.showerror('Feedback unavailable','Please email karol.j.cieslik@gmail.com. Include the version from About and a short description. No files have been sent.',parent=app.root)
        except Exception:
            pass
