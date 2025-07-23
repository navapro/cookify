import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { getUserCookLists } from "@/services/api";
import { getUser } from "@/utils/auth";

interface CookList {
  id: number;
  name: string;
  description: string;
  recipeCount: number;
}

interface CookListsContextType {
  userCookLists: CookList[];
  setUserCookLists: (cookLists: CookList[]) => void;
  refreshUserCookLists: () => Promise<void>;
  cookListsVersion: number;
}

const CookListsContext = createContext<CookListsContextType | undefined>(undefined);

export const CookListsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userCookLists, setUserCookLists] = useState<CookList[]>([]);
  const [cookListsVersion, setCookListsVersion] = useState(0);

  const refreshUserCookLists = useCallback(async () => {
    const currentUser = getUser();
    if (currentUser?.id) {
      try {
        const cookLists = await getUserCookLists(currentUser.id);
        setUserCookLists(cookLists);
        setCookListsVersion(prev => prev + 1);
      } catch (error) {
        console.error("Failed to refresh user cooklists:", error);
      }
    }
  }, []);

  return (
    <CookListsContext.Provider value={{
      userCookLists,
      setUserCookLists,
      refreshUserCookLists,
      cookListsVersion
    }}>
      {children}
    </CookListsContext.Provider>
  );
};

export const useCookLists = () => {
  const context = useContext(CookListsContext);
  if (context === undefined) {
    throw new Error("useCookLists must be used within a CookListsProvider");
  }
  return context;
};