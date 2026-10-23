"""Streamlit interface. Run: python -m streamlit run web_app.py."""
from html import escape
from pathlib import Path
import streamlit as st
from common.llm import ServiceError
from movie_finder.search import MovieFinder, movie_id, load_movies
from travel_buddy.bot import TravelBuddy
from ui_helpers import toggle_saved, watchlist_text, poster_style

ASSETS = Path(__file__).with_name('assets')
st.set_page_config(page_title='Weekend & Watchlist', page_icon='✦', layout='wide')
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

def hero(kind, eyebrow, title, description, facts, *, compact=False):
    if compact:
        svg = (ASSETS / f'{kind}.svg').read_text(encoding='utf-8')
        html(f'<div class="compact-hero"><div><div class="eyebrow">{eyebrow}</div>'
             f'<h1>{escape(title).replace(chr(10), " ")}</h1></div><div class="compact-art">{svg}</div></div>')
        return
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

def render_movie(movie, rank, *, ranked=False):
    title = escape(movie['title'])
    style = poster_style(movie)
    badge = f'<span class="rank-badge" aria-label="Match {rank}">{rank}</span>' if ranked else ''
    html(f'<article class="movie-card"><div class="poster" role="img" aria-label="Original cinematic artwork for {title}" style="{style}">{badge}</div>'
         f'<div class="movie-info"><h3 class="movie-title">{title} <span>({int(movie["year"])})</span></h3>'
         f'<div class="movie-meta">{escape(movie["director"])}</div>'
         f'<p class="movie-description">{escape(movie["description"])}</p>'
         f'<div class="movie-genre">{escape(movie["genre"])}</div></div></article>')

brand_col, nav_col = st.columns([1.2, 2.4], vertical_alignment='center')
with brand_col:
    html('<div class="brand"><span>Weekend &amp; <b>Watchlist</b></span></div>')
with nav_col:
    page = st.radio('Choose your experience', ['Plan a getaway', 'Find a film', 'Saved films'], index=1,
                    horizontal=True, label_visibility='collapsed', key='experience')
html('<div class="nav-rule"></div>')
if page != 'Plan a getaway':
    html(f'<style>{(ASSETS / "lounge.css").read_text(encoding="utf-8")}</style><div class="lounge-marker" aria-hidden="true"></div>')
if 'saved_movies' not in st.session_state:
    st.session_state.saved_movies = {}

if page == 'Plan a getaway':
    html(f'<style>{(ASSETS / "coastal.css").read_text(encoding="utf-8")}</style><div class="coastal-marker" aria-hidden="true"></div>')
    if 'travel' not in st.session_state:
        st.session_state.travel = TravelBuddy()
        st.session_state.travel.start()
    bot = st.session_state.travel
    html('<section class="coastal-hero' + (' coastal-compact' if bot.choices or bot.closed else '') + '"><div class="coastal-copy">'
         '<div class="eyebrow">YOUR WEEKEND STARTS HERE</div><h1>A little further<br>from ordinary.</h1>'
         '<div class="coastal-underline"></div><p>Your next weekend, planned<br>around you.</p></div></section>')
    with st.container(key='travel-planner'):
        stage = len(bot.choices)
        labels = ['The setting', 'Your stay', 'The experience']
        html('<div class="steps">' + ''.join(
            f'<div class="step {"done" if stage > i else "active" if stage == i else ""}" {"aria-current=\"step\"" if stage == i else ""}><b>{"✓" if stage > i else i+1}</b><span>{label}</span></div>'
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
            edits = st.columns(3)
            for index, label in enumerate(['Change setting', 'Change stay', 'Change activity']):
                if edits[index].button(label, use_container_width=True):
                    bot.edit(index)
                    st.rerun()
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
                        art = (f'<div class="destination-photo destination-{i}" role="img" aria-label="{escape(option)} scenery"></div>' if stage == 0 else
                               f'<div class="choice-art" aria-hidden="true" style="--tile:{color}">{icon}</div>')
                        html(f'{art}<div class="choice-title">{escape(option)}</div><div class="choice-description">{description}</div>')
                        if st.button(f'Choose {option}', key=f'choice-{stage}-{i}', use_container_width=True, type='primary'):
                            selected = option
            with st.form('travel-preference', clear_on_submit=True):
                input_col, send_col = st.columns([4, 1.2], vertical_alignment='bottom')
                preference = input_col.text_input('Tell us what you have in mind (optional)', placeholder='For example: a quiet beach, fresh mountain air, or a foodie city', max_chars=1000)
                with send_col:
                    send = st.form_submit_button('Continue →', type='primary', use_container_width=True)
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
elif page == 'Saved films':
    html('<div class="saved-heading"><div class="eyebrow">YOUR PERSONAL SCREENING LIST</div><h1>Worth saving.<br>Worth <em>watching.</em></h1></div>')
    saved = st.session_state.saved_movies
    if not saved:
        html('<div class="empty-state"><h3>Your next great film is out there.</h3><p>Find a film, then save the ones that catch your eye. They will stay here during this session.</p></div>')
    else:
        columns = st.columns(3, gap='medium')
        for rank, (identifier, movie) in enumerate(list(saved.items()), 1):
            with columns[(rank - 1) % 3]:
                render_movie(movie, rank)
                st.button(f'Remove {movie["title"]}', key=f'library-remove-{identifier}', on_click=toggle_saved, args=(saved, movie), use_container_width=True)
        st.download_button('Download saved films ↓', data=watchlist_text(saved.values()), file_name='saved-films.txt', mime='text/plain')
        st.caption('Saved for this session. Download your list to keep it after closing the app.')
else:
    html('<section class="lounge-hero"><div class="eyebrow">MOVIES FOR EVERY MOOD</div><h1>What do you want to <em>watch?</em></h1><p>Describe a movie, a feeling, a director, or just a vibe. Find something for tonight.</p></section>')
    if 'movie_input' not in st.session_state:
        st.session_state.movie_input = st.session_state.get('last_movie_query', '')
    with st.form('movie-query'):
        search_col, submit_col = st.columns([5, 1.4], vertical_alignment='bottom')
        query = search_col.text_input('What are you in the mood for?', placeholder='Movies by Christopher Nolan', key='movie_input', max_chars=1000, label_visibility='collapsed')
        with submit_col:
            submitted = st.form_submit_button('Find films →', type='primary', use_container_width=True)
    with st.container(key='mood-chips'):
        suggestions = st.columns(6)
        examples = [('A little suspense', 'something scary to watch tonight'), ('A Nolan night', 'movies by Christopher Nolan'), ('Something feel-good', 'a feel-good movie about friendship'), ('Mind-bending', 'a mind-bending science fiction movie'), ('Action-packed', 'an action movie with a thrilling adventure'), ('About friendship', 'a movie about friendship')]
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
                startup_note = st.empty()
                if not st.session_state.get('collection_opened'):
                    startup_note.info('The first search opens the collection. Your next searches will be quicker.')
                with st.spinner('Finding a few good stories...'):
                    finder = get_finder()
                    movies = finder.search(requested)
                st.session_state.movie_results = movies
                st.session_state.last_movie_query = requested
                st.session_state.collection_opened = True
                st.session_state.pop('movie_recommendation', None)
                startup_note.empty()
                st.rerun()
            except Exception:
                st.error('The movie collection is taking a little longer to connect. Please try again in a moment. Your previous picks are still here.')
    saved = st.session_state.saved_movies
    with st.expander(f'Saved for later ({len(saved)})'):
        st.caption('Your personal shortlist for this session. Download it to keep a copy after closing the app.')
        if not saved:
            st.write('When a film catches your eye, choose Save for later beneath its card.')
        for identifier, movie in list(saved.items()):
            title_col, remove_col = st.columns([3, 2])
            title_col.write(f'**{movie["title"]}** ({int(movie["year"])})')
            remove_col.button(f'Remove {movie["title"]}', key=f'remove-{identifier}',
                              on_click=toggle_saved, args=(saved, movie), use_container_width=True)
        if saved:
            st.download_button('Download saved films ↓', data=watchlist_text(saved.values()),
                               file_name='saved-films.txt', mime='text/plain', use_container_width=True)
    if 'movie_results' in st.session_state:
        movies = st.session_state.movie_results
        last_query = st.session_state.last_movie_query
        if not movies:
            html('<div class="empty-state"><h3>No close matches this time.</h3><p>Our little collection might not have that story yet. Try a broader mood, a genre like horror, or a director like Christopher Nolan.</p></div>')
        else:
            html(f'<div class="results-heading"><strong>Your next watch</strong><span>{len(movies)} film{"s" if len(movies) != 1 else ""} to explore</span></div>')
            st.caption(f'Picked for “{last_query}”')
            columns = st.columns(3, gap='medium')
            for rank, movie in enumerate(movies, 1):
                with columns[rank - 1]:
                    render_movie(movie, rank, ranked=True)
                    identifier = movie_id(movie)
                    is_saved = identifier in saved
                    st.button('Saved ✓ · remove' if is_saved else f'Save {movie["title"]} for later +',
                              key=f'save-{identifier}', on_click=toggle_saved, args=(saved, movie), use_container_width=True)
                    st.button('More like this →', key=f'similar-{identifier}', on_click=queue_query,
                              args=(f'{movie["genre"]} movies about {movie["description"]}',), use_container_width=True)
            if st.button('Help me choose ✦', type='primary', use_container_width=True):
                try:
                    with st.spinner('Putting together a personal recommendation...'):
                        st.session_state.movie_recommendation = get_finder().recommend(last_query, movies)
                except ServiceError:
                    st.warning('The recommendation writer is unavailable right now. You can still explore your film picks above.')
            if st.session_state.get('movie_recommendation'):
                html('<div class="section-label">A little help choosing</div>')
                st.markdown(st.session_state.movie_recommendation)
            watchlist = watchlist_text(movies)
            st.download_button('Save these picks ↓', data=watchlist, file_name='my-watchlist.txt', mime='text/plain', use_container_width=True)
            with st.expander('How these films were picked'):
                st.write('We compare the meaning of your request with each film’s description, then show up to three close matches. Explicit director requests also filter by director. The order is a similarity ranking, not a film rating.')
                for movie in movies:
                    st.caption(f'{movie["title"]} · cosine similarity {movie["score"]:.3f}')
                st.caption('Matching threshold: 0.30. AI recommendations use only your retrieved picks. The collection currently contains 30 films.')
    else:
        featured = {movie['title']: movie for movie in load_movies()}
        st.caption('FROM THE COLLECTION · Search above for your own matches')
        columns = st.columns(3, gap='medium')
        for rank, title in enumerate(['Interstellar', 'Inception', 'Memento'], 1):
            movie = featured[title]
            with columns[rank - 1]:
                render_movie(movie, rank)
                identifier = movie_id(movie)
                st.button('Saved ✓ · remove' if identifier in saved else f'Save {title} for later +',
                          key=f'featured-{identifier}', on_click=toggle_saved, args=(saved, movie), use_container_width=True)
    html('<div class="results-heading"><strong>More to explore</strong><span>From our 30-film collection</span></div>')
    browse = st.columns(6)
    collection = {m['title']: m for m in load_movies()}
    for column, title in zip(browse, ['The Dark Knight', 'Arrival', 'Parasite', 'La La Land', 'The Grand Budapest Hotel', 'Paddington 2']):
        movie = collection.get(title)
        if movie:
            with column:
                html(f'<div class="explore-art" role="img" aria-label="Illustrative {escape(movie["genre"])} artwork" style="{poster_style(movie)}"></div><div class="explore-title">{escape(title)}</div><div class="explore-year">{movie["year"]}</div>')
                st.button('Explore →', key=f'explore-{movie_id(movie)}', on_click=queue_query,
                          args=(f'{movie["genre"]} movies about {movie["description"]}',), use_container_width=True)
html('<div class="footer"><span>Weekend &amp; Watchlist · Your next great story.</span><span>' +
     ('Three simple steps. A weekend to make your own.' if page == 'Plan a getaway' else 'A small collection. A world of possibilities.') + '</span></div>')
