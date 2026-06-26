from __future__ import annotations

import json
from pathlib import Path


def run_gui(root: Path) -> int:
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        from tkinter.scrolledtext import ScrolledText
    except Exception as exc:
        raise RuntimeError("Tkinter is not available in this Python installation.") from exc

    from .core import APP_NAME, APP_VERSION, Store, analyze_email, analyze_file, analyze_text, analyze_url, level_from_score

    store = Store(root)
    store.init()

    PALETTE = {
        'bg': '#080a0e',
        'panel': '#10141b',
        'panel2': '#131a23',
        'soft': '#1c2430',
        'line': '#263241',
        'text': '#d9e1ea',
        'muted': '#7c8797',
        'red': '#ff355e',
        'red2': '#ff6b6b',
        'amber': '#ffb020',
        'green': '#39d98a',
        'cyan': '#52d1ff',
        'white': '#f5f7fa',
    }

    def score_color(score: int) -> str:
        level, _ = level_from_score(score)
        return {
            'CRITICAL': '#ff355e',
            'HIGH': '#ff6b6b',
            'MEDIUM': '#ffb020',
            'LOW': '#74d680',
            'INFO': '#52d1ff',
        }.get(level, PALETTE['white'])

    class LictorApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title(f"{APP_NAME} {APP_VERSION} // OBSIDIAN INTERFACE")
            self.geometry('1380x860')
            self.minsize(1200, 760)
            self.configure(bg=PALETTE['bg'])
            self.current_result = None
            self.current_mode = 'home'
            self.form_container = None
            self.result_text = None
            self.signal_list = None
            self.level_big = None
            self.score_value = None
            self.reco_label = None
            self.gauge_canvas = None
            self.footer_label = None
            self.nav_buttons = {}

            self._build_shell()
            self.show_home()

        def _build_shell(self):
            self.sidebar = tk.Frame(self, bg='#090c11', width=255, highlightthickness=1, highlightbackground=PALETTE['line'])
            self.sidebar.pack(side='left', fill='y')
            self.sidebar.pack_propagate(False)

            banner = (
                "██╗     ██╗ ██████╗████████╗ ██████╗ ██████╗\n"
                "██║     ██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗\n"
                "██║     ██║██║        ██║   ██║   ██║██████╔╝\n"
                "██║     ██║██║        ██║   ██║   ██║██╔══██╗\n"
                "███████╗██║╚██████╗   ██║   ╚██████╔╝██║  ██║\n"
                "╚══════╝╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝\n"
                "       LOCAL INDICATOR // CASE TRIAGE OPERATOR"
            )
            tk.Label(
                self.sidebar,
                text=banner,
                bg='#090c11', fg=PALETTE['red'],
                font=('Consolas', 10, 'bold'),
                justify='left'
            ).pack(anchor='w', padx=14, pady=(18, 10))

            tk.Label(
                self.sidebar,
                text='BROTHER UNIT OF CIVITAS\nSIGNATURE: xtr4ng3',
                bg='#090c11', fg=PALETTE['muted'],
                font=('Segoe UI', 10, 'bold'), justify='left'
            ).pack(anchor='w', padx=14, pady=(0, 18))

            nav_items = [
                ('home', 'HOME'),
                ('url', 'URL / DOMAIN'),
                ('email', 'EMAIL'),
                ('text', 'TEXT'),
                ('file', 'FILE HASH'),
                ('history', 'HISTORY'),
            ]
            for key, title in nav_items:
                cmd = getattr(self, f'show_{key}')
                btn = tk.Button(
                    self.sidebar, text=title, command=cmd,
                    relief='flat', bd=0, cursor='hand2',
                    bg=PALETTE['panel'], fg=PALETTE['text'],
                    activebackground=PALETTE['red'], activeforeground=PALETTE['white'],
                    font=('Segoe UI', 11, 'bold'), padx=12, pady=12,
                    anchor='w'
                )
                btn.pack(fill='x', padx=14, pady=5)
                self.nav_buttons[key] = btn

            info_box = tk.Frame(self.sidebar, bg='#090c11', highlightthickness=1, highlightbackground=PALETTE['line'])
            info_box.pack(fill='x', padx=14, pady=16)
            info_text = (
                '[ RULESET ]\n'
                'NO NETWORK LOOKUPS\n'
                'NO HIDDEN SENDING\n'
                'NO CREDENTIAL COLLECTION\n'
                'NO COVERT UPLOAD\n'
            )
            tk.Label(info_box, text=info_text, bg='#090c11', fg=PALETTE['cyan'], font=('Consolas', 10), justify='left').pack(anchor='w', padx=10, pady=10)

            self.main = tk.Frame(self, bg=PALETTE['bg'])
            self.main.pack(side='left', fill='both', expand=True)

            topbar = tk.Frame(self.main, bg=PALETTE['bg'])
            topbar.pack(fill='x', padx=18, pady=(16, 10))

            titlewrap = tk.Frame(topbar, bg=PALETTE['bg'])
            titlewrap.pack(side='left', fill='x', expand=True)
            tk.Label(titlewrap, text='LICTOR // OBSIDIAN OPERATIONS CONSOLE', bg=PALETTE['bg'], fg=PALETTE['white'], font=('Segoe UI', 22, 'bold')).pack(anchor='w')
            tk.Label(titlewrap, text='Cold local triage for suspicious indicators, message pressure and static risk signals.', bg=PALETTE['bg'], fg=PALETTE['muted'], font=('Segoe UI', 10)).pack(anchor='w', pady=(2,0))

            status = tk.Frame(topbar, bg=PALETTE['panel'], highlightthickness=1, highlightbackground=PALETTE['line'])
            status.pack(side='right')
            self.footer_label = tk.Label(status, text='STATUS: READY', bg=PALETTE['panel'], fg=PALETTE['green'], font=('Consolas', 11, 'bold'), padx=12, pady=10)
            self.footer_label.pack()

            self.hero = tk.Frame(self.main, bg=PALETTE['panel'], highlightthickness=1, highlightbackground=PALETTE['line'])
            self.hero.pack(fill='x', padx=18, pady=(0, 12))
            hero_left = tk.Frame(self.hero, bg=PALETTE['panel'])
            hero_left.pack(side='left', fill='both', expand=True)
            hero_ascii = (
                '╔════════════════════════════════════════════════════════════╗\n'
                '║  ░ SIGNAL TRIAGE  ░ STATIC REVIEW  ░ LOCAL ARCHIVE       ║\n'
                '║  ░ URL / EMAIL / TEXT / FILE ░ RISK SCORE ░ HTML REPORT  ║\n'
                '╚════════════════════════════════════════════════════════════╝'
            )
            tk.Label(hero_left, text=hero_ascii, bg=PALETTE['panel'], fg=PALETTE['red2'], font=('Consolas', 12, 'bold'), justify='left').pack(anchor='w', padx=18, pady=16)
            tk.Label(hero_left, text='CIVITAS keeps the archive. LICTOR interrogates the threshold.', bg=PALETTE['panel'], fg=PALETTE['muted'], font=('Segoe UI', 10, 'italic')).pack(anchor='w', padx=18, pady=(0,16))

            self.content = tk.Frame(self.main, bg=PALETTE['bg'])
            self.content.pack(fill='both', expand=True, padx=18, pady=(0, 18))

            self.left_panel = tk.Frame(self.content, bg=PALETTE['panel2'], highlightthickness=1, highlightbackground=PALETTE['line'])
            self.left_panel.pack(side='left', fill='both', expand=True)
            self.right_panel = tk.Frame(self.content, bg=PALETTE['panel'], width=450, highlightthickness=1, highlightbackground=PALETTE['line'])
            self.right_panel.pack(side='left', fill='y', padx=(14, 0))
            self.right_panel.pack_propagate(False)

            self._build_result_panel()

        def _set_status(self, text, color=None):
            self.footer_label.configure(text=text, fg=color or PALETTE['green'])

        def _set_nav(self, selected):
            for key, btn in self.nav_buttons.items():
                if key == selected:
                    btn.configure(bg=PALETTE['red'], fg=PALETTE['white'])
                else:
                    btn.configure(bg=PALETTE['panel'], fg=PALETTE['text'])

        def _clear_form(self):
            for w in self.left_panel.winfo_children():
                w.destroy()

        def _build_result_panel(self):
            for w in self.right_panel.winfo_children():
                w.destroy()

            head = tk.Frame(self.right_panel, bg=PALETTE['panel'])
            head.pack(fill='x', padx=16, pady=(16,10))
            tk.Label(head, text='RISK TELEMETRY', bg=PALETTE['panel'], fg=PALETTE['white'], font=('Segoe UI', 18, 'bold')).pack(anchor='w')
            tk.Label(head, text='Live output rendered after each local triage execution.', bg=PALETTE['panel'], fg=PALETTE['muted'], font=('Segoe UI', 9)).pack(anchor='w')

            gauge_card = tk.Frame(self.right_panel, bg=PALETTE['panel2'], highlightthickness=1, highlightbackground=PALETTE['line'])
            gauge_card.pack(fill='x', padx=16, pady=(0,10))

            top = tk.Frame(gauge_card, bg=PALETTE['panel2'])
            top.pack(fill='x', padx=14, pady=(12, 8))
            self.level_big = tk.Label(top, text='NO SCAN', bg=PALETTE['panel2'], fg=PALETTE['muted'], font=('Segoe UI', 20, 'bold'))
            self.level_big.pack(side='left')
            self.score_value = tk.Label(top, text='0 / 100', bg=PALETTE['panel2'], fg=PALETTE['white'], font=('Consolas', 16, 'bold'))
            self.score_value.pack(side='right')

            self.gauge_canvas = tk.Canvas(gauge_card, width=390, height=44, bg=PALETTE['panel2'], highlightthickness=0)
            self.gauge_canvas.pack(fill='x', padx=14)
            self._render_gauge(0)

            self.reco_label = tk.Label(gauge_card, text='Awaiting scan.', bg=PALETTE['panel2'], fg=PALETTE['muted'], font=('Segoe UI', 10), justify='left', wraplength=390)
            self.reco_label.pack(anchor='w', padx=14, pady=(8, 14))

            signals_card = tk.Frame(self.right_panel, bg=PALETTE['panel2'], highlightthickness=1, highlightbackground=PALETTE['line'])
            signals_card.pack(fill='x', padx=16, pady=(0,10))
            tk.Label(signals_card, text='SIGNALS', bg=PALETTE['panel2'], fg=PALETTE['white'], font=('Segoe UI', 14, 'bold')).pack(anchor='w', padx=12, pady=(10,8))
            self.signal_list = tk.Listbox(signals_card, bg='#0d1117', fg=PALETTE['text'], selectbackground=PALETTE['soft'], relief='flat', height=8, font=('Consolas', 9))
            self.signal_list.pack(fill='x', padx=12, pady=(0,12))

            output_card = tk.Frame(self.right_panel, bg=PALETTE['panel2'], highlightthickness=1, highlightbackground=PALETTE['line'])
            output_card.pack(fill='both', expand=True, padx=16, pady=(0,16))
            bar = tk.Frame(output_card, bg=PALETTE['soft'])
            bar.pack(fill='x')
            tk.Label(bar, text='STRUCTURED OUTPUT', bg=PALETTE['soft'], fg=PALETTE['white'], font=('Consolas', 11, 'bold')).pack(anchor='w', padx=10, pady=8)
            self.result_text = ScrolledText(output_card, height=18, bg='#0b0f14', fg='#e6edf3', insertbackground='#ffffff', relief='flat', font=('Consolas', 9), wrap='word')
            self.result_text.pack(fill='both', expand=True, padx=10, pady=10)
            self.result_text.insert('1.0', '{\n  "status": "ready"\n}')
            self.result_text.configure(state='disabled')

            btns = tk.Frame(self.right_panel, bg=PALETTE['panel'])
            btns.pack(fill='x', padx=16, pady=(0,16))
            tk.Button(btns, text='SAVE JSON', command=self.save_json, relief='flat', bg=PALETTE['red'], fg=PALETTE['white'], activebackground=PALETTE['red2'], activeforeground=PALETTE['white'], font=('Segoe UI', 10, 'bold'), padx=10, pady=10).pack(side='left', fill='x', expand=True)
            tk.Button(btns, text='SAVE HTML', command=self.save_html, relief='flat', bg=PALETTE['soft'], fg=PALETTE['white'], activebackground=PALETTE['line'], activeforeground=PALETTE['white'], font=('Segoe UI', 10, 'bold'), padx=10, pady=10).pack(side='left', fill='x', expand=True, padx=(8,0))

        def _render_gauge(self, score):
            c = self.gauge_canvas
            c.delete('all')
            w = max(c.winfo_width(), 390)
            h = 44
            pad = 2
            c.create_rectangle(pad, 10, w-pad, 34, fill='#0b0f14', outline=PALETTE['line'])
            fill = int((w-2*pad) * max(0, min(100, score)) / 100)
            col = score_color(score)
            c.create_rectangle(pad, 10, fill, 34, fill=col, outline=col)
            for t in [0, 25, 50, 75, 100]:
                x = pad + (w-2*pad) * t / 100
                c.create_line(x, 8, x, 36, fill='#334155')
                c.create_text(x, 3, text=str(t), fill=PALETTE['muted'], font=('Consolas', 8), anchor='n')

        def _field(self, parent, label, var=None, width=40):
            tk.Label(parent, text=label, bg=PALETTE['panel2'], fg=PALETTE['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=18, pady=(12, 4))
            ent = tk.Entry(parent, textvariable=var, bg='#0b0f14', fg=PALETTE['white'], insertbackground=PALETTE['white'], relief='flat', font=('Segoe UI', 12), width=width)
            ent.pack(fill='x', padx=18)
            return ent

        def _section_header(self, title, subtitle=''):
            wrap = tk.Frame(self.left_panel, bg=PALETTE['panel2'])
            wrap.pack(fill='x', padx=0, pady=0)
            tk.Label(wrap, text=title, bg=PALETTE['panel2'], fg=PALETTE['white'], font=('Segoe UI', 20, 'bold')).pack(anchor='w', padx=18, pady=(18, 4))
            if subtitle:
                tk.Label(wrap, text=subtitle, bg=PALETTE['panel2'], fg=PALETTE['muted'], font=('Segoe UI', 9)).pack(anchor='w', padx=18, pady=(0, 12))

        def _example_card(self, title, content):
            card = tk.Frame(self.left_panel, bg='#0c1016', highlightthickness=1, highlightbackground=PALETTE['line'])
            card.pack(fill='x', padx=18, pady=(12, 0))
            tk.Label(card, text=title, bg='#0c1016', fg=PALETTE['cyan'], font=('Consolas', 10, 'bold')).pack(anchor='w', padx=12, pady=(10, 6))
            tk.Label(card, text=content, bg='#0c1016', fg=PALETTE['muted'], justify='left', font=('Consolas', 9)).pack(anchor='w', padx=12, pady=(0, 10))

        def _action_button(self, text, command):
            return tk.Button(self.left_panel, text=text, command=command, relief='flat', cursor='hand2', bg=PALETTE['red'], fg=PALETTE['white'], activebackground=PALETTE['red2'], activeforeground=PALETTE['white'], font=('Segoe UI', 11, 'bold'), padx=12, pady=12)

        def render_result(self, result):
            self.current_result = result
            try:
                store.save(result)
            except Exception:
                pass
            score = int(result.get('score', 0))
            col = score_color(score)
            self._render_gauge(score)
            self.level_big.configure(text=result.get('level', 'UNKNOWN'), fg=col)
            self.score_value.configure(text=f'{score} / 100', fg=col)
            self.reco_label.configure(text=result.get('recommendation', ''), fg=PALETTE['text'])
            self.signal_list.delete(0, 'end')
            for sig in result.get('signals', []):
                line = f"+{sig.get('weight',0):>2}  {sig.get('code')}  ::  {sig.get('detail')}"
                self.signal_list.insert('end', line)
            self.result_text.configure(state='normal')
            self.result_text.delete('1.0', 'end')
            self.result_text.insert('1.0', json.dumps(result, ensure_ascii=False, indent=2))
            self.result_text.configure(state='disabled')
            self._set_status(f"STATUS: {result.get('level','READY')} // SCORE {score}", col)

        def save_json(self):
            if not self.current_result:
                messagebox.showwarning(APP_NAME, 'No result to save.')
                return
            path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
            if not path:
                return
            Path(path).write_text(json.dumps(self.current_result, ensure_ascii=False, indent=2), encoding='utf-8')
            self._set_status('STATUS: JSON WRITTEN', PALETTE['cyan'])
            messagebox.showinfo(APP_NAME, 'JSON saved.')

        def save_html(self):
            if not self.current_result:
                messagebox.showwarning(APP_NAME, 'No result to save.')
                return
            path = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML', '*.html')])
            if not path:
                return
            store.export_html(self.current_result, path)
            self._set_status('STATUS: HTML REPORT WRITTEN', PALETTE['cyan'])
            messagebox.showinfo(APP_NAME, 'HTML saved.')

        def show_home(self):
            self.current_mode = 'home'
            self._set_nav('home')
            self._clear_form()
            self._section_header('HOME', 'A heavier interface for local triage operations.')
            block = tk.Frame(self.left_panel, bg='#0c1016', highlightthickness=1, highlightbackground=PALETTE['line'])
            block.pack(fill='both', expand=True, padx=18, pady=(0,18))
            body = (
                'LICTOR is the harder brother of CIVITAS.\n\n'
                'Where CIVITAS organizes evidence and the case archive,\n'
                'LICTOR interrogates suspicious indicators at the threshold.\n\n'
                'Operational lanes:\n'
                '  • URL / DOMAIN static risk review\n'
                '  • EMAIL pressure and impersonation review\n'
                '  • TEXT scam pattern review\n'
                '  • FILE extension and hash review\n\n'
                'Everything is local-first.\n'
                'No hidden sending. No network calls. No credential collection.'
            )
            tk.Label(block, text=body, bg='#0c1016', fg=PALETTE['text'], justify='left', font=('Segoe UI', 13), padx=18, pady=18).pack(anchor='nw', fill='both', expand=True)
            self._example_card('QUICK LAUNCH', 'Double-click ABRIR_LICTOR.bat\nOr run: python lictor.py gui')
            self._set_status('STATUS: READY', PALETTE['green'])

        def show_url(self):
            self.current_mode = 'url'
            self._set_nav('url')
            self._clear_form()
            self._section_header('URL / DOMAIN', 'Static local review with no external lookups.')
            value = tk.StringVar()
            self._field(self.left_panel, 'Target', value)
            btn = self._action_button('EXECUTE URL TRIAGE', lambda: self.render_result(analyze_url(value.get())))
            btn.pack(anchor='w', padx=18, pady=16)
            self._example_card('EXAMPLE', 'http://bit.ly/test?token=123\nmercadopago-seguridad-login.example.com')
            self._set_status('STATUS: URL TRIAGE READY', PALETTE['green'])

        def show_email(self):
            self.current_mode = 'email'
            self._set_nav('email')
            self._clear_form()
            self._section_header('EMAIL', 'Sender, claimed entity and body pressure review.')
            sender = tk.StringVar(); claimed = tk.StringVar(); subject = tk.StringVar()
            self._field(self.left_panel, 'Sender', sender)
            self._field(self.left_panel, 'Claimed entity', claimed)
            self._field(self.left_panel, 'Subject', subject)
            tk.Label(self.left_panel, text='Body', bg=PALETTE['panel2'], fg=PALETTE['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=18, pady=(12,4))
            body = ScrolledText(self.left_panel, height=12, bg='#0b0f14', fg=PALETTE['white'], insertbackground=PALETTE['white'], relief='flat', font=('Segoe UI', 10), wrap='word')
            body.pack(fill='both', expand=True, padx=18)
            btn = self._action_button('EXECUTE EMAIL TRIAGE', lambda: self.render_result(analyze_email(sender.get(), subject.get(), body.get('1.0', 'end'), claimed.get())))
            btn.pack(anchor='w', padx=18, pady=16)
            self._example_card('EXAMPLE', 'Sender: support@hotmail.com\nClaimed entity: Microsoft\nSubject: Cuenta bloqueada\nBody: Confirma tu clave urgente.')
            self._set_status('STATUS: EMAIL TRIAGE READY', PALETTE['green'])

        def show_text(self):
            self.current_mode = 'text'
            self._set_nav('text')
            self._clear_form()
            self._section_header('TEXT', 'Pressure, secrecy and impersonation pattern review.')
            tk.Label(self.left_panel, text='Message', bg=PALETTE['panel2'], fg=PALETTE['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=18, pady=(12,4))
            txt = ScrolledText(self.left_panel, height=18, bg='#0b0f14', fg=PALETTE['white'], insertbackground=PALETTE['white'], relief='flat', font=('Segoe UI', 11), wrap='word')
            txt.pack(fill='both', expand=True, padx=18)
            btn = self._action_button('EXECUTE TEXT TRIAGE', lambda: self.render_result(analyze_text(txt.get('1.0', 'end'))))
            btn.pack(anchor='w', padx=18, pady=16)
            self._example_card('EXAMPLE', 'Soy tu nieto, cambié de número.\nNecesito plata urgente, no le digas a nadie.')
            self._set_status('STATUS: TEXT TRIAGE READY', PALETTE['green'])

        def show_file(self):
            self.current_mode = 'file'
            self._set_nav('file')
            self._clear_form()
            self._section_header('FILE HASH', 'Local file review with hashes and extension signalization.')
            file_var = tk.StringVar()
            self._field(self.left_panel, 'File path', file_var)
            def browse():
                path = filedialog.askopenfilename()
                if path:
                    file_var.set(path)
            browse_btn = tk.Button(self.left_panel, text='BROWSE', command=browse, relief='flat', cursor='hand2', bg=PALETTE['soft'], fg=PALETTE['white'], activebackground=PALETTE['line'], activeforeground=PALETTE['white'], font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
            browse_btn.pack(anchor='w', padx=18, pady=(12,8))
            btn = self._action_button('EXECUTE FILE TRIAGE', lambda: self.render_result(analyze_file(file_var.get())))
            btn.pack(anchor='w', padx=18, pady=8)
            self._example_card('EXAMPLE', 'C:\\Users\\You\\Downloads\\sample.exe')
            self._set_status('STATUS: FILE TRIAGE READY', PALETTE['green'])

        def show_history(self):
            self.current_mode = 'history'
            self._set_nav('history')
            self._clear_form()
            self._section_header('HISTORY', 'Local SQLite archive of previous triage results.')
            box = tk.Frame(self.left_panel, bg='#0c1016', highlightthickness=1, highlightbackground=PALETTE['line'])
            box.pack(fill='both', expand=True, padx=18, pady=(0,18))
            cols = ('created', 'type', 'level', 'score', 'input')
            tree = ttk.Treeview(box, columns=cols, show='headings')
            for col, width in [('created',150), ('type',90), ('level',90), ('score',70), ('input',500)]:
                tree.heading(col, text=col.upper())
                tree.column(col, width=width, anchor='w')
            y = ttk.Scrollbar(box, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=y.set)
            tree.pack(side='left', fill='both', expand=True, padx=(10,0), pady=10)
            y.pack(side='right', fill='y', pady=10, padx=(0,10))
            for row in store.latest(250):
                tree.insert('', 'end', values=(row.get('created_at'), row.get('type'), row.get('level'), row.get('score'), str(row.get('input'))[:200]))
            controls = tk.Frame(self.left_panel, bg=PALETTE['panel2'])
            controls.pack(fill='x', padx=18, pady=(0,18))
            tk.Button(controls, text='EXPORT CSV', command=self._export_csv, relief='flat', bg=PALETTE['red'], fg=PALETTE['white'], activebackground=PALETTE['red2'], activeforeground=PALETTE['white'], font=('Segoe UI', 10, 'bold'), padx=10, pady=10).pack(side='left')
            self._set_status('STATUS: HISTORY READY', PALETTE['green'])

        def _export_csv(self):
            path = store.export_csv()
            self._set_status('STATUS: CSV ARCHIVE WRITTEN', PALETTE['cyan'])
            messagebox.showinfo(APP_NAME, f'CSV exported:\n{path}')

    app = LictorApp()
    app.mainloop()
    return 0
