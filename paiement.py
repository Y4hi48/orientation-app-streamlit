import streamlit as st
import sqlite3
import re

# Formations Database with expanded options
FORMATIONS = {
    "Data": {"name": "Data Science", "etablissement": "ENSIAS", "frais": 500},
    "Electric": {"name": "Génie Électrique", "etablissement": "ENIM", "frais": 500},
    "Mechanique": {"name": "Génie Mécanique", "etablissement": "ENSAM", "frais": 500},
    "AI": {"name": "Intelligence Artificielle", "etablissement": "EMI", "frais": 500},
    "Industriel": {"name": "Génie Industriel", "etablissement": "EHTP", "frais": 500}
}

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            email TEXT,
            filiere TEXT,
            formation TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

# Validate email function
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Save registration to database
def save_registration(nom, email, filiere, formation):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO registrations 
        (nom, email, filiere, formation) 
        VALUES (?, ?, ?, ?)
    ''', (nom, email, filiere, formation))
    conn.commit()
    conn.close()

def main():
    # Initialize database
    init_db()

    # Streamlit page configuration
    st.set_page_config(page_title="CNC Orientation Service", page_icon=":graduation_cap:")

    # Sidebar for Student Profile
    st.sidebar.header("Profil Étudiant")
    nom = st.sidebar.text_input("Nom et Prénom")
    email = st.sidebar.text_input("Email")
    filiere = st.sidebar.selectbox("Filière CNC", ["MP", "PSI", "TSI"])

    # Main page content
    st.title("Système de Recommandation CNC")
    st.write("Bienvenue sur notre plateforme de recommandation des formations d'ingénieurs.")

    # Formation Selection
    st.subheader("Sélection de Formation")
    formation_choisie = st.selectbox(
        "Choisissez votre formation", 
        list(FORMATIONS.keys())
    )

    # Display formation details
    if formation_choisie:
        formation_details = FORMATIONS[formation_choisie]
        st.write(f"**Formation:** {formation_details['name']}")
        st.write(f"**Établissement:** {formation_details['etablissement']}")
        st.write(f"**Frais de dossier:** {formation_details['frais']} MAD")

    # Validate Profile and Proceed to Payment
    if st.button("Procéder au Paiement"):
        if not nom:
            st.error("Veuillez saisir votre nom")
        elif not validate_email(email):
            st.error("Veuillez saisir un email valide")
        else:
            # Save registration details
            save_registration(nom, email, filiere, formation_details['name'])
            
            # Redirect to Stripe payment
            st.markdown(
                f"""
                <a href="https://buy.stripe.com/test_9AQeXcdxsfFr5P2dQQ" 
                   target="_blank" 
                   style="display: inline-block; padding: 10px 20px; 
                          background-color: #4CAF50; color: white; 
                          text-decoration: none; border-radius: 5px;">
                    Payer {formation_details['frais']} MAD
                </a>
                """, 
                unsafe_allow_html=True
            )
            st.info("Après le paiement, votre inscription sera confirmée.")

    # Optional: View Registrations (Admin Feature)
    if st.checkbox("Voir les inscriptions (Admin)"):
        conn = sqlite3.connect('students.db')
        df = pd.read_sql_query("SELECT * FROM registrations", conn)
        st.dataframe(df)
        conn.close()

if __name__ == "__main__":
    main()