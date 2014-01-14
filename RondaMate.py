"""
Small UI created after my first tkinter tutorial about two years ago. Original version just showed the window, buttons, etc.
Dialogs and event handlers code were added to tie this with RondaClient
"""
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from RondaClient import RondaClient

network_client = None


def start(*args):
    network_client.create_ronda()
    

def cancel(*args):
    network_client.close_ronda()
    

def participate(*args):
    selected = rounds_list.get(ACTIVE)
    network_client.subscribe_to_ronda(str(selected))


def update_information():
    network_client.update()
    #clear list box
    rounds_list.delete(0, END)
    for round in network_client.published_rondas:
        rounds_list.insert(END, round)

    subscribed_list.delete(0, END)
    for subs in network_client.my_ronda_members:
        subscribed_list.insert(END, subs)

    root.after(1000, update_information)


def close_network_client():
    try:
        network_client.close_client()
        root.quit()
    except Exception as e:
        print("Error closing the client - Error: ", e)

#def run(): 
root = Tk()
root.title("Ronda mate")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

label_name = ttk.Label(mainframe, text="Nombre: ")

name = StringVar()
name_entry = ttk.Entry(mainframe, width=20, textvariable=name, state='readonly')

rounds_label = ttk.Label(mainframe, text="Rondas: ")
rounds_list = Listbox(mainframe, height=10)

subscribed_label = ttk.Label(mainframe, text="Participantes ronda: ")
subscribed_list = Listbox(mainframe, height=10)

start_button = ttk.Button(mainframe, text="Iniciar ronda", command=start)
cancel_button = ttk.Button(mainframe, text="Cerrar ronda", command=cancel)
participate_button = ttk.Button(mainframe, text="Sumarse a ronda", command=participate)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

name_entry.focus()

label_name.grid(column=1, row=1, sticky=(W, E))
name_entry.grid(column=2, row=1, sticky=(W, E))
rounds_label.grid(column=1, row=2, sticky=(W, E))
rounds_list.grid(column=1, row=3, sticky=(W,E)) 
subscribed_label.grid(column=2, row=2, sticky=(W, E))
subscribed_list.grid(column=2, row=3, sticky=(W,E)) 
start_button.grid(column=3, row=1, sticky=W)
cancel_button.grid(column=3, row=2, sticky=W)
participate_button.grid(column=3, row=3, sticky=N)

name_input = None
while not name_input:
    name_input = simpledialog.askstring("Nombre", "Ingrese el nombre de usuario")

name.set(name_input)

server = simpledialog.askstring('Server', 'Indique el server al cual conectarse')

if not server:
    server = '192.168.0.4'

network_client = RondaClient(name_input, server, 3490)
root.protocol("WM_DELETE_WINDOW", close_network_client)
root.protocol("WM_DELETE_WINDOW", close_network_client)
update_information()
root.mainloop()


#def main():    
#   return 0

#if __name__ == '__main__':
#   main()

