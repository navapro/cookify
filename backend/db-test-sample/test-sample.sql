-- feature 3: viewing a cooklist sample queries
-- creating a cooklist
INSERT INTO CookLists (User_ID, Name, Description, Is_Public)
VALUES (:user_id, :name, :description, :is_public);

-- add a recipe to a cooklist
INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID)
VALUES (:cooklist_id, :recipe_id);

-- select ordered list of cooklist recipes (ordered by date)
SELECT r.Recipe_ID, r.Name, r.Description, r.Instructions,  
r.Difficulty_Level, clr.Added_At as Added_To_List_At
FROM CookList_Recipes clr
JOIN Recipes r ON clr.Recipe_ID = r.Recipe_ID
JOIN Users u ON r.User_ID = u.User_ID
WHERE clr.CookList_ID = :cooklist_id
ORDER BY clr.Added_At;

-- select ordered list of cooklist recipes (ordered by date)
SELECT r.Recipe_ID, r.Name, r.Description, r.Instructions,  
r.Difficulty_Level, clr.Added_At as Added_To_List_At
FROM CookList_Recipes clr
JOIN Recipes r ON clr.Recipe_ID = r.Recipe_ID
JOIN Users u ON r.User_ID = u.User_ID
WHERE clr.CookList_ID = :cooklist_id
ORDER BY r.Name;