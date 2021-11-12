import streamlit as st
import dashboard
# Page layout

def main():
    st.title("""Machine Learning Recommendation Dashboard""")
    dashboard.app()

if __name__ == '__main__':
        main()