def search_for_recipes(cuisines, duration = "no filter", search = "") -> str:
    query = "select * from recipes r where "
    if (duration == "short"):
        query += "r.duration < 30"
    elif (duration == "medium"):
        query += "r.duration >= 30 AND r.duration <= 60"
    elif (duration == "long"):
        query += "r.duration > 60"
    else:
        query += "r.duration >= 0"
    if (search != ""):
        query += " AND r.rname like '%" + search + "%'"
    for cuisine in cuisines:
        query += " AND r.cuisine = '" + cuisine + "'"
    query += ";"
    return query