import { createContext, useContext, useCallback, useState } from "react";

interface LikedRecipesContextType {
  refreshLikedRecipes: () => void;
  likedRecipesVersion: number;
}

const LikedRecipesContext = createContext<LikedRecipesContextType | undefined>(undefined);

export const useLikedRecipes = () => {
  const context = useContext(LikedRecipesContext);
  if (!context) {
    throw new Error("useLikedRecipes must be used within a LikedRecipesProvider");
  }
  return context;
};

export const LikedRecipesProvider = ({ children }: { children: React.ReactNode }) => {
  const [likedRecipesVersion, setLikedRecipesVersion] = useState(0);

  const refreshLikedRecipes = useCallback(() => {
    setLikedRecipesVersion(prev => prev + 1);
  }, []);

  return (
    <LikedRecipesContext.Provider value={{ refreshLikedRecipes, likedRecipesVersion }}>
      {children}
    </LikedRecipesContext.Provider>
  );
};