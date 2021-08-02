import streamlit as st
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import simplejson as json
import time
from random import shuffle
import base64
import datetime
from urllib.parse import urlencode
import requests
import pandas as pd
import json
from spotipy import oauth2

def remove_duplicates(duplicates,no_duplicates):
    for item in duplicates:
        if item not in no_duplicates:
            no_duplicates.append(item)
    return no_duplicates
def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out
def main():
    #############################
    # CONFIGURATION DE LA PAGE
    #############################
    
    st.set_page_config(
        page_title="Recommandations Spotify",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.sidebar.title('Paramètres')
    st.title('Recommandations Spotify')
    
    #############################
    # VARIABLES
    #############################
    SPOTIPY_CLIENT_ID = 'c35363c3c06b4a459d30b2b4da74fd19'
    SPOTIPY_CLIENT_SECRET = 'eb7c7d1a84774f7b89cdfd901e2f33ec'
    #SPOTIPY_REDIRECT_URI='http://localhost:8085'
    SPOTIPY_REDIRECT_URI = 'https://spotidiscovery.herokuapp.com/'
    scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private streaming ugc-image-upload user-follow-modify user-follow-read user-library-read user-library-modify user-read-private user-read-birthdate user-read-email user-top-read user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played'
    CACHE = '.spotipyoauthcache'
    username=st.sidebar.text_input("Nom d'utilisateur", value='erwan.lenagard', max_chars=None, key=None, type='default')
    
    artist_ids_noduplicates=[]
    artist_ids=[]
    artist_images=[]
    artist_popularities=[]
    artist_names=[]
    chunks=[]
    final_top_track_noduplicates=[]
    col_1, col_2, col_3, col_4,col_5 = st.beta_columns([1,1,1,1,1])

    
    #############################
    # SIDEBAR
    #############################
    search=st.sidebar.text_input("Artiste", value='Mark Lanegan', max_chars=None, key=None, type='default')

    ntoptrack=st.sidebar.number_input("Top tracks",min_value=1,max_value=10,value=3,step=1)
    nb_recos=st.sidebar.number_input("Nombre de recommandations",min_value=1,max_value=None,value=3,step=1)
    acousticness=st.sidebar.slider("Acousticness", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    danceability=st.sidebar.slider("danceability", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    energy=st.sidebar.slider("energy", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    instrumentalness=st.sidebar.slider("instrumentalness", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    liveness=st.sidebar.slider("liveness", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    speechiness=st.sidebar.slider("speechiness", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    valence=st.sidebar.slider("valence", min_value=0.0, max_value=1.0, value=[0.0,1.0], step=0.1)
    popularity=st.sidebar.slider("popularity", min_value=0, max_value=100, value=[0,100], step=1)
    publicOrprivate=st.sidebar.checkbox('Playlist Publique ?',value=False)
    
    #############################
    # NAMING DE LA PLAYLIST
    #############################
    timestr = time.strftime("%Y%m%d")
    playlistname=timestr+"_related_"+search
    
    #############################
    # AUTHENTIFICATION
    #############################
    
    if st.sidebar.button('Obtenir des recommandations'):

#         cache_path = '/tmp/cache-{}'.format(username)
#         st.write(cache_path)
#         auth_manager=SpotifyOAuth(username=username, client_id=SPOTIPY_CLIENT_ID,client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope,cache_path=cache_path,open_browser=False,show_dialog=False)
#         scope="playlist-modify-public"

# #         print( "auth_manager.get_authorize_url() : {}".format(auth_manager.get_authorize_url() ))

#         sp = spotipy.Spotify(auth_manager=auth_manager)
#         st.write("alleluiah")
#         sp = spotipy.Spotify(auth=token)
#         st.write("coucou")
        #token = util.prompt_for_user_token(username,scope,client_id=SPOTIPY_CLIENT_ID,client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI,show_dialog=True,cache_path=cache_path, open_browser=True)

        # if token:
        #     sp = spotipy.Spotify(auth=token)
            #sp.trace = False

#         token =util.prompt_for_user_token(username,scope,client_id=SPOTIPY_CLIENT_ID,client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri='https://spotidiscovery.herokuapp.com',show_dialog=True)
#         st.write(token)
#         print("token",token)
#         if token:
#             sp = spotipy.Spotify(auth=token)
#             sp.trace = False


        st.write("<a href=\"https://oauthspotidiscovery.herokuapp.com/\">Login to Spotify</a>",unsafe_allow_html=True)




#         Création de la playlist
        playlist=sp.user_playlist_create(username,name=playlistname, public=publicOrprivate)
        playlist_id= str(playlist['id'])
        final_top_track=[]
        final_top_track_noduplicates=[]
        tmp_top_track=[]

        #on cherche l'artiste demandé
        results_search=sp.search(search, type='artist', limit=1)
        artistid=results_search['artists']['items'][0]['uri']

        #initialisation de la barre de progression
        latest_iteration = st.empty()
        bar = st.progress(0)
        i=0      
        # on cherche les artistes associés 
        related = sp.artist_related_artists(artistid)
        for artistrelated in related['artists']:       
            artistrelated_id = artistrelated['id']
            artistrelated_uri=artistrelated['uri']
            artist_name=artistrelated['name']
            artist_popularity=artistrelated['popularity']
            artist_followers=artistrelated['followers']['total']
            artist_img=artistrelated['images'][0]['url']
            artist_ids.append(artistrelated_id)


            #Pour chaque artiste lié on récupère un nombre de chanson recommandées (pas forcément de cet artiste)
            reco=sp.recommendations(market='fr', seed_artists=[artistrelated_uri], limit=nb_recos)
            for trackreco in reco['tracks'] :
                artist_ids.append(trackreco['artists'][0]['id'])
                trackreco_id=["spotify:track:" + trackreco['id']]
                final_top_track.append(trackreco_id)

            #pour chaque artiste lié, on récupère ses 10 tops tracks
            result=sp.artist_top_tracks(artistrelated_id, country='FR')
            for toptrack in result['tracks']:
                trackid=["spotify:track:" + toptrack['id']]
                tmp_top_track.append(trackid)
            shuffle(tmp_top_track)

            # après les avoir mélangées aléatoirement, on en pioche n
            for item in tmp_top_track[:ntoptrack]:
                final_top_track.append(item)

            latest_iteration.text(f"Progression {round(((i+1)/len(related['artists']))*100)}%")
            bar.progress((i+1)/len(related['artists']))
            i=i+1
        bar.empty() 
        latest_iteration.empty()
        # On dédoublonne la liste des chansons et on mélange
        final_top_track_noduplicates=remove_duplicates(final_top_track,final_top_track_noduplicates)
        shuffle(final_top_track_noduplicates)  

        # On dédoublonne la liste des artistes
        artist_ids_noduplicates=remove_duplicates(artist_ids,artist_ids_noduplicates)

        # On crée des paquets de 10 artistes pour récupérer leurs infos
        chunks_artist_ids=[artist_ids_noduplicates[i:i + 10] for i in range(0, len(artist_ids_noduplicates), 10)]
        for chunk in chunks_artist_ids:
            artist_lookup=sp.artists(chunk)
            for lookup in artist_lookup["artists"]:
                artist_images.append(lookup['images'][0]['url'])
                artist_popularities.append(lookup['popularity'])
                artist_names.append(lookup['name'])

        l_img=chunkIt(artist_images, 5)
        l_pop=chunkIt(artist_popularities,5)
        l_names=chunkIt(artist_names,5)

        ###################################
        # AFFICHAGE DES COLONNES
        ###################################

        with col_1:
            i=0
            for img in l_img[0]:
                st.image(img,use_column_width=True,caption=l_names[0][i]+' - '+str(l_pop[0][i]))
                i=i+1
        with col_2:
            i=0
            for img in l_img[1]:
                st.image(img,use_column_width=True,caption=l_names[1][i]+' - '+str(l_pop[1][i]))
                i=i+1
        with col_3:
            i=0
            for img in l_img[2]:
                st.image(img,use_column_width=True,caption=l_names[2][i]+' - '+str(l_pop[2][i]))
                i=i+1

        with col_4:
            i=0
            for img in l_img[3]:
                st.image(img,use_column_width=True,caption=l_names[3][i]+' - '+str(l_pop[3][i]))
                i=i+1

        with col_5:
            i=0
            for img in l_img[4]:
                st.image(img,use_column_width=True,caption=l_names[4][i]+' - '+str(l_pop[4][i]))
                i=i+1

        latest_iteration_playlist = st.empty()
        bar_playlist = st.progress(0)
        j=0
        # On ajoute les tracks à la playlist
        for t in final_top_track_noduplicates:
            sp.user_playlist_add_tracks(username, playlist_id, t)    
            latest_iteration_playlist.text(f'Création de la playlist {round(((j+1)/len(final_top_track_noduplicates))*100)}%')
            bar_playlist.progress((j+1)/len(final_top_track_noduplicates))
            j=j+1

        bar_playlist.empty() 
        latest_iteration_playlist.empty()
#     else:
#         print("Can't get token for", username) 

            
if __name__ == "__main__":
    main()