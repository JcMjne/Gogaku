import streamlit as st
import numpy as np
import requests,json,os

request=st.text_area("Any specific requests for the language model?",'',)
st.write(request)