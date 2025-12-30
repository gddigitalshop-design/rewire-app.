def genera_immagine(prompt_immagine):
    try:
        import urllib.parse
        import random # Importiamo random per cambiare sempre immagine
        
        # Puliamo il prompt
        prompt_pulito = urllib.parse.quote(prompt_immagine)
        
        # Generiamo un numero casuale per forzare il refresh dell'immagine
        seed = random.randint(0, 99999)
        
        # URL aggiornato con seed casuale e parametri di stile
        image_url = f"https://image.pollinations.ai/prompt/{prompt_pulito}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
        
        st.success(f"🎨 Generata immagine per: {prompt_immagine}")
        return image_url
    except Exception as e:
        st.error(f"Errore nella generazione: {e}")
        return None
