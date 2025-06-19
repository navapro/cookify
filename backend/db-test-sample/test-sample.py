def get_cooklist_recipes(cooklist_id, order_by='alphabetical'):
    query = """
    SELECT r.Recipe_ID, r.Name, r.Description, r.Instructions, 
           r.Prep_Time, r.Cook_Time, r.Total_Time, r.Servings, 
           r.Difficulty_Level, r.Created_At, r.Updated_At,
           r.Image_URL, r.Video_URL, r.User_ID as Author_ID,
           u.Username as Author_Name,
           clr.Added_At as Added_To_List_At
    FROM CookList_Recipes clr
    JOIN Recipes r ON clr.Recipe_ID = r.Recipe_ID
    JOIN Users u ON r.User_ID = u.User_ID
    WHERE clr.CookList_ID = :cooklist_id
    """
    
    if order_by == 'date':
        query += " ORDER BY clr.Added_At"
    else:
        query += " ORDER BY r.Name"
    
    return execute_query(query, {'cooklist_id': cooklist_id})