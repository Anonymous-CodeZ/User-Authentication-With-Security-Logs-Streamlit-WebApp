import streamlit as st
from streamlit_option_menu import option_menu
import datetime
import re
import email_request
import sqlite3
import os
from itertools import chain
import hashlib
import secrets

db_path = "data/database.db"
if not os.path.exists(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)

def initialize():
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username CHAR(50) NOT NULL,
            password CHAR(50) NOT NULL,
            email CHAR NOT NULL,
            date_created CHAR(50) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Logs (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            datetime_logged CHAR(50) NOT NULL,
            username CHAR(50) NOT NULL,
            log_type CHAR(50) NOT NULL
        );
    ''')

    conn.commit()

initialize()

def insert_user(email, username, password):
    command = f'''
    INSERT INTO User (username, password, email, date_created)
    VALUES ('{username}', '{password}', '{email}', '{str(datetime.datetime.now())}')
    '''
    conn.execute(command)
    conn.commit()

def delete_user(username): 
    conn.execute(f"DELETE FROM User WHERE username = '{username}'")
    conn.commit()

def change_password(email, password):
    new_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    username = conn.execute(f"SELECT username FROM User WHERE email = '{email}'").fetchone()[0]
    print(username, new_password)
    conn.execute(f"DELETE FROM User WHERE email = '{email}'")
    conn.commit()

    command = f'''
    INSERT INTO User (username, password, email, date_created)
    VALUES ('{username}', '{new_password}', '{email}', '{str(datetime.datetime.now())}')
    '''
    conn.execute(command)
    conn.commit()
    return(True)

def recreate(email, username, password):
    conn.execute(f"DELETE FROM User WHERE username = '{username}'")
    conn.commit()

    #Recreating the User Account
    command = f'''
    INSERT INTO User (username, password, email, date_created)
    VALUES ('{username}', '{password}', '{email}', '{str(datetime.datetime.now())}')
    '''
    conn.execute(command)
    conn.commit()   
    return True

def fetch_users():
    return conn.execute("SELECT * FROM User").fetchall()

def get_user_emails():
    return list(chain.from_iterable(conn.execute("SELECT email FROM User").fetchall()))

def get_usernames():
    return list(chain.from_iterable(conn.execute("SELECT username FROM User").fetchall()))

def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$" #tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False

def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """
    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False

def validate_password_wemail(email='', password=''):
    if email in list(chain.from_iterable(conn.execute("SELECT email FROM User").fetchall())):
        hashed_password = conn.execute(f"SELECT password from User WHERE email = '{email}'").fetchone()[0]
        if hashed_password == password:
            return True
    return False

def generate_random_passwd() -> str:
    """
    Generates a random password to be sent in email.
    """
    password_length = 10
    return secrets.token_urlsafe(password_length)

def insert_login_act(username): 
    command = f'''
    INSERT INTO Logs (datetime_logged, username, log_type)
    VALUES ('{str(datetime.datetime.now())}','{username}', 'logged in')
    '''
    conn.execute(command)
    conn.commit()

def insert_logout_act(username):
    command = f'''
    INSERT INTO Logs (datetime_logged, username, log_type)
    VALUES ('{str(datetime.datetime.now())}','{username}', 'logged out')
    '''
    conn.execute(command)
    conn.commit()

def scan_login():
    status = list(chain.from_iterable(conn.execute("SELECT log_type from Logs").fetchall()))[-1]
    if status == 'logged in':
        return True
    return False

def home():
    if scan_login() == True:
        st.title("This is a Home Page")
        st.subheader("You are now logged in")
    
    else:
        st.title("Please Log in to continue!")

def sign_up():
    if scan_login() == False:
        st.title("Already Have An Account? Log in")
        with st.form(key='signup', clear_on_submit=True):
            st.subheader(':green[Sign Up]')
            email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
            username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
            password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
            password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

            if email:
                if validate_email(email):
                    if email not in get_user_emails():
                        if validate_username(username):
                            if username not in get_usernames():
                                if len(username) >= 2:
                                    if len(password1) >= 6:
                                        if password1 == password2:
                                            # Add User to DB
                                            password_bytes = password2.encode('utf-8')
                                            hashed_password = hashlib.sha256(password_bytes).hexdigest()
                                
                                            insert_user(email, username, hashed_password)
                                            st.success('Account created successfully!!')
                                            st.balloons()
                                        else:
                                            st.warning('Passwords Do Not Match')
                                    else:
                                        st.warning('Password is too Short')
                                else:
                                    st.warning('Username Too short')
                            else:
                                st.warning('Username Already Exists')

                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Email Already exists!!')
                else:
                    st.warning('Invalid Email')
            
            btn1, bt2, btn3, btn4, btn5 = st.columns(5)

            with btn3:
                st.form_submit_button('Sign Up')
    else:
        st.title("You are already Logged in!")
        
def forgot_password():
    st.title("Account Recovery")
    with st.form("Forgot Password Form", clear_on_submit=True):
            email_forgot_passwd = st.text_input(':blue[Email]', placeholder='Enter Your Email')
            email_exists_check = True if email_forgot_passwd in get_user_emails() else False

            st.markdown("###")
            forgot_passwd_submit_button = st.form_submit_button(label = 'Get Password')

            if forgot_passwd_submit_button:
                if email_exists_check == False:
                    st.error("Email ID not registered with us!")

                if email_exists_check == True:
                    random_password = generate_random_passwd()
                    email_request.sendmail(email_forgot_passwd, random_password)
                    change_password(email_forgot_passwd, random_password)
                    st.success("Secure Password Sent Successfully!")
                    st.balloons()


def login():
    if scan_login() == False:
        st.title("Don't have an account? Sign Up")
        with st.form(key='login', clear_on_submit=True):
            st.subheader(':green[Log In]')
            email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
            username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
            password = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
            
            if email:
                if validate_email(email):
                    if email in get_user_emails():
                        if validate_username(username):
                            if username in get_usernames():
                                if password:
                                    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

                                    #Confirm password with the database
                                    if validate_password_wemail(email, hashed) == True:
                                        st.success("Logging In...")
                                        insert_login_act(username)
                                        st.balloons()
                                    else:
                                        st.warning('Password Does Not Match')
                                else:
                                    st.warning('Please Enter Your Password')
                            else:
                                st.warning('Username Does Not Exists')
                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Email Does Not Exists!!')
                else:
                    st.warning('Invalid Email')

            btn1, bt2, btn3, btn4, btn5 = st.columns(5)

            with btn3:
                st.form_submit_button('Log In')       
    else:
        st.title("You are already Logged in!")

def reset_password():
    st.title("Reset Account Password")
    with st.form("Reset Password Form", clear_on_submit=True):
        st.subheader(':green[Reset Your Password]')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Current Password]', placeholder='Enter Your Current Password', type='password')
        password2 = st.text_input(':blue[Current Password]', placeholder='Re-Enter Your Current Password', type='password')
        newpw1 = st.text_input(':blue[New Password]', placeholder='Enter Your New Password', type='password', key= '1')
        newpw2 = st.text_input(':blue[New Password]', placeholder='Re-Enter Your New Password', type='password', key= '2')

        if email:
            if validate_email(email):
                if email in get_user_emails():
                    if validate_username(username):
                        if username in get_usernames():
                            if password1 == password2:
                                hashed = hashlib.sha256(password1.encode('utf-8')).hexdigest()
                                #Confirm password with the database
                                if validate_password_wemail(email, hashed) == True:
                                    if newpw1:
                                        if newpw2:
                                            if newpw1 == newpw2:
                                                hashpw = hashlib.sha256(newpw1.encode('utf-8')).hexdigest()

                                                st.success("Processing...")

                                                print(recreate(email, username, hashpw))
                                                print(email, username, hashpw)
                                                if recreate(email, username, hashpw) == True:
                                                    print(recreate(email, username, hashpw))
                                                    st.success("Password Successfully Updated")
                                                    st.balloons()

                                            else:
                                                st.warning('New Password Does Not Match')
                                        else:
                                            st.warning('Reenter New Password')
                                else:
                                    st.warning('Password Does Not Match')
                            
                            else:
                                st.warning('Make Sure Both Passwords Match')
                        else:
                            st.warning('Username Does Not Exists')
                    else:
                        st.warning('Invalid Username')
                else:
                    st.warning('Email Does Not Exists!!')
            else:
                st.warning('Invalid Email')

        btn1, bt2, btn3, btn4, btn5 = st.columns(5)

        with btn3:
            st.form_submit_button('Submit')

def logout():
    try:
        status = list(chain.from_iterable(conn.execute("SELECT log_type FROM Logs").fetchall()))[-1]

        if status == 'logged in':
            st.title("You are now Logged Out!")
            username = list(chain.from_iterable(conn.execute("SELECT username FROM Logs WHERE log_type = 'logged in'").fetchall()))[-1]
            insert_logout_act(username)
            st.balloons()

        elif status == 'logged out':
            st.title("You are not yet Logged In")
    except IndexError:
        st.title("You are not yet Logged In")

#main
st.sidebar.title("Welcome To My Page")
st.sidebar.caption("User Authentication with Security Logs Streamlit App")
st.sidebar.markdown("---")


main_page_sidebar = st.sidebar.empty()
with main_page_sidebar:
    selected_option = option_menu(
        menu_title = 'Navigation',
        menu_icon = 'list-columns-reverse',
        icons = ['menu-up','box-arrow-in-right', 'person-plus', 'x-circle','arrow-counterclockwise', 'box-arrow-in-left'],
        options = ['Home','Login', 'Create Account', 'Forgot Password?', 'Reset Password', 'Log Out'],
        styles = {
            "container": {"padding": "5px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px"}} ) 
st.sidebar.markdown("---")
st.sidebar.subheader("Created By")
st.sidebar.caption("Savakroth LEAV - Github: ")
st.sidebar.markdown("---")

if selected_option == 'Home':
    st.session_state.page = 'home_page'
elif selected_option == 'Create Account':
    st.session_state.page = 'signup_page'
elif selected_option == 'Login':
    st.session_state.page = 'login_page'
elif selected_option == 'Forgot Password?':
    st.session_state.page = 'forgot_pw'
elif selected_option == 'Reset Password':
    st.session_state.page = 'reset_pw'
elif selected_option == 'Log Out':
    st.session_state.page = 'logout_page'

if st.session_state.page == "home_page":
    home()
elif st.session_state.page == "signup_page":    
    sign_up()
elif st.session_state.page == "login_page":
    login()
elif st.session_state.page == "forgot_pw":
    forgot_password()
elif st.session_state.page == "reset_pw":
    reset_password()
elif st.session_state.page == "logout_page":
    logout()
