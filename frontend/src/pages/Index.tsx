import { useState, useEffect } from "react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { FilterBar } from "@/components/FilterBar";
import { RecipeCard } from "@/components/RecipeCard";
import { searchRecipes } from "@/services/api";
import type { Recipe } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Package, User } from "lucide-react";
import Profile from "./Profile";
import { useRecipes } from "@/contexts/RecipesContext";
import { getUser } from "@/utils/auth";

const Index = () => {
  const [showProfile, setShowProfile] = useState(false);
  const currentUser = getUser();
  const [durationFilter, setDurationFilter] = useState<{ operator: string; value: number }>(
    () => JSON.parse(localStorage.getItem('durationFilter') || '{"operator": "none", "value": 0}')
  );
  const [searchFilter, setSearchFilter] = useState(
    () => localStorage.getItem('searchFilter') || ''
  );
  const [cuisineFilter, setCuisineFilter] = useState<string[]>(
    () => JSON.parse(localStorage.getItem('cuisineFilter') || '[]')
  );
  const [myRecipesOnly, setMyRecipesOnly] = useState(
    () => localStorage.getItem('myRecipesOnly') === 'true'
  );
  const [searchMyIngredients, setSearchMyIngredients] = useState(
    () => localStorage.getItem('searchMyIngredients') === 'true'
  );
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalRecipes, setTotalRecipes] = useState(0);
  const { toast } = useToast();
  const { recipesVersion } = useRecipes();

  // Debounce search to avoid too many API calls
  const [debouncedSearchFilter, setDebouncedSearchFilter] = useState("");
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchFilter(searchFilter);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchFilter]);

  // Persist settings to localStorage
  useEffect(() => {
    localStorage.setItem('durationFilter', JSON.stringify(durationFilter));
  }, [durationFilter]);

  useEffect(() => {
    localStorage.setItem('searchFilter', searchFilter);
  }, [searchFilter]);

  useEffect(() => {
    localStorage.setItem('cuisineFilter', JSON.stringify(cuisineFilter));
  }, [cuisineFilter]);

  useEffect(() => {
    localStorage.setItem('myRecipesOnly', myRecipesOnly.toString());
  }, [myRecipesOnly]);

  useEffect(() => {
    localStorage.setItem('searchMyIngredients', searchMyIngredients.toString());
  }, [searchMyIngredients]);

  // Function to fetch recipes
  const fetchRecipes = async () => {
    setLoading(true);
    try {
      // Map duration filter to backend format
      let duration = "none";
      if (durationFilter.operator === "lte" && durationFilter.value === 30) {
        duration = "short";
      } else if (durationFilter.operator === "range") {
        duration = "medium";
      } else if (durationFilter.operator === "gte" && durationFilter.value === 60) {
        duration = "long";
      }

      const data = await searchRecipes({
        search: debouncedSearchFilter,
        duration: duration !== "none" ? duration : undefined,
        cuisines: cuisineFilter.length > 0 ? cuisineFilter : undefined,
        myRecipes: myRecipesOnly,
        searchMyIngredients: searchMyIngredients,
        limit: 50
      });
      
      // Transform API data to match our Recipe interface
      const formattedRecipes = data.map((recipe: any) => ({
        id: recipe.id,
        title: recipe.name,
        image: recipe.image_url || "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300",
        duration: recipe.duration || 30,
        cuisine: recipe.cuisine || "Unknown",
        ingredients: recipe.ingredients || [],
        instructions: recipe.instructions ? recipe.instructions.split('\n').filter(Boolean) : [],
        isMyRecipe: recipe.is_my_recipe
      }));
      setRecipes(formattedRecipes);
      setTotalRecipes(formattedRecipes.length);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch recipes. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch recipes when filters change or when a new recipe is created
  useEffect(() => {
    fetchRecipes();
  }, [durationFilter, debouncedSearchFilter, cuisineFilter, myRecipesOnly, searchMyIngredients, recipesVersion]);

  // Listen for recipe creation events
  useEffect(() => {
    const handleRecipeCreated = () => {
      fetchRecipes();
    };

    window.addEventListener('recipe-created', handleRecipeCreated);
    return () => window.removeEventListener('recipe-created', handleRecipeCreated);
  }, []);

  // Handler for when a recipe is deleted
  const handleRecipeDeleted = () => {
    fetchRecipes();
  };

  const handleDurationChange = (operator: string, value: number) => {
    setDurationFilter({ operator, value });
  };

  const handleSearchChange = (search: string) => {
    setSearchFilter(search);
  };

  const handleCuisineChange = (cuisines: string[]) => {
    setCuisineFilter(cuisines);
  };

  const handleMyRecipesToggle = (enabled: boolean) => {
    setMyRecipesOnly(enabled);
  };

  const handleReset = () => {
    setDurationFilter({ operator: "none", value: 0 });
    setSearchFilter("");
    setCuisineFilter([]);
    setMyRecipesOnly(false);
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-blue-100 via-blue-50 to-indigo-50 relative">
        {/* Grainy texture overlay */}
        <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,0.8)_1px,transparent_0)] bg-[length:20px_20px]"></div>
        
        <div className="flex-1 flex flex-col relative z-10">
          <header className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white border-b-2 border-blue-700 p-4 shadow-xl">
            <div className="flex items-center justify-between gap-4 w-full">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold">🍳 Cookify</h1>
                <p className="text-blue-100 text-sm italic hidden sm:block">Spotify but for recipes</p>
              </div>
              
              <div className="flex items-center gap-4">
                {currentUser && (
                  <div className="flex items-center gap-2 bg-blue-700/30 px-3 py-2 rounded-lg">
                    <User className="w-4 h-4 text-blue-100" />
                    <span className="text-sm font-medium text-blue-100">
                      {currentUser.name}
                    </span>
                  </div>
                )}
                
                <div className="flex items-center space-x-2 bg-blue-700/30 px-3 py-2 rounded-lg">
                  <Package className="w-4 h-4 text-blue-100" />
                  <Switch
                    id="ingredient-mode"
                    checked={searchMyIngredients}
                    onCheckedChange={setSearchMyIngredients}
                    className="data-[state=checked]:bg-green-500"
                  />
                  <Label htmlFor="ingredient-mode" className="text-sm font-medium text-blue-100 cursor-pointer">
                    Search my ingredients
                  </Label>
                </div>
                
                <SidebarTrigger className="hover:bg-blue-500 hover:text-white text-blue-100" />
              </div>
            </div>
          </header>
          
          {!showProfile && (
            <FilterBar
              onDurationChange={handleDurationChange}
              onSearchChange={handleSearchChange}
              onCuisineChange={handleCuisineChange}
              onMyRecipesToggle={handleMyRecipesToggle}
              onReset={handleReset}
            />
          )}
          
          <main className="flex-1 p-6">
            {showProfile ? (
              <Profile onBackClick={() => setShowProfile(false)} />
            ) : (
              <>
                <div className="mb-4">
                  <p className="text-blue-800 font-medium">
                    {loading ? "Loading recipes..." : (
                      <>
                        Showing {recipes.length} recipes
                        {searchMyIngredients && (
                          <span className="ml-2 text-green-600">
                            <Package className="inline w-4 h-4 mr-1" />
                            (matching your ingredients)
                          </span>
                        )}
                      </>
                    )}
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {recipes.map(recipe => (
                    <RecipeCard 
                      key={recipe.id} 
                      recipe={recipe} 
                      showDeleteButton={true}
                      onDelete={handleRecipeDeleted}
                    />
                  ))}
                </div>
                
                {!loading && recipes.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-blue-700 text-lg font-medium">
                      {searchMyIngredients 
                        ? "No recipes match all your ingredients." 
                        : "No recipes match your current filters."}
                    </p>
                    <p className="text-blue-600 mt-2">
                      {searchMyIngredients 
                        ? "Try adding more ingredients to your pantry or turn off ingredient filtering." 
                        : "Even Gordon would be stumped! Try adjusting your search criteria."}
                    </p>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
        <AppSidebar onProfileClick={() => setShowProfile(true)} />
      </div>
    </SidebarProvider>
  );
};

export default Index;
