import streamlit_authenticator as stauth

passwords = ['demo123']
hashed = stauth.Hasher(passwords).generate()
print(hashed)
