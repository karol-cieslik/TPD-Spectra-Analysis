"""Project and selected-report actions, separate from scientific computation."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .workflow_io import save_project, load_project
from .workflow_report import export_report
from .run_session import proposed_run_folder


class ProjectMixin:
    def setup_project_actions(self):
        for title,command in (('Open project…',self.open_project),('Save project…',self.save_project),('Report / Export…',self.report_dialog)):
            ttk.Button(self.project_actions,text=title,command=command).pack(side='left',padx=3)

    def save_project(self):
        path=filedialog.asksaveasfilename(parent=self.root,title='Save portable project',defaultextension='.tpd.json',filetypes=[('TPD project','*.tpd.json')])
        if path:
            try:
                save_project(self.project,path)
                self.status.set('Project saved: '+path)
            except (OSError,ValueError,TypeError) as exc:
                messagebox.showerror('Save failed',str(exc),parent=self.root)

    def open_project(self):
        if self.job_busy:
            self.status.set('Finish or cancel the current calculation before opening a project.')
            return
        path=filedialog.askopenfilename(parent=self.root,title='Open portable project',filetypes=[('TPD project','*.tpd.json'),('JSON','*.json')])
        if not path:
            return
        try:
            project=load_project(path)
            if self.project.datasets and not messagebox.askyesno('Replace current workspace?', 'Open this project and replace the current workspace? Save your current project first if you need to retain it.',parent=self.root):
                return
            self.install_project(project)
            self.status.set('Opened project. '+' '.join(project.source_warnings))
        except (OSError,ValueError,TypeError) as exc:
            messagebox.showerror('Open failed',str(exc),parent=self.root)

    def install_project(self,project):
        self.project=project
        self.spectra.clear()
        self.file_table.delete(*self.file_table.get_children())
        for dataset in project.datasets.values():
            self.spectra[dataset.path]={'path':Path(dataset.path),'spec':dataset.spectrum,'visible':True,'included':True,'sha256':dataset.digest}
            self.file_table.insert('','end',iid=dataset.path,values=('✓','✓',Path(dataset.path).name,f'{dataset.spectrum.signal.size:,}'))
        self.refresh_context()

    def report_dialog(self):
        if not self.project.runs:
            self.status.set('Save one or more labeled analysis results before preparing a report.')
            return
        dialog=tk.Toplevel(self.root)
        dialog.title('Review report selection and export destination')
        dialog.geometry('780x500')
        ttk.Label(dialog,text='Select the saved runs to include',font=('Segoe UI',14,'bold'),padding=12).pack(anchor='w')
        ttk.Label(dialog,text='PDF + CSV + JSON + PNG + SVG. Each run retains its original settings and source hash.\nAssociated modeling sessions are included separately with their own settings; missing acquisition metadata is identified.',wraplength=730,padding=12).pack(fill='x')
        listing=tk.Listbox(dialog,selectmode='extended',exportselection=False)
        listing.pack(fill='both',expand=True,padx=12)
        ids=list(self.project.runs)
        previous=getattr(self.project,'report_selection',[])
        for index,ident in enumerate(ids):
            run=self.project.runs[ident]
            listing.insert('end',f"{run['label']} | {run['snapshot']['peak']} | {run['snapshot']['method']} | {run['created_utc']}")
            if ident in previous:
                listing.selection_set(index)
        preview=tk.StringVar(dialog,value='Choose one or more runs. Ctrl/Shift selects multiple rows.')
        ttk.Label(dialog,textvariable=preview,padding=12).pack(fill='x')
        listing.bind('<<ListboxSelect>>',lambda _e:preview.set(f'{len(listing.curselection())} saved runs selected. Export creates a new folder; existing reports are preserved.'))
        def generate():
            chosen=[ids[i] for i in listing.curselection()]
            if not chosen:
                preview.set('Select at least one saved run.')
                return
            folder=filedialog.askdirectory(parent=dialog,title='Choose where to save the report bundle')
            if not folder:
                return
            try:
                output=export_report(self.project,chosen,proposed_run_folder(folder))
                self.project.report_selection=chosen
                self.status.set('Report bundle saved: '+str(output))
                dialog.destroy()
            except (OSError,ValueError,TypeError) as exc:
                messagebox.showerror('Report export failed',str(exc),parent=dialog)
        ttk.Button(dialog,text='Choose destination and generate report…',command=generate).pack(anchor='e',padx=12,pady=12)
