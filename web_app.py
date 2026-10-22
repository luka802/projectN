"""Run with: streamlit run web_app.py (from the assignments directory)."""
import streamlit as st

from common.llm import ServiceError
from movie_finder.search import MovieFinder
from travel_buddy.bot import TravelBuddy

st.set_page_config(page_title='Weekend & Watchlist', page_icon='🎬', layout='centered')
st.title('Weekend & Watchlist')
st.caption('Plan a little adventure. Find a great story.')
page = st.sidebar.radio('Explore', ['TravelBuddy', 'Movie Finder'])
st.sidebar.caption('Python • OpenRouter • MiniLM • Pinecone')

if page == 'TravelBuddy':
    st.header('Your next weekend starts here')
    st.write('Three simple choices. One lovely getaway.')
    if 'travel' not in st.session_state:
        st.session_state.travel = TravelBuddy()
        st.session_state.travel.start()
    bot = st.session_state.travel
    if st.button('Start a new trip'):
        st.session_state.travel = TravelBuddy()
        st.session_state.travel.start()
        st.rerun()
    st.progress(len(bot.choices) / 3, text=f'{len(bot.choices)} of 3 choices confirmed')
    for message in bot.history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    if bot.closed:
        st.info('This conversation has ended. Start a new trip whenever you like.')
    else:
        selected = None
        if bot.options:
            columns = st.columns(3)
            for i, option in enumerate(bot.options):
                if columns[i].button(option, key=f'choice-{len(bot.choices)}-{i}', use_container_width=True):
                    selected = option
        typed = st.chat_input('Choose an option, describe your preference, or type exit')
        if selected or typed:
            with st.spinner('Planning your getaway...'):
                bot.reply(selected or typed)
            st.rerun()
else:
    st.header('Find your next favorite film')
    st.write('Search by mood, story, genre, or director across a curated collection of 30 movies.')
    rag = st.toggle('Add an AI recommendation', value=False,
                    help='Uses OpenRouter to explain only the movies retrieved from Pinecone.')
    with st.form('movie-query'):
        query = st.text_input('What are you in the mood for?', placeholder='A feel-good movie about friendship')
        submitted = st.form_submit_button('Find movies', type='primary')
    st.caption('Try: “something scary to watch tonight” or “movies by Christopher Nolan”.')

    @st.cache_resource
    def get_finder():
        finder = MovieFinder()
        finder.sync()
        return finder

    if submitted:
        if query.strip().casefold() == 'exit':
            st.info('Goodbye! Enjoy your next movie.')
        elif not query.strip():
            st.warning('Enter a mood, genre, story, or director first.')
        else:
            try:
                with st.spinner('Searching the collection. The first run may download MiniLM...'):
                    finder = get_finder()
                    movies = finder.search(query)
                if not movies:
                    st.info("I couldn't find any matching movies. Try another description.")
                for movie in movies:
                    with st.container(border=True):
                        st.subheader(f'{movie["title"]} ({movie["year"]})')
                        st.caption(f'{movie["director"]} · {movie["genre"]}')
                        st.write(movie['description'])
                        st.caption(f'Cosine similarity: {movie["score"]:.3f}')
                if rag and movies:
                    try:
                        with st.spinner('Writing your recommendation...'):
                            recommendation = finder.recommend(query, movies)
                        st.markdown('### Why these films?')
                        st.write(recommendation)
                    except ServiceError as exc:
                        st.warning(f'AI recommendation unavailable: {exc}. Your search results are still available above.')
            except Exception as exc:
                st.error(f'Could not search: {exc}')
                st.caption('Check your local .env configuration and connection, then try again.')
