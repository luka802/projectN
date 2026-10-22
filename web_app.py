"""Streamlit interface. Run: python -m streamlit run web_app.py."""
from html import escape
from pathlib import Path
import streamlit as st
from common.llm import ServiceError
from movie_finder.search import MovieFinder
from travel_buddy.bot import TravelBuddy

ASSETS = Path(__file__).with_name('assets')
st.set_page_config(page_title='Weekend & Watchlist', page_icon='✦', layout='centered')
st.markdown(f'<style>{(ASSETS / "style.css").read_text(encoding="utf-8")}</style>', unsafe_allow_html=True)
CHOICE_DETAILS = {
    'Beach': ('☀', 'Salt air, slow mornings, and a little sunshine.', '#f3e3bc'),
    'Mountains': ('△', 'Fresh air, open trails, and room to breathe.', '#dce8d6'),
    'City break': ('▥', 'Good food, hidden corners, and something new.', '#eadbcf'),
    'Cozy guesthouse': ('⌂', 'A welcoming little place to call your own.', '#e8dfca'),
    'Boutique hotel': ('✦', 'Thoughtful details and a little extra comfort.', '#e6dce5'),
    'Camping': ('△', 'Sleep close to nature, wake up to the outdoors.', '#dce8d6'),
    'Snorkeling': ('≈', 'Discover a different world beneath the surface.', '#d5e8e5'),
    'Sunset beach walk': ('☀', 'Take the scenic route as the sky turns gold.', '#f1dfbd'),
    'Coastal boat tour': ('≋', 'A new perspective on a beautiful coastline.', '#dbe5e7'),
    'Scenic hiking': ('△', 'Follow a trail to a view worth the walk.', '#dce8d6'),
    'Wildlife watching': ('❋', 'Slow down and see who shares the landscape.', '#e7e6cc'),
    'Stargazing': ('✧', 'A quiet night beneath a sky full of stars.', '#dce1ec'),
    'Museum tour': ('▥', 'A little history, art, and fresh perspective.', '#e8dfca'),
    'Local food walk': ('◉', 'Get to know a city one delicious stop at a time.', '#f0ddce'),
    'Historic neighborhood stroll': ('⌂', 'Wander streets with a story around every corner.', '#dce8d6'),
}

def html(content):
    st.markdown(content, unsafe_allow_html=True)

def hero(kind, eyebrow, title, description, facts):
    left, right = st.columns([1.15, 1], gap='large', vertical_alignment='center')
    with left:
        html(f'<div class="eyebrow">{eyebrow}</div>')
        html('<h1>' + escape(title).replace('\n', '<br>') + '</h1>')
        html(f'<div class="hero-copy">{description}</div><div class="hero-facts">' + ''.join(f'<span>{escape(f)}</span>' for f in facts) + '</div>')
    with right:
        svg = (ASSETS / f'{kind}.svg').read_text(encoding='utf-8')
        html(f'<div class="hero-art">{svg}</div>')

@st.cache_resource(show_spinner=False)
def get_finder():
    finder = MovieFinder()
    finder.sync()
    return finder

def queue_query(query):
    st.session_state.movie_input = query
    st.session_state.queued_query = query

def render_movie(movie, rank):
    palettes = [('#d9e5d4', '#285b50'), ('#edddc4', '#8f5c35'), ('#dedee9', '#545875')]
    background, ink = palettes[(rank - 1) % len(palettes)]
    title = escape(movie['title'])
    html(f'''<article class="movie-card">
      <div class="movie-cover" aria-hidden="true" style="--cover:{background};--cover-ink:{ink}"><span>{rank:02}</span></div>
      <div><div class="movie-topline">Your {'closest match' if rank == 1 else 'next pick'} · {int(movie['year'])}</div>
      <h3 class="movie-title">{title}</h3>
      <div class="movie-meta">Directed by {escape(movie['director'])}</div>
      <p class="movie-description">{escape(movie['description'])}</p>
      <span class="movie-genre">{escape(movie['genre'])}</span></div>
    </article>''')

html('<div class="brand"><div class="brand-name"><span class="brand-mark" aria-hidden="true">✦</span> Weekend &amp; Watchlist</div><div class="brand-note">Make room for a good time</div></div>')
page = st.radio('Choose your experience', ['Plan a getaway', 'Find a film'], horizontal=True, label_visibility='collapsed', key='experience')

if page == 'Plan a getaway':
    hero('travel', 'A change of scenery', 'Small escape.\nBig reset.',
         'Some weekends deserve a different view. Find your kind of getaway, one simple choice at a time.',
         ['3 simple steps', 'Made for your mood', 'No bookings needed'])
    if 'travel' not in st.session_state:
        st.session_state.travel = TravelBuddy()
        st.session_state.travel.start()
    bot = st.session_state.travel
    stage = len(bot.choices)
    labels = ['The setting', 'Your stay', 'The experience']
    html('<div class="steps">' + ''.join(
        f'<div class="step {"done" if stage > i else "active" if stage == i else ""}"><b>{"✓" if stage > i else f"0{i+1}"}</b> {label}</div>'
        for i, label in enumerate(labels)) + '</div>')
    if bot.choices:
        html('<div class="hero-facts">' + ''.join(f'<span>✓ {escape(c)}</span>' for c in bot.choices) + '</div>')
    if st.session_state.get('travel_notice'):
        st.warning(st.session_state.pop('travel_notice'))
    if bot.complete:
        html('<div class="itinerary"><div class="tag">YOUR WEEKEND, SORTED</div><h3>A little adventure to look forward to.</h3>' +
             ''.join(f'<div class="itinerary-row"><span>{label}</span><b>{escape(value)}</b></div>'
                     for label, value in zip(['Setting', 'Stay', 'Experience'], bot.choices)) + '</div>')
        st.download_button('Save your weekend plan ↓', data=bot.summary(), file_name='my-weekend-plan.txt', mime='text/plain', use_container_width=True)
        st.caption('An idea for your weekend, ready to make your own. Accommodation and activities are suggestions; nothing is booked.')
    elif bot.closed:
        st.info('Happy travels! Start a new trip whenever inspiration strikes.')
    else:
        headings = ['Where would you rather be?', 'Find your home away from home.', 'Make a little memory.']
        notes = ['Pick the setting that feels like your kind of weekend.', 'Choose a place that suits your pace.', 'These experiences are chosen to fit your destination.']
        html(f'<div class="section-label">{headings[stage]}</div><div class="section-note">{notes[stage]}</div>')
        selected = None
        columns = st.columns(3, gap='medium')
        for i, option in enumerate(bot.options):
            icon, description, color = CHOICE_DETAILS[option]
            with columns[i]:
                with st.container(border=True):
                    html(f'<div class="choice-art" aria-hidden="true" style="--tile:{color}">{icon}</div><div class="choice-title">{escape(option)}</div><div class="choice-description">{description}</div>')
                    if st.button(f'Choose {option}', key=f'choice-{stage}-{i}', use_container_width=True, type='primary'):
                        selected = option
        st.caption('Have something in mind? You can describe your preference below, too.')
        with st.form('travel-preference', clear_on_submit=True):
            preference = st.text_input('Or tell TravelBuddy what you like', placeholder='For example: somewhere with fresh mountain air', max_chars=1000)
            send = st.form_submit_button('Send preference →', use_container_width=True)
        answer = selected or (preference if send else None)
        if answer is not None:
            before = len(bot.choices)
            with st.spinner('A little planning magic...'):
                response = bot.reply(answer)
            if len(bot.choices) == before and not bot.closed and answer.casefold().strip() != 'restart':
                st.session_state.travel_notice = response.split("Let's choose", 1)[0].strip()
            st.rerun()
    controls = st.columns(2)
    if controls[0].button('← Back a step', disabled=not bot.choices or bot.closed, use_container_width=True):
        bot.back()
        st.rerun()
    if controls[1].button('Start a new trip ↗', use_container_width=True):
        st.session_state.travel = TravelBuddy()
        st.session_state.travel.start()
        st.session_state.pop('travel_notice', None)
        st.rerun()
    with st.expander('Your conversation'):
        st.caption('Your choices stay in this session. Type exit in the preference field to end the conversation.')
        for message in bot.history:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
else:
    hero('cinema', 'Something worth watching', 'Less scrolling.\nMore cinema.',
         'A mood, a favorite director, a story you need right now. Tell us what sounds good; we’ll find a few films to match.',
         ['30 handpicked films', 'Search in your own words', 'A little help choosing'])
    if 'movie_input' not in st.session_state:
        st.session_state.movie_input = st.session_state.get('last_movie_query', '')
    with st.form('movie-query'):
        query = st.text_input('What are you in the mood for?', placeholder='A feel-good movie about friendship', key='movie_input', max_chars=1000)
        submitted = st.form_submit_button('Find my next film →', type='primary', use_container_width=True)
    st.caption('A few ideas to get you started')
    suggestions = st.columns(3)
    examples = [('A little suspense', 'something scary to watch tonight'), ('A Nolan night', 'movies by Christopher Nolan'), ('Something feel-good', 'a feel-good movie about friendship')]
    for column, (label, example) in zip(suggestions, examples):
        column.button(label, on_click=queue_query, args=(example,), use_container_width=True)
    requested = st.session_state.pop('queued_query', None)
    if submitted:
        requested = query.strip()
    if requested is not None:
        if not requested.strip():
            st.warning('Tell us a little about what you want to watch, or try one of the ideas above.')
        elif requested.strip().casefold() == 'exit':
            st.session_state.pop('movie_results', None)
            st.session_state.pop('last_movie_query', None)
            st.info('Enjoy your next movie. Come back whenever you need another idea.')
        else:
            try:
                with st.spinner('Finding a few good stories...'):
                    finder = get_finder()
                    movies = finder.search(requested)
                st.session_state.movie_results = movies
                st.session_state.last_movie_query = requested
                st.session_state.pop('movie_recommendation', None)
            except Exception:
                st.error('The movie collection is taking a little longer to connect. Please try again in a moment. Your previous picks are still here.')
    if 'movie_results' in st.session_state:
        movies = st.session_state.movie_results
        last_query = st.session_state.last_movie_query
        if not movies:
            html('<div class="empty-state"><h3>No close matches this time.</h3><p>Our little collection might not have that story yet. Try a broader mood, a genre like horror, or a director like Christopher Nolan.</p></div>')
        else:
            html(f'<div class="results-heading"><strong>Your next watch</strong><span>{len(movies)} film{"s" if len(movies) != 1 else ""} to explore</span></div>')
            st.caption(f'Picked for “{last_query}”')
            for rank, movie in enumerate(movies, 1):
                render_movie(movie, rank)
            if st.button('Help me choose ✦', type='primary', use_container_width=True):
                try:
                    with st.spinner('Putting together a personal recommendation...'):
                        st.session_state.movie_recommendation = get_finder().recommend(last_query, movies)
                except ServiceError:
                    st.warning('The recommendation writer is unavailable right now. You can still explore your film picks above.')
            if st.session_state.get('movie_recommendation'):
                html('<div class="section-label">A little help choosing</div>')
                st.markdown(st.session_state.movie_recommendation)
            watchlist = '\n\n'.join(f'{m["title"]} ({m["year"]}) — {m["director"]}\n{m["description"]}' for m in movies)
            st.download_button('Save these picks ↓', data=watchlist, file_name='my-watchlist.txt', mime='text/plain', use_container_width=True)
            with st.expander('How these films were picked'):
                st.write('We compare the meaning of your request with each film’s description, then show up to three close matches. Explicit director requests also filter by director. The order is a similarity ranking, not a film rating.')
                for movie in movies:
                    st.caption(f'{movie["title"]} · cosine similarity {movie["score"]:.3f}')
                st.caption('Matching threshold: 0.30. AI recommendations use only your retrieved picks. The collection currently contains 30 films.')
    else:
        html('<div class="empty-state"><h3>The right film starts with a feeling.</h3><p>From comforting friendships to edge-of-your-seat stories, tell us what you’re after. Your picks will appear here.</p></div>')
html('<div class="footer"><span>Weekend &amp; Watchlist · Good plans, good stories.</span><span>A small collection. A world of possibilities.</span></div>')
