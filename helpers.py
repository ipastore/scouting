import streamlit as st

# ######################
#Clear Cache
def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)