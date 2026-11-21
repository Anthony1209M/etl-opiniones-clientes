def construir_cadena(db):
    base = (f"DRIVER={{{db['driver']}}};SERVER={db['server']};"
            f"DATABASE={db['database']};")
    if db.get("user"):
        return base + f"UID={db['user']};PWD={db['password']};"
    return base + "Trusted_Connection=yes;"   # autenticación de Windows