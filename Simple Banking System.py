from tkinter import *
import tkinter.messagebox
from tkinter import simpledialog
import os
import sqlite3
import re
import random
import datetime

COLORS = {
    'primary': '#2563EB',           
    'primary_dark': '#1E40AF',      
    'primary_light': '#DBEAFE',     
    'secondary': '#10B981',         
    'danger': '#EF4444',            
    'warning': '#F59E0B',           
    'background': '#F8FAFC',        
    'card': '#FFFFFF',              
    'text_dark': '#1E293B',         
    'text_medium': '#475569',       
    'text_light': '#94A3B8',        
    'border': '#E2E8F0',            
    'shadow': '#CBD5E1'             
}

FONTS = {
    'heading_large': ('Segoe UI', 24, 'bold'),
    'heading': ('Segoe UI', 18, 'bold'),
    'subheading': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 11),
    'body_bold': ('Segoe UI', 11, 'bold'),
    'small': ('Segoe UI', 9),
    'button': ('Segoe UI', 10, 'bold')
}

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
    'xxl': 48
}

def create_primary_button(parent, text, command, width=20):
    return Button(parent, text=text, width=width, font=FONTS['button'],
                  bg=COLORS['primary'], fg='white',
                  activebackground=COLORS['primary_dark'], activeforeground='white',
                  relief='flat', bd=0, cursor='hand2', command=command,
                  padx=SPACING['md'], pady=SPACING['sm'])

def create_secondary_button(parent, text, command, width=20):
    return Button(parent, text=text, width=width, font=FONTS['button'],
                  bg=COLORS['card'], fg=COLORS['primary'],
                  activebackground=COLORS['primary_light'], activeforeground=COLORS['primary_dark'],
                  relief='solid', bd=1, cursor='hand2', command=command,
                  padx=SPACING['md'], pady=SPACING['sm'])

def create_entry_field(parent, show=None):
    return Entry(parent, font=FONTS['body'], bd=1, relief='solid',
                 fg=COLORS['text_dark'], bg=COLORS['card'],
                 highlightthickness=1, highlightcolor=COLORS['primary'],
                 highlightbackground=COLORS['border'], show=show)


def create_registration_table():
    con = sqlite3.connect("ATMdatabase.db")

    cur = con.cursor()
    cur.execute("""
    CREATE TABLE Registration_data(
        Name text,
        gender text,
        age text,
        dob integer,
        Mobile_No text,
        Aadhar_No integer,
        username text,
        Account_number integer,
        PIN integer
    )""")
    con.commit()
    con.close()


def create_transation_table():
    con = sqlite3.connect("ATMdatabase.db")

    cur = con.cursor()
    cur.execute("""
    CREATE TABLE transaction_data(
        username text,
        account_balance integer,
        transactions text
    )""")
    con.commit()
    con.close()

root = Tk()
root.geometry('600x500')
root.resizable(0, 0)

global account_userName
account_userName = StringVar()

def transaction_init():
    global account_userName
    username = account_userName.get()
    acBal = 0
    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
    transactions = f"{time_now}: 0 Account Created|"
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO transaction_data VALUES (?,?,?)", (username, acBal, transactions))
        
    except sqlite3.OperationalError:
        
        create_transation_table()
        cur.execute("INSERT INTO transaction_data VALUES (?,?,?)", (username, acBal, transactions))
    con.commit()
    con.close()


def check_user_exist(un):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT username from Registration_data")
        li = cur.fetchall()

        li = [i for i in li if i[0] == un]
        return len(li)
    except:
        pass


def get_balance(username):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT account_balance from transaction_data WHERE username=?", (username,))
        balance = cur.fetchone()

        return balance[0]
    except TypeError:
        pass


def balanceEnq():
    global account_userName
    bal = get_balance(account_userName.get())
    tkinter.messagebox.showinfo(title=f"Account Balance for {account_userName.get()}",
                                message=f"Your current Balance is Rs. {bal}")


def get_PIN(username):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT PIN FROM Registration_data WHERE username=?", (username,))
        return cur.fetchone()[0]
    except sqlite3.OperationalError:
        pass
    con.close()


def changePIN():
    global account_userName
    username = account_userName.get()
    curPIN = simpledialog.askinteger(title="Change PIN STEP 1/2", prompt="Current PIN:")
    dbPIN = get_PIN(username)

    if curPIN != None:
        if curPIN == dbPIN:
            newPIN = simpledialog.askinteger(title="Change PIN STEP 2/2", prompt="New PIN:")

            con = sqlite3.connect("ATMdatabase.db")
            cur = con.cursor()

            cur.execute("UPDATE Registration_data set PIN = ? WHERE username=?", (newPIN, username))

            con.commit()
            con.close()
            tkinter.messagebox.showinfo(title="Successful", message="PIN Changed Successfully")
        else:
            tkinter.messagebox.showwarning(title="Error", message="Entered PIN is Wrong")


def mini_statement():
    global account_userName
    username = account_userName.get()
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    cur.execute("SELECT transactions FROM transaction_data WHERE username=?", (username,))
    transactions = cur.fetchone()[0]

    transaction_list = transactions.split('|')
    transaction_list = transaction_list[:-1]  

    mini_state = f"Mini Statement of {username}:\n"
    for item in transaction_list:
        mini_state += item + "\n"
    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
    mini_state += f"Clear Balance Rs.{get_balance(username)}-as on {time_now}"
    tkinter.messagebox.showinfo(title="Mini Statement", message=mini_state)


def cash_depo():
    global account_userName
    username = account_userName.get()

    amount_to_add = simpledialog.askinteger(title="Cash Deposit", prompt="Enter Amount:")

    if amount_to_add != None:
        con = sqlite3.connect("ATMdatabase.db")
        cur = con.cursor()
        cur_bal = get_balance(account_userName.get())

        updated_bal = cur_bal + amount_to_add
        cur.execute("UPDATE transaction_data set account_balance = ? WHERE username=?", (updated_bal, username))

        time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
        current_transaction = f"{time_now}: {amount_to_add} Cr|"
        cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (username,))
        past_transaction = cur.fetchone()
        updated_transaction = past_transaction[0] + current_transaction
        cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?", (updated_transaction, username))

        con.commit()
        con.close()
        tkinter.messagebox.showinfo(title="Successful", message="Amount added Successfully")


def cach_withdrawl():
    global account_userName
    username = account_userName.get()

    amount_to_withdrawl = simpledialog.askinteger(title="Cash Withdrawl", prompt="Enter Amount:")

    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    cur_bal = get_balance(account_userName.get())

    try:
        if cur_bal < amount_to_withdrawl:
            tkinter.messagebox.showwarning(title="Error", message="insufficient Balance")
        else:
            updated_bal = cur_bal - amount_to_withdrawl
            cur.execute("UPDATE transaction_data set account_balance = ? WHERE username=?", (updated_bal, username))
            time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
            current_transaction = f"{time_now}: {amount_to_withdrawl} Dr|"
            cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (username,))
            past_transaction = cur.fetchone()
            updated_transaction = past_transaction[0] + current_transaction
            cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",
                        (updated_transaction, username))
            con.commit()
            con.close()
            tkinter.messagebox.showinfo(title="Successful", message="Transaction Successfully")
    except TypeError:
        pass


def transfer():
    global account_userName
    receiver_username = simpledialog.askstring(title="Cash Transfer STEP 1/2", prompt="Username of receiver:")
    if receiver_username != None:

        if check_user_exist(receiver_username) == 0:
            tkinter.messagebox.showwarning(title="Error", message="Account Not Found")

        else:
            sending_amount = simpledialog.askinteger(title="Cash Transfer STEP 1/2",
                                                     prompt="Enter Amount to be transfer:")

            SenderUserName = account_userName.get()
            sender_cur_bal = get_balance(account_userName.get())
            receiver_cur_bal = get_balance(receiver_username)

            try:
                if sending_amount > sender_cur_bal:
                    tkinter.messagebox.showwarning(title="Error", message="insufficient Balance")
                else:
                    sender_updated_amount = sender_cur_bal - sending_amount
                    receiver_updated_amount = receiver_cur_bal + sending_amount

                    con = sqlite3.connect("ATMdatabase.db")
                    cur = con.cursor()
                    cur.execute("UPDATE transaction_data set account_balance = ? WHERE username=?",
                                (sender_updated_amount, SenderUserName))
                    cur.execute("UPDATE transaction_data set account_balance = ? WHERE username=?",
                                (receiver_updated_amount, receiver_username))
                    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
                    sender_current_transaction = f"{time_now}: {sending_amount} Dr Transferred To {receiver_username}|"
                    cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (SenderUserName,))
                    sender_past_transaction = cur.fetchone()  
                    sender_updated_transaction = sender_past_transaction[0] + sender_current_transaction
                    cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",
                                (sender_updated_transaction, SenderUserName))
                    receiver_current_transaction = f"{time_now}: {sending_amount} Cr Transaferred From {SenderUserName}|"
                    cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (receiver_username,))
                    receiver_past_transaction = cur.fetchone()  
                    receiver_updated_transaction = receiver_past_transaction[0] + receiver_current_transaction
                    cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",
                                (receiver_updated_transaction, receiver_username))
                    con.commit()
                    con.close()
                    tkinter.messagebox.showinfo(title="Successful", message="Amount Transferred Successfully")
            except TypeError:
                pass


def generateAcNo(e):
    acNo = random.randint(11111111, 99999999)
    e.delete(0, END)
    e.insert(0, acNo)


def check_acNo_exist(un):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT Account_number from Registration_data")
        li = cur.fetchall()

        un = int(un)
        li = [i for i in li if i[0] == un]
        return len(li)
    except:
        pass


def login(e1, e2):
    global account_userName
    username = e1.get()
    password = e2.get()

    if "" in (username, password):
        tkinter.messagebox.showerror('Error Message', 'Missing fields')
    else:
        try:
            dbPass = get_PIN(username)
            if password == str(dbPass):
                tkinter.messagebox.showinfo('Successful', 'Login Successfully')
                account_userName.set(username)
                main_window()
            else:
                tkinter.messagebox.showerror('Error Message', 'Invalid Username/PIN')
        except:
            tkinter.messagebox.showerror('Error Message', 'Invalid Username/PIN')


def registration_data(en1, en2, en3, en4, en5, en6, en7, en8):
    global account_userName
    pin = random.randint(1111, 9999)
    name = en1.get()

    gender = en2.get()
    if gender == 1:
        gender = "Male"
    elif gender == 2:
        gender = "Female"
    else:
        gender = "Others"

    age = en3.get()
    dob = en4.get()
    cNo = en5.get()
    AdharNo = en6.get()
    Username = en7.get()
    acNo = en8.get()

    if "" in (name, gender, age, dob, cNo, AdharNo, Username, acNo):
        tkinter.messagebox.showerror(title="error", message="Missing Fields")
    else:
        try:
            age = int(age)
            if age < 10:
                tkinter.messagebox.showerror(title="Error", message=f"You are Underage! Wait for {10 - age} years.")
                return
            else:
                if len(cNo) == 10:
                    try:
                        cNo = int(cNo)
                    except ValueError:
                        tkinter.messagebox.showerror(title="Error", message="Mobile Number is invalid")

                    if len(AdharNo) == 12:
                        try:
                            cNo = int(cNo)
                        except ValueError:
                            tkinter.messagebox.showerror(title="Error", message="Aadhar Number is invalid")
                            return

                        if check_user_exist(Username) == 1:
                            tkinter.messagebox.showerror(title="Error", message="Username is already Exist. Try New!")
                            return
                        if check_acNo_exist(acNo) == 1:
                            tkinter.messagebox.showerror(title="Error",
                                                         message="Account Number already Exist. Try New!")
                            return

                        else:
                            account_userName.set(Username)
                            
                            con = sqlite3.connect("ATMdatabase.db")
                            cur = con.cursor()
                            try:
                                cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",
                                            (name, gender, age, dob, cNo, AdharNo, Username, acNo, pin))
                                
                            except sqlite3.OperationalError:
                                
                                create_registration_table()
                                cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",
                                            (name, gender, age, dob, cNo, AdharNo, Username, acNo, pin))
                            con.commit()
                            con.close()
                            tkinter.messagebox.showinfo(title="Successful",
                                                        message=f"Account has been created. You PIN is {pin}")
                            transaction_init()
                            Home()

                    else:
                        tkinter.messagebox.showerror(title="Error", message="Aadhar Number is invalid")
                        return
                else:
                    tkinter.messagebox.showerror(title="Error", message="Mobile Number is invalid")

        except ValueError:
            tkinter.messagebox.showerror(title="Error", message="Age is invalid")


def RegistrationWindow():
    varGen = IntVar()  

    signUpFrame = Frame(root, width=600, height=500, bg=COLORS['background'])
    signUpFrame.place(x=0, y=0)
    root.title("Registration")

    
    headerFrame = Frame(signUpFrame, bg=COLORS['primary'], width=600, height=60)
    headerFrame.place(x=0, y=0)
    
    lblBack = Button(headerFrame, text='← Back', font=FONTS['body_bold'],
                    bg=COLORS['primary'], fg='white',
                    activebackground=COLORS['primary_dark'], activeforeground='white',
                    relief='flat', bd=0, cursor='hand2', command=Home)
    lblBack.place(x=20, y=18)
    
    lblTitle = Label(headerFrame, text='Create Account', 
                    bg=COLORS['primary'], fg='white', font=FONTS['heading'])
    lblTitle.place(x=220, y=18)

    
    cardFrame = Frame(signUpFrame, bg=COLORS['card'], width=560, height=365, relief='flat', bd=1)
    cardFrame.config(highlightbackground=COLORS['border'], highlightthickness=1)
    cardFrame.place(x=20, y=70)

    y_offset = 15
    x_label = 25
    x_entry = 180
    field_height = 45

    
    Label(cardFrame, text='Full Name *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    enName = create_entry_field(cardFrame)
    enName.config(width=38)
    enName.place(x=x_entry, y=y_offset, height=28)

    
    y_offset += field_height
    Label(cardFrame, text='Gender *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    
    genderFrame = Frame(cardFrame, bg=COLORS['card'])
    genderFrame.place(x=x_entry, y=y_offset)
    Radiobutton(genderFrame, text="Male", font=FONTS['body'], bg=COLORS['card'],
                variable=varGen, value=1, cursor='hand2').pack(side=LEFT, padx=5)
    Radiobutton(genderFrame, text="Female", font=FONTS['body'], bg=COLORS['card'],
                variable=varGen, value=2, cursor='hand2').pack(side=LEFT, padx=5)
    Radiobutton(genderFrame, text="Others", font=FONTS['body'], bg=COLORS['card'],
                variable=varGen, value=3, cursor='hand2').pack(side=LEFT, padx=5)

    
    y_offset += field_height
    Label(cardFrame, text='Age *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    enAge = create_entry_field(cardFrame)
    enAge.config(width=16)
    enAge.place(x=x_entry, y=y_offset, height=28)
    
    Label(cardFrame, text='DOB *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=310, y=y_offset)
    enDob = create_entry_field(cardFrame)
    enDob.config(width=17)
    enDob.place(x=365, y=y_offset, height=28)

    
    y_offset += field_height
    Label(cardFrame, text='Mobile Number *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    enCno = create_entry_field(cardFrame)
    enCno.config(width=38)
    enCno.place(x=x_entry, y=y_offset, height=28)

    
    y_offset += field_height
    Label(cardFrame, text='Aadhar Number *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    enAdhar = create_entry_field(cardFrame)
    enAdhar.config(width=38)
    enAdhar.place(x=x_entry, y=y_offset, height=28)

    
    y_offset += field_height
    Label(cardFrame, text='Username *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    enUsername = create_entry_field(cardFrame)
    enUsername.config(width=38)
    enUsername.place(x=x_entry, y=y_offset, height=28)

    
    y_offset += field_height
    Label(cardFrame, text='Account Number *', bg=COLORS['card'], 
          fg=COLORS['text_medium'], font=FONTS['body_bold']).place(x=x_label, y=y_offset)
    enAcNo = create_entry_field(cardFrame)
    enAcNo.config(width=27)
    enAcNo.place(x=x_entry, y=y_offset, height=28)
    
    btnGenerate = Button(cardFrame, text='Generate', font=FONTS['small'],
                        bg=COLORS['primary_light'], fg=COLORS['primary'],
                        activebackground=COLORS['primary'], activeforeground='white',
                        relief='flat', bd=0, cursor='hand2',
                        command=lambda: generateAcNo(enAcNo))
    btnGenerate.place(x=470, y=y_offset, height=28, width=70)

    
    submitButton = create_primary_button(signUpFrame, 'Create Account',
                                        lambda: registration_data(enName, varGen, enAge, enDob, 
                                                                 enCno, enAdhar, enUsername, enAcNo),
                                        width=18)
    submitButton.place(x=150, y=450)
    
    resetButton = create_secondary_button(signUpFrame, 'Reset', RegistrationWindow, width=15)
    resetButton.place(x=320, y=450)

    signUpFrame.mainloop()



def main_window():
    global account_userName
    mainFrame = Frame(root, width=600, height=500, bg=COLORS['background'])
    mainFrame.place(x=0, y=0)
    root.title("Account Dashboard")

    
    navFrame = Frame(mainFrame, bg=COLORS['primary'], width=600, height=60)
    navFrame.place(x=0, y=0)
    
    lblBrand = Label(navFrame, text='🏦 Banking', bg=COLORS['primary'], 
                    fg='white', font=FONTS['heading'])
    lblBrand.place(x=20, y=15)
    
    
    userInfoFrame = Frame(navFrame, bg=COLORS['primary_dark'], width=170, height=45, 
                         relief='flat', bd=0)
    userInfoFrame.place(x=410, y=8)
    
    Label(userInfoFrame, text='Welcome!', bg=COLORS['primary_dark'], 
          fg='white', font=FONTS['small']).place(x=10, y=5)
    Label(userInfoFrame, text=account_userName.get(), bg=COLORS['primary_dark'], 
          fg='white', font=FONTS['body_bold']).place(x=10, y=22)

    
    Label(mainFrame, text='Dashboard', bg=COLORS['background'], 
          fg=COLORS['text_dark'], font=FONTS['subheading']).place(x=25, y=75)

    
    card_width = 260
    card_height = 85
    gap = 15
    start_x = 25
    start_y = 110

    
    def create_service_card(parent, x, y, icon, title, command):
        
        Frame(parent, bg=COLORS['shadow'], width=card_width+3, height=card_height+3).place(x=x+2, y=y+2)
        
        
        card = Frame(parent, bg=COLORS['card'], width=card_width, height=card_height,
                    relief='flat', bd=1, cursor='hand2')
        card.config(highlightbackground=COLORS['border'], highlightthickness=1)
        card.place(x=x, y=y)
        
        
        Label(card, text=icon, bg=COLORS['card'], font=('Segoe UI', 20)).place(x=15, y=25)
        
        
        Label(card, text=title, bg=COLORS['card'], fg=COLORS['text_dark'],
              font=FONTS['body_bold'], anchor='w').place(x=60, y=20)
        
        
        Label(card, text='Click to access', bg=COLORS['card'], 
              fg=COLORS['text_light'], font=FONTS['small']).place(x=60, y=42)
        
        
        btn = Button(card, text='→', font=('Segoe UI', 14, 'bold'),
                    bg=COLORS['primary'], fg='white',
                    activebackground=COLORS['primary_dark'], activeforeground='white',
                    relief='flat', bd=0, cursor='hand2', command=command,
                    width=3, height=1)
        btn.place(x=210, y=25)
        
        return card

    
    create_service_card(mainFrame, start_x, start_y, '💰', 'Balance Enquiry', balanceEnq)
    create_service_card(mainFrame, start_x + card_width + gap, start_y, '📊', 'Mini Statement', mini_statement)

    
    create_service_card(mainFrame, start_x, start_y + card_height + gap, '🔐', 'Change PIN', changePIN)
    create_service_card(mainFrame, start_x + card_width + gap, start_y + card_height + gap, '💵', 'Cash Withdrawal', cach_withdrawl)

    
    create_service_card(mainFrame, start_x, start_y + (card_height + gap) * 2, '📥', 'Cash Deposit', cash_depo)
    create_service_card(mainFrame, start_x + card_width + gap, start_y + (card_height + gap) * 2, '💸', 'Transfer Funds', transfer)

    
    logoutBtn = Button(mainFrame, text='Logout', font=FONTS['button'],
                      bg=COLORS['danger'], fg='white',
                      activebackground='#DC2626', activeforeground='white',
                      relief='flat', bd=0, cursor='hand2', command=Home,
                      width=15, padx=SPACING['sm'], pady=SPACING['xs'])
    logoutBtn.place(x=235, y=460)

    mainFrame.mainloop()


def Home():
    mainFrame = Frame(root, height=500, width=600, bg=COLORS['background'])
    mainFrame.place(x=0, y=0)

    
    brandFrame = Frame(mainFrame, bg=COLORS['primary'], width=600, height=100)
    brandFrame.place(x=0, y=0)
    
    
    lblIcon = Label(brandFrame, text='🏦', bg=COLORS['primary'], font=('Segoe UI', 32))
    lblIcon.place(x=275, y=10)
    
    lblTitle = Label(brandFrame, text='Simple Banking System', 
                    bg=COLORS['primary'], fg='white', font=FONTS['heading'])
    lblTitle.place(x=180, y=60)

    shadowFrame = Frame(mainFrame, bg=COLORS['shadow'], width=384, height=284)
    shadowFrame.place(x=111, y=133)
    
    cardFrame = Frame(mainFrame, bg=COLORS['card'], width=380, height=280, relief='flat', bd=0)
    cardFrame.place(x=110, y=130)

    lblWelcome = Label(cardFrame, text='Sign In', bg=COLORS['card'], 
                      fg=COLORS['text_dark'], font=FONTS['heading'])
    lblWelcome.place(x=40, y=25)
    
    lblSubtext = Label(cardFrame, text='Access your account', bg=COLORS['card'], 
                      fg=COLORS['text_light'], font=FONTS['body'])
    lblSubtext.place(x=40, y=55)

    lblAcNo = Label(cardFrame, text='Username', bg=COLORS['card'], 
                   fg=COLORS['text_medium'], font=FONTS['body_bold'])
    lblAcNo.place(x=40, y=90)

    enUser = create_entry_field(cardFrame)
    enUser.config(width=35)
    enUser.place(x=40, y=115, height=32)

    lblPIN = Label(cardFrame, text='PIN', bg=COLORS['card'], 
                  fg=COLORS['text_medium'], font=FONTS['body_bold'])
    lblPIN.place(x=40, y=155)

    enPass = create_entry_field(cardFrame, show='●')
    enPass.config(width=35)
    enPass.place(x=40, y=180, height=32)

    loginButton = create_primary_button(cardFrame, 'Sign In', 
                                       lambda: login(enUser, enPass), width=30)
    loginButton.place(x=40, y=230)

    createAccountFrame = Frame(mainFrame, bg=COLORS['background'], width=380, height=40)
    createAccountFrame.place(x=110, y=425)
    
    lblNewUser = Label(createAccountFrame, text="Don't have an account?", 
                      bg=COLORS['background'], fg=COLORS['text_medium'], font=FONTS['body'])
    lblNewUser.place(x=70, y=10)
    
    btnSignUp = Button(createAccountFrame, text='Create Account', font=FONTS['body_bold'],
                      bg=COLORS['background'], fg=COLORS['primary'],
                      activebackground=COLORS['background'], activeforeground=COLORS['primary_dark'],
                      relief='flat', bd=0, cursor='hand2', command=RegistrationWindow)
    btnSignUp.place(x=240, y=8)

    mainFrame.mainloop()

Home()
