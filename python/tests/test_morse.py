from morse import normalize, text_to_pattern


def test_sos():
    assert text_to_pattern("SOS") == "._._.|-_-_-|._._."


def test_palabras_separadas_por_doble_barra():
    assert "||" in text_to_pattern("ALTO ROJO")


def test_tildes_y_enie():
    assert normalize("año") == "AÑO"  # la Ñ se conserva; las tildes se quitan
    assert text_to_pattern("ñ") == "-_-_._-_-"  # Ñ = --.--


def test_caracteres_desconocidos_se_ignoran():
    assert text_to_pattern("A!") == "._-"  # A = .-, el '!' se ignora
