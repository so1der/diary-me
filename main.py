import sqlite3
from tkinter import Toplevel, Label, Button, Entry, Tk
from tkinter import ttk
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.messagebox


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
    Button(page, text='Edit', font=fonts[1],
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
    Label(entry_page, text='Date: ',  font=fonts[0]).grid(row=0, column=0)
    submit_date = Entry(entry_page, bd=5, font=fonts[0])
    submit_date.grid(row=0, column=1)
    submit_date.insert(tk.END, date)
    Label(entry_page, text='Text:',  font=fonts[0]).grid(row=1, column=0)
    kwargs = {'wrap': 'word', 'font': fonts[1], 'exportselection': 0}
    page_box = scrolledtext.ScrolledText(entry_page, **kwargs)
    page_box.grid(row=1, column=1)
    page_box.insert(tk.END, page)
    submit = Button(entry_page, text='Submit',  font=fonts[1])
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

root = Tk()
root.resizable(0, 0)
root.title('Diary Me')

tree = ttk.Treeview(show='tree', selectmode='browse', height=12)
scrollbar = ttk.Scrollbar(orient="vertical", command=tree.yview)
scrollbar.pack(side='right', fill='y')
tree.configure(yscrollcommand=scrollbar.set)
tree.pack()
Button(text='Read page', command=readPage).pack(fill='x')
Button(text='Add new page', command=writePage).pack(fill='x')
Button(text='Refresh', command=refreshDB).pack(fill='x')
Button(text='Delete page', command=deletePage).pack(fill='x')
tree.bind("<Return>", OnDoubleClick)
tree.bind("<Double-1>", OnDoubleClick)

if __name__ == '__main__':
    try:
        refreshDB()
    except:
        print('new database was detected/created')
    root.mainloop()
