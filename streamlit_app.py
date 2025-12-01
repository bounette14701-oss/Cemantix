import streamlit as st
import difflib

# --- Le mot mystère est maintenant fixé ici ---
MOT_MYSTERE_FIXE = "AMOUREUX"
# ---------------------------------------------

def calculer_similarite(mot_mystere, proposition):
    """
    Calcule un score de similarité entre 0 et 1000 basé sur la similarité textuelle.
    """
    mot_mystere = mot_mystere.lower().strip()
    proposition = proposition.lower().strip()

    # 1. Ratio de similarité de séquence
    score_base = difflib.SequenceMatcher(None, mot_mystere, proposition).ratio()
    
    # 2. Poids pour la longueur
    if len(mot_mystere) > 0:
        diff_longueur = abs(len(mot_mystere) - len(proposition))
        poids_longueur = max(0, 1.0 - (diff_longueur / len(mot_mystere)))
    else:
        poids_longueur = 0

    # Score final pondéré
    score_final = (score_base * 0.7 + poids_longueur * 0.3)
    
    # Conversion à l'échelle Cémantix (0 à 1000)
    score_cemantix = int(score_final * 1000)
    
    return max(0, min(1000, score_cemantix))

# --- Fonction de rappel pour la soumission ---
def gerer_proposition_soumise(proposition_utilisateur):
    """
    Traite la proposition, calcule le score et réinitialise le champ d'entrée.
    """
    if not proposition_utilisateur:
        st.session_state.message_erreur = "Veuillez entrer un mot valide."
        return

    st.session_state.message_erreur = ""
    mot_mystere = MOT_MYSTERE_FIXE
    
    if proposition_utilisateur == mot_mystere:
        st.session_state.trouve = True
        score = 1000
    else:
        score = calculer_similarite(mot_mystere, proposition_utilisateur)
    
    st.session_state.historique_propositions.append((proposition_utilisateur, score))
    st.session_state.dernier_score = (proposition_utilisateur, score)
    
    # Réinitialisation SÛRE du champ d'entrée via session_state
    if not st.session_state.trouve:
        st.session_state.input_prop = ""

# --- Fonctions d'affichage de la jauge ---
def afficher_jauge_coloree(score):
    """
    Affiche une barre de progression colorée (rouge vers vert) et stylisée.
    """
    couleur = "red"
    if score >= 900:
        couleur = "green"
    elif score >= 700:
        couleur = "lightgreen"
    elif score >= 500:
        couleur = "yellow"
    elif score >= 250:
        couleur = "orange"
        
    # NOUVEL AFFICHAGE : Utilisation d'un markdown pour le pourcentage et la jauge
    score_pourcentage = int(score / 1000 * 100) # Conversion en pourcentage entier
    
    st.markdown(f"**{score_pourcentage}%** de similarité", unsafe_allow_html=True)
    
    style_html = f"""
    <div style="background-color: #eee; border-radius: 5px; height: 30px; width: 100%; margin-bottom: 20px;">
        <div style="background-color: {couleur}; border-radius: 5px; height: 100%; width: {score_pourcentage}%;">
        </div>
    </div>
    """
    st.markdown(style_html, unsafe_allow_html=True)
    
# --- Initialisation de l'application Streamlit ---

st.title("🏹 La Chasse au Mot Secret")
st.markdown("Trouvez le mot mystère en proposant des mots qui s'en approchent sémantiquement.")

# Initialisation des variables de session
if 'historique_propositions' not in st.session_state:
    st.session_state.historique_propositions = []
if 'trouve' not in st.session_state:
    st.session_state.trouve = False
if 'dernier_score' not in st.session_state:
    st.session_state.dernier_score = None
if 'message_erreur' not in st.session_state:
    st.session_state.message_erreur = ""

# --- Affichage du statut du jeu et de la Jauge ---
st.header("État du Jeu")

if not st.session_state.trouve:
    st.info(f"Le mot mystère est prêt. Tentatives : {len(st.session_state.historique_propositions)}")
    
    # Afficher la jauge du dernier score (si existant)
    if st.session_state.dernier_score:
        mot, score = st.session_state.dernier_score
        
        st.subheader(f"✨ Similarité pour **'{mot}'**")
        # AFFICHAGE VISUEL DE LA JAUGE ET DU POURCENTAGE
        afficher_jauge_coloree(score)
        
else:
    st.success(f"🎉 FÉLICITATIONS ! Le mot mystère était **{MOT_MYSTERE_FIXE}** ! Vous avez trouvé en {len(st.session_state.historique_propositions)} tentatives.")
    st.balloons()
    

# --- Formulaire de Jeu (Étape 2) ---
if not st.session_state.trouve:
    st.header("1️⃣ Faites une Proposition")
    
    proposition_utilisateur = st.text_input("Proposez un mot :", key="input_prop", value=st.session_state.get('input_prop', '')).strip().upper()
    
    st.button(
        "Soumettre",
        on_click=gerer_proposition_soumise,
        args=[proposition_utilisateur]
    )
    
    if st.session_state.message_erreur:
        st.error(st.session_state.message_erreur)
        st.session_state.message_erreur = ""


    # --- Affichage de l'historique ---
    if st.session_state.historique_propositions:
        st.header("Historique et Meilleurs Scores")
        
        historique_trie = sorted(st.session_state.historique_propositions, key=lambda x: x[1], reverse=True)
        
        # Le tableau affiche toujours le score /1000 pour la précision des résultats
        data = [{"Mot": mot, "Score": score} for mot, score in historique_trie]
        st.dataframe(data, use_container_width=True, hide_index=True)

# --- Fin de partie et Option de Réinitialisation ---
if st.session_state.trouve:
    st.header("Partie Terminée")
    def reinitialiser_jeu():
        st.session_state.historique_propositions = []
        st.session_state.trouve = False
        st.session_state.dernier_score = None
        st.session_state.input_prop = "" 

    if st.button("Recommencer une nouvelle partie", on_click=reinitialiser_jeu):
        st.rerun()
