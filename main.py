from tkinter import *
from customtkinter import *
from tkinter import filedialog, messagebox

from login import main
from API_dealer import *
from image_handler import *

import threading
import webbrowser
import requests
import random
import time



########################################################### Closing part ################################################################
def on_close():
    if server_status == True:
        requests.post('http://127.0.0.1:5000/shutdown')
    win.destroy()
##########################################################################################################################################
# Gloabal variables
access_token = None
sizes = ['2x2','3x3','4x4','5x5','6x6','7x7','8x8']
server_status = False

##########################################################################################################################################


def thread_server():
    global access_token,playlists_dict,server_status
        
    threading.Thread(target=main).start()
    server_status = True
    
    webbrowser.open('http://localhost:5000/')
    time.sleep(1)
    response = requests.get('http://localhost:5000/data')
    data = response.json()

    access_token = data['access_token']
    
    if access_token is not None:
        
        login.configure(text='Logged in',font=('Arial',11),state='disabled')
        
        usrname, email, userid = get_user_info(access_token=access_token)
        if len(email) + len(usrname) > 30:
            email = email[:6]+'...'+email[-11:]
        
        info.configure(text=f"{usrname} | {email}")
        
        playlists, playlists_dict_list = get_user_playlists(access_token=access_token,user_id=userid)
        
        playlists_dict = {}
        for data in playlists_dict_list:
            playlists_dict[data['name']] = data['uri']
            
        pList.configure(values=playlists, command=check_playlist,state='normal')
        grid.configure(command=check_grid) 


def check_playlist(choice):
    
    pList.configure(state='disabled')
    bar.configure(mode='indeterminate',indeterminate_speed=2)
    bar.start()
    
    threading.Thread(target=checking_playlist_process, args=(access_token,choice)).start()
def checking_playlist_process(access_token,choice):
    global playlists_dict
    
    collage_size = int(grid.get().split('x')[0]) * int(grid.get().split('x')[1])
    albums = get_playlist_albums_count(access_token,playlists_dict[choice])

    if albums >= collage_size:
        gen_btn.configure(state='normal',fg_color='#125CFF', command=generate)
    else:
        gen_btn.configure(state='normal',fg_color='#FF3333', command=lambda : messagebox.showwarning("Error",f"There are not enough album arts in \"{choice}\" to create a {grid.get()}={collage_size} size cover! "))    
        
    pList.configure(state='normal')
    grid.configure(state='normal')
    bar.stop()
    bar.configure(mode='determinate')
    bar.set(0)

    
def check_grid(choice):
    
    pList.configure(state='disabled')
    grid.configure(state='disabled')
    bar.configure(mode='indeterminate',indeterminate_speed=2)
    bar.start()

    threading.Thread(target=checking_grid_process, args=(access_token,choice)).start()
def checking_grid_process(access_token,choice):
    global playlists_dict   
  
    collage_size = int(choice.split('x')[0]) * int(choice.split('x')[1])
    albums = get_playlist_albums_count(access_token,playlists_dict[pList.get()])

    if albums >= collage_size:
        gen_btn.configure(state='normal',fg_color='#125CFF', command=generate)
    else:
        gen_btn.configure(state='normal',fg_color='#FF3333', command=lambda : messagebox.showwarning("Error",f"There are not enough album arts in \"{pList.get()}\" to create a {choice}={collage_size} size cover! "))      
    
    pList.configure(state='normal')
    grid.configure(state='normal')
    bar.stop()
    bar.configure(mode='determinate')
    bar.set(0)   
    

def generate():   
    threading.Thread(target=generate_process).start()
def generate_process():
    global playlists_dict,access_token,col_image,image_list,grid_length,collage_size,image_length,current_playlist_name,current_grid_size
    
    # configuring the GUI
    pList.configure(state='disabled')
    grid.configure(state='disabled')
    gen_btn.configure(state='disabled',text='Generating')
    bar.configure(mode='indeterminate',indeterminate_speed=2)
    
    # main variables for this part
    grid_length = int(grid.get().split('x')[0])
    collage_size = grid_length ** 2
    image_length = int(2000/grid_length)+1
    
    bar.start()
    
    # getting the image url list
    img_url_list = make_image_url_list(access_token,playlists_dict[pList.get()])
    
    # randomizing the image url list
    random.shuffle(img_url_list)
    img_url_list = img_url_list[:collage_size]
    
    bar.stop()
    bar.configure(mode='determinate')
    bar.set(0)
    
    # making the image object list from the randomized list
    image_list = []
    increment = 1/len(img_url_list)
    v = 0
    for url in img_url_list:
        image_list.append(get_image(url,image_length,image_length))
        v += increment
        bar.set(v)
    bar.set(1)
    
    bar.configure(mode='indeterminate')
    bar.start()
    
    # creating the collage
    col_image = create_collage(image_list,grid_length,image_length)
    
    # displaying the result
    art = CTkImage(dark_image=col_image,size=(360,360))
    art_label.configure(image=art)   
    
    current_playlist_name = pList.get()
    current_grid_size = grid.get()
    
    pList.configure(state='normal')
    grid.configure(state='normal')
    rando.configure(state='normal')
    save.configure(state='normal')
    gen_btn.configure(state='normal',text='Generate')
    bar.stop()
    bar.configure(mode='determinate')
    bar.set(1)


def randomize():
    threading.Thread(target=randomize_process).start()
def randomize_process():
    global image_list,col_image,grid_length
    
    pList.configure(state='disabled')
    grid.configure(state='disabled')
    gen_btn.configure(state='disabled')
    rando.configure(state='disabled')
    bar.configure(mode='indeterminate')
    bar.start()
    
    # randomizing the image list
    random.shuffle(image_list) 
    
    # creating the collage
    col_image = create_collage(image_list,grid_length,image_length)
    
    # displaying the result
    art = CTkImage(dark_image=col_image,size=(360,360))
    art_label.configure(image=art)  
    
    pList.configure(state='normal')
    grid.configure(state='normal')
    gen_btn.configure(state='normal')
    rando.configure(state='normal')
    bar.stop()
    bar.configure(mode='determinate')
    bar.set(1)


def save_image():
    global col_image,current_playlist_name,current_grid_size
    
    file_name = f"{current_playlist_name} {current_grid_size}.png"

    file_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=file_name, filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    
    if file_path:
        try:
            col_image.save(file_path)
            messagebox.showinfo("Saved", f"Your cover image : \"{file_name}\" saved successfully!")
        except:
            messagebox.showerror("Error",f"You cover image : \"{file_name}\" has not been saved!")
        
    
    
##########################################################################################################################################

def get_df_image():
    threading.Thread(target=config_image).start()
def config_image():
    art = CTkImage(dark_image=get_image('https://i.ibb.co/CM82z7N/default-art.png',360,360),size=(360,360))
    art_label.configure(image=art)
    bar.stop()
    bar.configure(mode='determinate')
    bar.set(0)

    
set_appearance_mode("dark")
set_default_color_theme("green")

win = CTk()
win.title('Playlist Cover Maker')
win.geometry('400x550')
win.protocol("WM_DELETE_WINDOW", on_close)
win.resizable(False , False)

info = CTkLabel(win,text='USER | EMAIL',font=('Kristen ITC', 14))
info.place(relx=0.1,rely=0.04)

login = CTkButton(win,text='Login',font=('Arial',17,'bold'),corner_radius=30,border_width=2,border_color='#FFFFFF',width=50,height=40,command=thread_server)
login.place(relx=0.71,rely=0.03,relwidth=0.23)

pList = CTkOptionMenu(win,values=["select a playlist"],state='disabled')
pList.place(relx=0.05,rely=0.13,relwidth=0.45)

grid = CTkOptionMenu(win,values=sizes,state='disabled')
grid.configure(width=50)
grid.place(relx=0.5,rely=0.13,relwidth=0.15)

gen_btn = CTkButton(win,text='Generate',font=('Arial',14,'bold'),fg_color='#125CFF',state='disabled',command=generate,border_width=2,border_color='#FFFFFF')
gen_btn.place(relx=0.695,rely=0.13,relwidth=0.25)

bar = CTkProgressBar(win,indeterminate_speed=2,mode='indeterminate')
bar.place(relx=0.05,rely=0.21,relwidth=0.9,relheight=0.02)
bar.start()

get_df_image()

art_label = CTkLabel(win,text='')
art_label.place(relheight=0.6545, relwidth=0.9, relx=0.05, rely=0.25)

rando =  CTkButton(win,text='randomize',font=('Arial',13,'bold'),width=90,corner_radius=20,border_width=2,border_color='#FFFFFF',command=randomize,state='disabled')
rando.place(relx=0.052,rely=0.925)

save = CTkButton(win,text='SAVE',font=('Arial',13,'bold'),width=70,corner_radius=20,border_width=2,border_color='#FFFFFF',command=save_image,state='disabled')
save.place(relx=0.775,rely=0.925)

win.mainloop()
