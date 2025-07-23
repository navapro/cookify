def search_for_recipes(duration, cuisines, search = "") -> str:
    query = "select * from recipes r where "
    if (duration == "short"):
        query += "r.duration <= 10"
    elif (duration == "medium"):
        query += "r.duration >= 10 AND r.duration <= 60"
    else:
        query += "r.duration >= 60"
    if (search != ""):
        query += " AND r.rname like '%" + search + "%'"
    for cuisine in cuisines:
        query += " AND r.cuisine = '" + cuisine + "'"
    query += ";"
    return query