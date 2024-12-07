import streamlit as st
import stripe
import re

# Configure Stripe
STRIPE_SECRET_KEY = "your_stripe_secret_key_here"
stripe.api_key = STRIPE_SECRET_KEY

# Function to validate email
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Payment Intent Creation Function
def create_payment_intent(amount):
    try:
        # Convert amount to cents (assuming amount is in MAD)
        amount_in_cents = int(amount * 100)
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="mad",  # Using Moroccan Dirham
            payment_method_types=["card"],
        )
        return payment_intent.client_secret
    except Exception as e:
        st.error(f"Error creating payment: {e}")
        return None

# Main Streamlit App
def main():
    st.set_page_config(page_title="CNC Orientation Service", page_icon=":graduation_cap:")

    # Sidebar for Student Profile
    st.sidebar.header("Profil Étudiant")
    nom = st.sidebar.text_input("Nom et Prénom")
    email = st.sidebar.text_input("Email")
    classement = st.sidebar.number_input("Classement CNC", min_value=1, max_value=5000, step=1)
    filiere = st.sidebar.selectbox("Filière choisie", ["MP", "PSI", "TSI"])
    interets = st.sidebar.text_area("Mots-clés d'intérêt (ex: IA, Génie Civil, Énergie)")

    # Main page content
    st.title("Système de Recommandation CNC")
    st.write("Bienvenue sur notre plateforme de recommandation des formations d'ingénieurs pour les étudiants du CNC.")

    # Formations Database
    formations = [
        {
            "Nom": "Génie Informatique", 
            "Etablissement": "EMI", 
            "Débouchés": "Ingénieur logiciel, Data Scientist", 
            "Mots-clés": "Informatique, IA, Programmation",
            "Frais": 500
        },
        {
            "Nom": "Génie Civil", 
            "Etablissement": "EHTP", 
            "Débouchés": "Chef de projet, Consultant en BTP", 
            "Mots-clés": "Construction, BTP, Environnement",
            "Frais": 500
        },
        {
            "Nom": "Ingénierie des Données", 
            "Etablissement": "ENSIAS", 
            "Débouchés": "Data Analyst, Ingénieur Big Data", 
            "Mots-clés": "Data Science, IA, Cloud",
            "Frais": 500
        }
    ]

    # Validate Profile
    profile_valid = False
    if st.sidebar.button("Enregistrer le profil"):
        if not nom:
            st.sidebar.error("Veuillez saisir votre nom")
        elif not validate_email(email):
            st.sidebar.error("Veuillez saisir un email valide")
        elif not interets:
            st.sidebar.error("Veuillez saisir vos mots-clés d'intérêt")
        else:
            profile_valid = True
            st.sidebar.success("Profil enregistré avec succès !")

    # Recommandation de Formations
    st.subheader("Formations recommandées")
    
    # Filter formations based on interests
    if interets and profile_valid:
        mots_cles = [mot.strip().lower() for mot in interets.split(",")]
        formations_recommandees = [
            formation for formation in formations
            if any(mot in formation["Mots-clés"].lower() for mot in mots_cles)
        ]

        if not formations_recommandees:
            st.write("Aucune formation ne correspond à vos mots-clés. Essayez d'élargir vos intérêts.")
        else:
            # Store selected formation in session state
            if 'selected_formation' not in st.session_state:
                st.session_state.selected_formation = None

            for i, formation in enumerate(formations_recommandees):
                with st.container():
                    st.write(f"**{formation['Nom']}** - {formation['Etablissement']}")
                    st.write(f"Débouchés : {formation['Débouchés']}")
                    st.write(f"Mots-clés : {formation['Mots-clés']}")
                    st.write(f"Frais de dossier : {formation['Frais']} MAD")
                    
                    if st.button(f"Sélectionner {formation['Nom']}"):
                        st.session_state.selected_formation = formation
                        st.success(f"Vous avez sélectionné : {formation['Nom']}")

    # Payment Section
    st.subheader("Paiement des frais de dossier")
    
    if st.session_state.get('selected_formation'):
        formation = st.session_state.selected_formation
        
        # Payment process
        st.write(f"Frais de dossier pour {formation['Nom']} : {formation['Frais']} MAD")
        
        if st.checkbox("J'accepte de payer les frais de dossier"):
            if st.button("Procéder au Paiement"):
                # Create Payment Intent
                client_secret = create_payment_intent(formation['Frais'])
                
                if client_secret:
                    st.success("Lien de paiement généré!")
                    st.write(f"Veuillez suivre ce lien pour compléter le paiement : [Payer {formation['Frais']} MAD](https://checkout.stripe.com/pay/{client_secret})")
                else:
                    st.error("Erreur lors de la génération du lien de paiement")
    else:
        st.info("Veuillez d'abord sélectionner une formation pour procéder au paiement.")

if __name__ == "__main__":
    main()