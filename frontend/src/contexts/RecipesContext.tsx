import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { Recipe, getUserRecipes } from "@/services/api";
import { getUser } from "@/utils/auth";

interface RecipesContextType {
  userRecipes: Recipe[];
  setUserRecipes: (recipes: Recipe[]) => void;
  refreshUserRecipes: () => Promise<void>;
  recipesVersion: number;
}

const RecipesContext = createContext<RecipesContextType | undefined>(undefined);

export const RecipesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userRecipes, setUserRecipes] = useState<Recipe[]>([]);
  const [recipesVersion, setRecipesVersion] = useState(0);

  const refreshUserRecipes = useCallback(async () => {
    const currentUser = getUser();
    if (currentUser?.id) {
      try {
        const recipes = await getUserRecipes(currentUser.id);
        setUserRecipes(recipes);
        setRecipesVersion(prev => prev + 1);
      } catch (error) {
        console.error("Failed to refresh user recipes:", error);
      }
    }
  }, []);

  return (
    <RecipesContext.Provider value={{
      userRecipes,
      setUserRecipes,
      refreshUserRecipes,
      recipesVersion
    }}>
      {children}
    </RecipesContext.Provider>
  );
};

export const useRecipes = () => {
  const context = useContext(RecipesContext);
  if (context === undefined) {
    throw new Error("useRecipes must be used within a RecipesProvider");
  }
  return context;
};