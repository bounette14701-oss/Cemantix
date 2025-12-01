import streamlit as st
import difflib

# --- Le mot mystère est maintenant fixé ici ---
MOT_MYSTERE_FIXE = "AMOUREUX"
# ---------------------------------------------

def calculer_similarite(mot_mystere, proposition):
    """
    Calcule un score de similarité entre 0 et 1000.
    """
    mot_mystere = mot_mystere.lower().strip()
    proposition = proposition.lower().strip()

    # 1. Ratio de similarité de séquence (plus le mot est proche du mot mystère)
    score_base = difflib.SequenceMatcher(None, mot_mystere, proposition).ratio()
    
    # 2. Poids pour la longueur (plus c'est proche, mieux c'est)
    if len(mot_mystere) > 0:
        diff_longueur = abs(len(mot_mystere) - len(proposition))
        # Le poids de longueur diminue si la différence de longueur est grande
        poids_longueur = max(0, 1.0 - (diff_longueur / len(mot_mystere)))
    else:
        poids_longueur = 0

    # Score final pondéré
    score_final = (score_base * 0.7 + poids_longueur * 0.3)
    
    # Conversion à l'échelle Cémantix (0 à 1000)
    score_cemantix = int(score_final * 1000)
    
    # S'assurer que le score est entre 0 et 1000
    return max(0, min(1000, score_cemantix))

# --- Initialisation de l'application Streamlit ---

st.title("💖 Cémantix Personnalisé : Thème Amour")
st.markdown("Trouvez le mot mystère en vous basant sur la similarité sémantique (simulée ici par une distance textuelle).")

# Initialisation des variables de session si elles n'existent pas
if 'historique_propositions' not in st.session_state:
    st.session_state.historique_propositions = []
if 'trouve' not in st.session_state:
    st.session_state.trouve = False

# --- Affichage du statut du jeu ---
st.header("État du Jeu")
if not st.session_state.trouve:
    st.info(f"Le mot mystère est prêt. Tentatives : {len(st.session_state.historique_propositions)}")
else:
    st.success(f"🎉 Le mot mystère était **{MOT_MYSTERE_FIXE}** ! Partie terminée.")

# --- Formulaire de Jeu (Étape 2) ---
if not st.session_state.trouve:
    st.header("1️⃣ Faites une Proposition")
    
    with st.form("form_proposition"):
        proposition_utilisateur = st.text_input("Proposez un mot :", key="input_prop").strip().upper()
        proposition_soumise = st.form_submit_button("Soumettre")

        if proposition_soumise and proposition_utilisateur:
            
            if proposition_utilisateur == MOT_MYSTERE_FIXE:
                st.session_state.trouve = True
                score = 1000
                st.session_state.historique_propositions.append((proposition_utilisateur, score))
                st.balloons()
                # Le message de succès est géré par l'affichage du statut du jeu
                st.rerun()
            else:
                score = calculer_similarite(MOT_MYSTERE_FIXE, proposition_utilisateur)
                st.session_state.historique_propositions.append((proposition_utilisateur, score))
                st.markdown(f"**👉 Score pour '{proposition_utilisateur}' : ** `{score}/1000`")
                # Vider la boîte de saisie après soumission et relancer pour mise à jour
                st.session_state.input_prop = ""
                st.rerun()

    # --- Affichage de l'historique ---
    if st.session_state.historique_propositions:
        st.header("Historique et Meilleurs Scores")
        
        # Tri de l'historique par score
        historique_trie = sorted(st.session_state.historique_propositions, key=lambda x: x[1], reverse=True)
        
        # Affichage sous forme de tableau
        data = [{"Mot": mot, "Score": score} for mot, score in historique_trie]
        st.dataframe(data, use_container_width=True, hide_index=True)

# --- Fin de partie et Option de Réinitialisation ---
if st.session_state.trouve:
    st.header("Partie Terminée")
    if st.button("Recommencer une nouvelle partie"):
        st.session_state.historique_propositions = []
        st.session_state.trouve = False
        st.rerun()
