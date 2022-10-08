import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import en_core_web_sm
nlp = en_core_web_sm.load()

conn = sqlite3.connect("data.db")
c = conn.cursor()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')

def add_data(author,title,article,postdate):
    c.execute('INSERT INTO blogtable(author,title,article,postdate) VALUES (?,?,?,?)',(author,title,article,postdate))
    conn.commit()

def view_all_notes():
	c.execute('SELECT * FROM blogtable')
	data = c.fetchall()
	return data

def view_all_titles():
	c.execute('SELECT DISTINCT title FROM blogtable')
	data = c.fetchall()
	return data

def get_blog_by_title(title):
	c.execute('SELECT * FROM blogtable WHERE title="{}"'.format(title))
	data = c.fetchall()
	return data

def get_blog_by_author(author):
	c.execute('SELECT * FROM blogtable WHERE author="{}"'.format(author))
	data = c.fetchall()
	return data

def delete_data(title):
	c.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
	conn.commit()

# Reading Time
def readingTime(mytext):
	total_words = len([ token for token in mytext.split(" ")])
	estimatedTime = total_words/200.0
	return estimatedTime

def analyze_text(text):
	return nlp(text)

# Layout templete
title_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
	<h4 style="color:white;text-align:center;">{}</h1>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
	<h6>Author:{}</h6>
	<br/>
	<br/>	
	<p style="text-align:justify">{}</p>
	</div>
	"""
article_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
	<h4 style="color:white;text-align:center;">{}</h1>
	<h6>Author:{}</h6> 
	<h6>Post Date: {}</h6>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;" >
	<br/>
	<br/>
	<p style="text-align:justify">{}</p>
	</div>
	"""
head_message_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
	<h4 style="color:white;text-align:center;">{}</h1>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
	<h6>Author:{}</h6> 		
	<h6>Post Date: {}</h6>		
	</div>
	"""
full_message_temp ="""
	<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
		<p style="text-align:justify;color:white;padding:10px">{}</p>
	</div>
	"""

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""

def main():
    st.title("Zuko Blogs")

    menu = ["Home","View Posts","Add Post","Search","Manage Blog"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Home":
        st.subheader("Home")
        result = view_all_notes()

        for i in result:
            b_author = i[0]
            b_title = i[1]
            b_article = str(i[2])[0:100]
            b_post_date = i[3]
            st.markdown(title_temp.format(b_author,b_title,b_article,b_post_date),unsafe_allow_html=True)

    elif choice == "View Posts":
        st.subheader("View Posts")
        all_titles = [i[0] for i in view_all_titles()]
        postlist = st.sidebar.selectbox("View Posts",all_titles)
        post_result = get_blog_by_title(postlist)
        for i in post_result:
            b_author = i[0]
            b_title = i[1]
            b_article = i[2]
            b_post_date = i[3]
            st.text("Reading Time:{} minutes".format(readingTime(str(i[2]))))
            st.markdown(head_message_temp.format(i[1], i[0], i[3]), unsafe_allow_html=True)
            st.markdown(full_message_temp.format(i[2]), unsafe_allow_html=True)

    elif choice == "Add Post":
        st.subheader("Add Post")
        create_table()

        blog_author = st.text_input("Enter the name of author",max_chars=50)
        blog_title = st.text_input("Enter Post title")
        blog_article = st.text_area("Post article here", height=200)
        blog_post_date = st.date_input("Date")

        if st.button("Add"):
            add_data(blog_author,blog_title,blog_article,blog_post_date)
            st.success("Post : {} Saved".format(blog_title))


    elif choice == "Search":

        st.subheader("Search Articles")

        search_term = st.text_input("Enter Term")

        search_choice = st.radio("Field to Search", ("title", "author"))

        if st.button('Search'):

            if search_choice == "title":

                article_result = get_blog_by_title(search_term)

            elif search_choice == "author":

                article_result = get_blog_by_author(search_term)

            # Preview Articles

            for i in article_result:
                st.text("Reading Time:{} minutes".format(readingTime(str(i[2]))))

                # st.write(article_temp.format(i[1],i[0],i[3],i[2]),unsafe_allow_html=True)

                st.write(head_message_temp.format(i[1], i[0], i[3]), unsafe_allow_html=True)

                st.write(full_message_temp.format(i[2]), unsafe_allow_html=True)



    elif choice == "Manage Blog":

        st.subheader("Manage Blog")

        result = view_all_notes()
        clean_db = pd.DataFrame(result,columns=["Author","Title","Article"," Post Date"])
        st.dataframe(clean_db)
        unique_list = [i[0] for i in view_all_titles()]
        delete_by_title = st.selectbox("Select Title", unique_list)
        if st.button("Delete"):
            delete_data(delete_by_title)
            st.warning("Deleted: '{}'".format(delete_by_title))



if __name__ == '__main__':
    main()