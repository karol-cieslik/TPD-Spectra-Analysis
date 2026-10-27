"""Offline, read-only scientific Help for the three-stage TPD workflow.

Help does not inspect the active spectrum, execute calculations, write files,
change method inputs or connect to a network service.
"""

import json
import tkinter as tk
from tkinter import ttk

from .beta_resources import resource


CATALOG_RESOURCE = 'docs/beta/SCIENTIFIC_HELP_TOPICS.json'
REQUIRED_FIELDS = {'id', 'group', 'title', 'symbol', 'unit', 'role', 'context',
                   'short', 'detail', 'example', 'caution'}


def load_help_catalog(path=None):
    """Load and check the bundled topics; useful independently of Tk/display."""
    location = path if path is not None else resource(CATALOG_RESOURCE)
    with open(location, encoding='utf-8') as handle:
        payload = json.load(handle)
    if payload.get('schema_version') != 1 or not isinstance(payload.get('topics'), list):
        raise ValueError('Unsupported scientific Help catalog schema.')
    ids = set()
    for topic in payload['topics']:
        if not isinstance(topic, dict) or not REQUIRED_FIELDS <= topic.keys():
            raise ValueError('Scientific Help topic has missing required fields.')
        # Workflow actions legitimately have no equation symbol.
        if not isinstance(topic['symbol'], str) or not all(
                isinstance(topic[key], str) and topic[key].strip()
                for key in REQUIRED_FIELDS - {'context', 'symbol'}):
            raise ValueError('Scientific Help topic contains a blank text field.')
        if not isinstance(topic['context'], list) or not topic['context']:
            raise ValueError('Scientific Help topic has no workflow context.')
        if topic['id'] in ids:
            raise ValueError('Duplicate scientific Help topic: ' + topic['id'])
        ids.add(topic['id'])
    if not payload['topics']:
        raise ValueError('Scientific Help catalog is empty.')
    return payload


def help_button(parent, app, topic_id):
    """Focusable, visible alternative to hover-only field tooltips."""
    return ttk.Button(parent, text='?', width=3,
                      command=lambda: app.open_scientific_help(topic_id))


class ScientificHelpDialog:
    """Non-modal searchable topic browser with keyboard-accessible controls."""

    def __init__(self, app, selected_topic=None):
        self.app = app
        self.catalog = load_help_catalog()
        self.by_id = {item['id']: item for item in self.catalog['topics']}
        self.window = tk.Toplevel(app.root)
        self.window.title('Scientific Help — TPD Spectra Studio')
        self.window.geometry('1000x650')
        self.window.minsize(700, 460)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.bind('<Escape>', lambda _event: self.close())

        heading = ttk.Frame(self.window, padding=(12, 12, 12, 6))
        heading.pack(fill='x')
        ttk.Label(heading, text='Scientific Help / Parameter Reference',
                  font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        ttk.Label(heading,
                  text='Search topics or select a category. Help is offline and does not change any calculation.',
                  wraplength=850).pack(anchor='w', pady=(4, 0))
        search_bar = ttk.Frame(self.window, padding=(12, 0, 12, 8))
        search_bar.pack(fill='x')
        ttk.Label(search_bar, text='Search').pack(side='left', padx=(0, 8))
        self.query = tk.StringVar(self.window)
        self.search = ttk.Entry(search_bar, textvariable=self.query)
        self.search.pack(side='left', fill='x', expand=True)
        ttk.Button(search_bar, text='Clear', command=lambda: self.query.set('')).pack(side='left', padx=(8, 0))

        panes = ttk.Panedwindow(self.window, orient='horizontal')
        panes.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        browser, reader = ttk.Frame(panes), ttk.Frame(panes)
        panes.add(browser, weight=1)
        panes.add(reader, weight=2)
        browser.rowconfigure(0, weight=1)
        browser.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(browser, show='tree', selectmode='browse')
        self.tree.grid(row=0, column=0, sticky='nsew')
        nav_scroll = ttk.Scrollbar(browser, orient='vertical', command=self.tree.yview)
        nav_scroll.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=nav_scroll.set)
        self.tree.bind('<<TreeviewSelect>>', self._render_selected)

        reader.rowconfigure(0, weight=1)
        reader.columnconfigure(0, weight=1)
        self.detail = tk.Text(reader, wrap='word', padx=14, pady=12,
                              font=('Segoe UI', 10), state='disabled')
        self.detail.grid(row=0, column=0, sticky='nsew')
        detail_scroll = ttk.Scrollbar(reader, orient='vertical', command=self.detail.yview)
        detail_scroll.grid(row=0, column=1, sticky='ns')
        self.detail.configure(yscrollcommand=detail_scroll.set)
        self.detail.tag_configure('title', font=('Segoe UI', 14, 'bold'), spacing3=12)
        self.detail.tag_configure('subheading', font=('Segoe UI', 10, 'bold'), spacing1=11)
        self.detail.tag_configure('warning', foreground='#9b3b1e')

        footer = ttk.Frame(self.window, padding=(12, 0, 12, 12))
        footer.pack(fill='x')
        self.count = tk.StringVar(self.window)
        ttk.Label(footer, textvariable=self.count).pack(side='left')
        ttk.Button(footer, text='Close', command=self.close).pack(side='right')
        self.query.trace_add('write', lambda *_: self.refresh())
        self.refresh(selected_topic)
        self.search.focus_set()

    def refresh(self, selected_topic=None):
        """Filter on scientific content while retaining category grouping."""
        current = selected_topic or self._current_id()
        term = self.query.get().casefold().strip()
        matches = []
        for topic in self.catalog['topics']:
            searchable = ' '.join(str(topic.get(key, '')) for key in
                                  ('title', 'id', 'group', 'symbol', 'unit', 'short', 'detail', 'example', 'caution'))
            if not term or term in searchable.casefold():
                matches.append(topic)
        self.tree.delete(*self.tree.get_children())
        group_ids = {}
        for topic in matches:
            name = topic['group']
            if name not in group_ids:
                parent = self.tree.insert('', 'end', text=name, open=True)
                group_ids[name] = parent
            self.tree.insert(group_ids[name], 'end', iid=topic['id'], text=topic['title'])
        self.count.set(f'{len(matches)} / {len(self.catalog["topics"])} topics')
        target = current if current in {topic['id'] for topic in matches} else (
            matches[0]['id'] if matches else None)
        if target is not None:
            self.tree.selection_set(target)
            self.tree.see(target)
            self._display_topic(self.by_id[target])
        else:
            self._display_empty('No matching topics. Try a different search term.')

    def _current_id(self):
        selection = self.tree.selection()
        return selection[0] if selection and selection[0] in self.by_id else None

    def _render_selected(self, _event=None):
        selected = self._current_id()
        if selected is not None:
            self._display_topic(self.by_id[selected])

    def select_topic(self, topic_id):
        """Focus a requested topic even if an earlier search hid it."""
        if topic_id and topic_id not in self.by_id:
            self._display_empty('This Help topic is unavailable. Open the full reference to browse other topics.')
            return
        if topic_id:
            self.query.set('')
        self.refresh(topic_id)
        self.window.lift()

    def _display_empty(self, message):
        self.detail.configure(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('end', message)
        self.detail.configure(state='disabled')

    def _display_topic(self, topic):
        self.detail.configure(state='normal')
        self.detail.delete('1.0', 'end')

        def line(value, tag=None):
            self.detail.insert('end', str(value).strip() + '\n', (tag,) if tag else ())

        line(topic['title'] + ('  (' + topic['symbol'] + ')' if topic['symbol'] not in ('—', '-') else ''), 'title')
        line('Unit: ' + topic['unit'])
        role = topic['role'].replace('_', ' ').capitalize()
        legend = self.catalog.get('role_legend', {}).get(topic['role'], '')
        line('Role: ' + role + ('. ' + legend if legend else ''))
        if topic.get('role_notes'):
            line('Method-dependent role: ' + topic['role_notes'])
        line('In brief', 'subheading')
        line(topic['short'])
        line('Explanation', 'subheading')
        line(topic['detail'])
        line('Example', 'subheading')
        line(topic['example'])
        line('Scientific caution', 'subheading')
        line(topic['caution'], 'warning')
        line('Relevant sections: ' + ', '.join(topic['context']))
        self.detail.configure(state='disabled')
        self.detail.yview_moveto(0)

    def close(self):
        if self.window.winfo_exists():
            self.window.destroy()
        if getattr(self.app, 'scientific_help_dialog', None) is self:
            self.app.scientific_help_dialog = None
