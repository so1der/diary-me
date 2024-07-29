import sqlite3
from tkinter import Toplevel, Label, Entry, Tk
from tkinter import ttk
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.messagebox
import sv_ttk

fonts = (
    'TimesNewRoman',
    'TimesNewRoman 16',
    'TimesNewRoman 20'
)


def refreshDB():
    tree.delete(*tree.get_children())
    dates = sql.execute('SELECT date FROM diary')
    dates_list = [*dates]
    for index, value in enumerate(dates_list):
        tree.insert(parent='', text=value[0], index=index)
    tree.selection_set(tree.get_children()[0])


def submitPage(submit_date, submit_page):
    sql.execute('INSERT INTO diary VALUES (?, ?)', (submit_date, submit_page))
    db.commit()


def editPage(date, page, old_date):
    sql.execute('UPDATE diary SET date = (?), page = (?) WHERE date = (?)',
                (date, page, old_date))
    db.commit()


def readPage():
    page = Toplevel(root)
    page.focus()
    page.resizable(0, 0)
    selection = tree.item(tree.selection())
    selected_date = selection['text']
    page.title(selected_date)
    Label(page, text=selected_date, font=fonts[2]).pack()
    page_text = sql.execute('SELECT page FROM diary WHERE date = (?)',
                            (selected_date,))
    page_text = list(page_text)[0][0]
    kwargs = {'wrap': 'word', 'font': fonts[1], 'exportselection': 0}
    text = scrolledtext.ScrolledText(page, **kwargs)
    text.insert(tk.END, page_text)
    text.pack()
    ttk.Button(page, text='Edit',
           command=lambda: [writePage(date=selected_date, page=page_text,
                                      edit=True),
                            page.destroy()]).pack()


def writePage(date='', page='', edit=False):
    entry_page = Toplevel(root)
    entry_page.focus()
    entry_page.resizable(0, 0)
    entry_page.title('New Page')
    if edit is True:
        entry_page.title(f'Edit Page {date}')
        old_date = date
    Label(entry_page, text='Date: ',  font=fonts[1]).grid(row=0, column=0)
    submit_date = Entry(entry_page, bd=5, font=fonts[1])
    submit_date.grid(row=0, column=1)
    submit_date.insert(tk.END, date)
    Label(entry_page, text='Text:',  font=fonts[0]).grid(row=1, column=0)
    kwargs = {'wrap': 'word', 'font': fonts[1], 'exportselection': 0}
    page_box = scrolledtext.ScrolledText(entry_page, **kwargs)
    page_box.grid(row=1, column=1)
    page_box.insert(tk.END, page)
    submit = ttk.Button(entry_page, text='Submit')
    submit.grid(row=2, column=1)
    submit.configure(command=lambda: [submitPage(submit_date.get(),
                                                 page_box.get('1.0', tk.END)),
                                      refreshDB(),
                                      entry_page.destroy()])
    if edit is True:
        submit.configure(command=lambda: [editPage(submit_date.get(),
                                                   page_box.get('1.0', tk.END),
                                                   old_date),
                                          refreshDB(),
                                          entry_page.destroy()])


def deletePage():
    selection = tree.item(tree.selection())
    selected_date = selection['text']
    kwargs = {'title': 'Delete page?',
              'message': f'This will fully delete "{selected_date}" page'}
    if tkinter.messagebox.askyesno(**kwargs):
        sql.execute('DELETE FROM diary WHERE date = (?)', (selected_date,))
        db.commit()
        refreshDB()


def OnDoubleClick(event):
    readPage()


db = sqlite3.connect('diary.sqlite3')
sql = db.cursor()
sql.execute('''CREATE TABLE IF NOT EXISTS diary(
        date TEXT,
        page TEXT
    )''')


root = tk.Tk()
root.resizable(0, 0)
root.title('Diary Me')


frame = ttk.Frame(root, padding="10 10 10 10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

tree = ttk.Treeview(frame, show='tree', selectmode='browse', height=12)
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S))
tree.configure(yscrollcommand=scrollbar.set)
tree.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

button_frame = ttk.Frame(frame, padding="10 10 10 10")
button_frame.grid(column=0, row=1, sticky=(tk.W, tk.E))

ttk.Button(button_frame, text='Read page', command=readPage).grid(column=0, row=0, sticky=(tk.W, tk.E))
ttk.Button(button_frame, text='Add new page', command=writePage).grid(column=1, row=0, sticky=(tk.W, tk.E))
ttk.Button(button_frame, text='Refresh', command=refreshDB).grid(column=2, row=0, sticky=(tk.W, tk.E))
ttk.Button(button_frame, text='Delete page', command=deletePage).grid(column=3, row=0, sticky=(tk.W, tk.E))

tree.bind("<Return>", OnDoubleClick)
tree.bind("<Double-1>", OnDoubleClick)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)



if __name__ == '__main__':
    try:
        refreshDB()
    except:
        print('new database was detected/created')
    sv_ttk.set_theme("dark")
    root.mainloop()
