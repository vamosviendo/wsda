def existe_columna(cursor, tabla, columna):
    """ Devuelve true si columna existe en tabla."""
    if cursor.db.vendor == "sqlite":
        cursor.execute(f"PRAGMA table_info({tabla})")
        return any(row[1] == columna for row in cursor.fetchall())

    cursor.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        [tabla, columna],
    )
    return cursor.fetchone() is not None
