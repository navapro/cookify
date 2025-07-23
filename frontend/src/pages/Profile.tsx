import { useState, useEffect } from "react";
import { ArrowLeft, ChefHat, Award, Package, Search, Trash2, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { RecipeCard } from "@/components/RecipeCard";
import { getUser } from "@/utils/auth";
import { getUserDetails, getUserStats, getUserCookLists, getCookList, getUserIngredients, deleteCookList, addUserIngredient, type User, type UserStats, type Recipe, type UserIngredient } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { getCookListRecipes } from "@/services/api";
import { useLikedRecipes } from "@/contexts/LikedRecipesContext";
import { useRecipes } from "@/contexts/RecipesContext";
import { useCookLists } from "@/contexts/CookListsContext";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { CreateCooklistDialog } from "@/components/CreateCooklistDialog";

// Helper function to convert cookify level to title with emojis
const getCookifyLevelTitle = (level: string): string => {
  switch (level) {
    case "Remy the Rat":
      return "👑🐭 Remy the Rat";
    case "Michelin Star Chef":
      return "👨‍🍳 Michelin Star Chef";
    case "Head Chef":
      return "👨‍🍳 Head Chef";
    case "Sous Chef":
      return "🧂 Sous Chef";
    case "Chef":
      return "👨‍🍳 Chef";
    case "Prep Cook":
      return "🔪 Prep Cook";
    case "Dishwasher":
      return "🧽 Dishwasher";
    case "Street Rat":
      return "🐀 Street Rat";
    default:
      return `🍳 ${level}`;
  }
};

interface ProfileProps {
  onBackClick?: () => void;
}

const Profile = ({ onBackClick }: ProfileProps = {}) => {
  const navigate = useNavigate();
  const [selectedCookList, setSelectedCookList] = useState<any | null>(null);
  const [userDetails, setUserDetails] = useState<User | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [userCookLists, setUserCookLists] = useState<any[]>([]);
  const [userIngredients, setUserIngredients] = useState<UserIngredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [cookListRecipes, setCookListRecipes] = useState<any[]>([]);
  const [cookListSort, setCookListSort] = useState<'date_desc' | 'date_asc' | 'name_asc'>(
    () => (localStorage.getItem('cookListSort') as 'date_desc' | 'date_asc' | 'name_asc') || 'date_desc'
  );
  const [recipeSearchTerm, setRecipeSearchTerm] = useState<string>(
    () => localStorage.getItem('recipeSearchTerm') || ''
  );
  const [addIngredientOpen, setAddIngredientOpen] = useState(false);
  const [ingredientName, setIngredientName] = useState("");
  const [ingredientQuantity, setIngredientQuantity] = useState("");
  const [ingredientCategory, setIngredientCategory] = useState("");
  const [createCooklistDialogOpen, setCreateCooklistDialogOpen] = useState(false);
  const { toast } = useToast();
  const { likedRecipesVersion } = useLikedRecipes();
  const { userRecipes, refreshUserRecipes, recipesVersion } = useRecipes();
  const { userCookLists: contextCookLists, refreshUserCookLists, cookListsVersion } = useCookLists();
  
  // Get the current user's information
  const currentUser = getUser();
  const userName = userDetails?.name || currentUser?.name || "Chef";

  useEffect(() => {
    const fetchUserData = async () => {
      if (currentUser?.id) {
        try {
          // Fetch user details, stats, cooklists, and ingredients
          const [details, stats, cookLists, ingredients] = await Promise.all([
            getUserDetails(currentUser.id),
            getUserStats(currentUser.id),
            getUserCookLists(currentUser.id),
            getUserIngredients(currentUser.id)
          ]);
          
          setUserDetails(details);
          setUserStats({
            ...stats,
            cookify_level: getCookifyLevelTitle(stats.cookify_level) // Change from Number(details.level)
          });
          setUserCookLists(cookLists);
          setUserIngredients(ingredients);
          
          // Refresh user recipes and cooklists from context
          refreshUserRecipes();
          refreshUserCookLists();
        } catch (error) {
          console.error("Failed to fetch user data:", error);
          // Set default values if API fails
          setUserStats({
            points: 0,
            cookify_level: "🐀 Street Rat",
            recipes_created: 0,
            cooklists_created: 0
          });
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [currentUser?.id, refreshUserRecipes]);

  // Persist settings to localStorage
  useEffect(() => {
    localStorage.setItem('cookListSort', cookListSort);
  }, [cookListSort]);

  useEffect(() => {
    localStorage.setItem('recipeSearchTerm', recipeSearchTerm);
  }, [recipeSearchTerm]);

  // Sync cooklists from context when they change
  useEffect(() => {
    if (contextCookLists.length > 0 || cookListsVersion > 0) {
      setUserCookLists(contextCookLists);
    }
  }, [contextCookLists, cookListsVersion]);

  // Refresh cooklists when liked recipes change
  useEffect(() => {
    const refreshCookLists = async () => {
      if (currentUser?.id && likedRecipesVersion > 0) {
        try {
          await refreshUserCookLists();
          
          // If we're currently viewing a cooklist, refresh its recipes too
          if (selectedCookList) {
            fetchCookListRecipes(selectedCookList.id, cookListSort);
          }
        } catch (error) {
          console.error("Failed to refresh cooklists:", error);
        }
      }
    };

    refreshCookLists();
  }, [likedRecipesVersion, currentUser?.id, selectedCookList?.id, cookListSort, refreshUserCookLists]);
  
  // Also refresh user recipes when component mounts or recipesVersion changes
  useEffect(() => {
    if (currentUser?.id) {
      refreshUserRecipes();
    }
  }, [currentUser?.id, refreshUserRecipes]);

  // Refresh user stats and details when recipes change or liked recipes change
  useEffect(() => {
    const refreshUserData = async () => {
      if (currentUser?.id) {
        try {
          const [details, stats] = await Promise.all([
            getUserDetails(currentUser.id),
            getUserStats(currentUser.id)
          ]);
          
          setUserDetails(details);
          setUserStats({
            ...stats,
            cookify_level: getCookifyLevelTitle(stats.cookify_level)
          });
        } catch (error) {
          console.error("Failed to refresh user data:", error);
        }
      }
    };

    refreshUserData();
  }, [recipesVersion, likedRecipesVersion, currentUser?.id]);

  // Listen for cooklist and recipe creation events from AppSidebar
  useEffect(() => {
    const handleCooklistCreated = async () => {
      if (currentUser?.id) {
        try {
          await refreshUserCookLists();
          const stats = await getUserStats(currentUser.id);
          setUserStats({
            ...stats,
            cookify_level: getCookifyLevelTitle(stats.cookify_level)
          });
        } catch (error) {
          console.error("Failed to refresh after cooklist creation:", error);
        }
      }
    };

    const handleRecipeCreated = async () => {
      if (currentUser?.id) {
        try {
          // Refresh cooklists to update recipe counts
          await refreshUserCookLists();
        } catch (error) {
          console.error("Failed to refresh cooklists after recipe creation:", error);
        }
      }
    };

    window.addEventListener('cooklist-created', handleCooklistCreated);
    window.addEventListener('recipe-created', handleRecipeCreated);
    return () => {
      window.removeEventListener('cooklist-created', handleCooklistCreated);
      window.removeEventListener('recipe-created', handleRecipeCreated);
    };
  }, [currentUser?.id, refreshUserCookLists]);

  const handleDeleteCookList = async (cookListId: number, cookListName: string) => {
    try {
      await deleteCookList(cookListId);
      toast({
        title: "Cook List Deleted",
        description: `"${cookListName}" has been deleted successfully`,
      });
      // Refresh cook lists
      await refreshUserCookLists();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete cook list",
        variant: "destructive",
      });
    }
  };

  const handleBackClick = () => {
    if (selectedCookList) {
      setSelectedCookList(null);
    } else if (onBackClick) {
      onBackClick();
    } else {
      navigate("/");
    }
  };

  const handleAddIngredient = async () => {
    if (!ingredientName || !ingredientQuantity) {
      toast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    try {
      await addUserIngredient(currentUser.id, {
        name: ingredientName,
        quantity: ingredientQuantity,
        category: ingredientCategory || 'Other'
      });

      toast({
        title: "Success",
        description: `${ingredientName} has been added to your pantry`,
      });

      // Refresh ingredients list
      const updatedIngredients = await getUserIngredients(currentUser.id);
      setUserIngredients(updatedIngredients);

      // Reset form and close dialog
      setIngredientName("");
      setIngredientQuantity("");
      setIngredientCategory("");
      setAddIngredientOpen(false);
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add ingredient",
        variant: "destructive",
      });
    }
  };

  // Fetch cooklist details and recipes (with sorting)
  const handleCookListClick = async (cookList: any) => {
    try {
      // Fetch detailed cooklist data with recipes
      const detailedCookList = await getCookList(cookList.id);
      setSelectedCookList(detailedCookList);
      // Fetch sorted recipes for this cooklist
      fetchCookListRecipes(cookList.id, cookListSort);
    } catch (error) {
      console.error('Error fetching cooklist details:', error);
      setSelectedCookList(cookList);
      setCookListRecipes([]);
    }
  };

  // Fetch recipes for a cooklist with sorting
  const fetchCookListRecipes = async (cookListId: number, sort: string) => {
    try {
      const data = await getCookListRecipes(cookListId, sort);
      setCookListRecipes(data);
    } catch (err) {
      setCookListRecipes([]);
      toast({
        title: "Error",
        description: "Failed to fetch cooklist recipes.",
        variant: "destructive",
      });
    }
  };

  // When sort changes, refetch recipes for the selected cooklist
  useEffect(() => {
    if (selectedCookList) {
      fetchCookListRecipes(selectedCookList.id, cookListSort);
    }
    // eslint-disable-next-line
  }, [cookListSort, selectedCookList?.id]);

  // Chef level styling based on level title
  const getChefLevelStyle = (level: string) => {
    switch (level) {
      case "👑🐭 Remy the Rat":
        return { color: "text-purple-600", bgColor: "bg-purple-100" };
      case "👨‍🍳 Michelin Star Chef":
        return { color: "text-red-600", bgColor: "bg-red-100" };
      case "👨‍🍳 Head Chef":
        return { color: "text-orange-600", bgColor: "bg-orange-100" };
      case "🧂 Sous Chef":
        return { color: "text-green-600", bgColor: "bg-green-100" };
      case "👨‍🍳 Chef":
        return { color: "text-blue-600", bgColor: "bg-blue-100" };
      case "🔪 Prep Cook":
        return { color: "text-indigo-600", bgColor: "bg-indigo-100" };
      case "🧽 Dishwasher":
        return { color: "text-gray-600", bgColor: "bg-gray-100" };
      case "🐀 Street Rat":
        return { color: "text-gray-500", bgColor: "bg-gray-50" };
      default:
        return { color: "text-gray-500", bgColor: "bg-gray-50" };
    }
  };

  const chefLevelStyle = getChefLevelStyle(userStats?.cookify_level || "🐀 Street Rat");

  // Filter recipes based on search term
  const filteredRecipes = userRecipes.filter(recipe => {
    if (!recipeSearchTerm) return true;
    const searchLower = recipeSearchTerm.toLowerCase();
    return (
      recipe.title.toLowerCase().includes(searchLower) ||
      recipe.cuisine?.toLowerCase().includes(searchLower) ||
      recipe.ingredients?.some(ing => ing.toLowerCase().includes(searchLower))
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-blue-600 text-lg font-medium">Loading profile...</div>
      </div>
    );
  }

  return (
    <>
      {/* Back Button */}
      <div className="mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBackClick}
          className="hover:bg-blue-100"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {selectedCookList ? "Back to Profile" : "Back to Recipes"}
        </Button>
      </div>

      {!selectedCookList ? (
        <>
          {/* Profile Header */}
          <div className="bg-white rounded-lg shadow-sm border border-blue-100 p-4 mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
                <ChefHat className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-2xl font-bold text-blue-800 truncate">Chef {userName}</h2>
                <p className="text-blue-600 truncate">{userDetails?.email}</p>
                <div className={`inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full ${chefLevelStyle.bgColor}`}>
                  <Award className="w-4 h-4" />
                  <span className={`text-sm font-medium ${chefLevelStyle.color}`}>{userStats?.cookify_level}</span>
                </div>
              </div>
            </div>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 text-center">
                <div className="text-xl font-bold text-blue-700">{userStats?.cookify_level || "🐀 Street Rat"}</div>
                <div className="text-sm text-blue-600">Chef Level</div>
                <div className="text-xs text-blue-500 mt-1">{userDetails?.points || 0} points</div>
              </div>
              <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 text-center">
                <div className="text-xl font-bold text-blue-700">{userStats?.recipes_created || 0}</div>
                <div className="text-sm text-blue-600">Recipes</div>
              </div>
              <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 text-center">
                <div className="text-xl font-bold text-blue-700">{userStats?.cooklists_created || 0}</div>
                <div className="text-sm text-blue-600">Cook Lists</div>
              </div>
            </div>
          </div>

          {/* My Recipes Section */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-blue-800">My Recipes</h3>
              {userRecipes.length > 0 && (
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search recipes..."
                    value={recipeSearchTerm}
                    onChange={(e) => setRecipeSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-1 text-sm w-48"
                  />
                </div>
              )}
            </div>
            
            {userRecipes.length > 0 ? (
              filteredRecipes.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredRecipes.map((recipe: Recipe) => (
                    <RecipeCard key={recipe.id} recipe={recipe} showDeleteButton={true} />
                  ))}
                </div>
              ) : (
                <div className="bg-white rounded-lg border border-blue-100 p-8 text-center">
                  <ChefHat className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                  <p className="text-blue-600">No recipes found matching your search.</p>
                </div>
              )
            ) : (
              <div className="bg-white rounded-lg border border-blue-100 p-8 text-center">
                <ChefHat className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                <p className="text-blue-600 font-medium mb-2">No recipes yet!</p>
                <p className="text-sm text-blue-500">Create your first recipe to see it here.</p>
              </div>
            )}
          </div>

          {/* Cook Lists Section */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-blue-800 mb-4">My Cook Lists</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {userCookLists.map((cookList) => (
                <div
                  key={cookList.id}
                  className="bg-white rounded-lg border border-blue-100 p-4 hover:shadow-md transition-shadow cursor-pointer relative group"
                  onClick={() => handleCookListClick(cookList)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-blue-800 truncate pr-2">{cookList.name}</h4>
                    <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      {cookList.recipeCount} recipes
                    </span>
                  </div>
                  <p className="text-blue-600 text-sm line-clamp-2">{cookList.description}</p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteCookList(cookList.id, cookList.name);
                    }}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 text-red-600 hover:bg-red-50 rounded transition-opacity"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              
              {/* Add Cooklist Button */}
              <div
                className="bg-white rounded-lg border-2 border-dashed border-blue-300 p-4 hover:shadow-md hover:border-blue-400 transition-all cursor-pointer flex flex-col items-center justify-center min-h-[120px] group"
                onClick={() => setCreateCooklistDialogOpen(true)}
              >
                <Plus className="w-8 h-8 text-blue-400 group-hover:text-blue-600 mb-2" />
                <h4 className="font-semibold text-blue-600 group-hover:text-blue-700">Add Cooklist</h4>
                <p className="text-blue-500 text-sm mt-1">Create a new collection</p>
              </div>
              
              {userCookLists.length === 0 && (
                <div className="col-span-full bg-white rounded-lg border border-blue-100 p-8 text-center">
                  <ChefHat className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                  <p className="text-blue-600 font-medium mb-2">No cook lists yet!</p>
                  <p className="text-sm text-blue-500">Click "Add Cooklist" to create your first collection.</p>
                </div>
              )}
            </div>
          </div>

          {/* My Pantry Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-blue-800">My Pantry</h3>
              <Dialog open={addIngredientOpen} onOpenChange={setAddIngredientOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" className="bg-green-600 hover:bg-green-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add to Pantry
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Ingredient to Pantry</DialogTitle>
                    <DialogDescription>
                      Add a new ingredient to your pantry inventory.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 pt-4">
                    <div>
                      <Label htmlFor="ingredient-name">Ingredient Name *</Label>
                      <Input
                        id="ingredient-name"
                        value={ingredientName}
                        onChange={(e) => setIngredientName(e.target.value)}
                        placeholder="e.g., Tomatoes"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="ingredient-quantity">Quantity *</Label>
                      <Input
                        id="ingredient-quantity"
                        value={ingredientQuantity}
                        onChange={(e) => setIngredientQuantity(e.target.value)}
                        placeholder="e.g., 2 lbs, 500g, 3 pieces"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="ingredient-category">Category (Optional)</Label>
                      <Input
                        id="ingredient-category"
                        value={ingredientCategory}
                        onChange={(e) => setIngredientCategory(e.target.value)}
                        placeholder="e.g., Vegetables, Dairy, Meat"
                        className="mt-1"
                      />
                    </div>
                    <div className="flex justify-end gap-2 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => {
                          setIngredientName("");
                          setIngredientQuantity("");
                          setIngredientCategory("");
                          setAddIngredientOpen(false);
                        }}
                      >
                        Cancel
                      </Button>
                      <Button onClick={handleAddIngredient}>
                        Add Ingredient
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <div className="bg-white rounded-lg border border-blue-100 p-4">
              {userIngredients.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {userIngredients.map((ingredient) => (
                    <div
                      key={ingredient.ingredient_id}
                      className="bg-green-50 rounded-lg p-3 border border-green-100"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Package className="w-4 h-4 text-green-600" />
                        <h4 className="font-medium text-green-800 text-sm">{ingredient.name}</h4>
                      </div>
                      <p className="text-green-700 text-sm">
                        Qty: {ingredient.quantity}
                      </p>
                      {ingredient.category && (
                        <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded mt-1 inline-block">
                          {ingredient.category}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Package className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                  <p className="text-blue-600 font-medium mb-2">Your pantry is empty!</p>
                  <p className="text-sm text-blue-500">Add ingredients to track what you have.</p>
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Cook List Detail View */}
          <div className="bg-white rounded-lg shadow-sm border border-blue-100 p-4 mb-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                <ChefHat className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-blue-800">{selectedCookList.name}</h2>
                <p className="text-blue-600">{selectedCookList.recipeCount} recipes</p>
              </div>
            </div>
            
            {/* Sort Buttons */}
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={cookListSort === "date_desc" ? "default" : "outline"}
                onClick={() => setCookListSort("date_desc")}
              >
                Newest
              </Button>
              <Button
                size="sm"
                variant={cookListSort === "date_asc" ? "default" : "outline"}
                onClick={() => setCookListSort("date_asc")}
              >
                Oldest
              </Button>
              <Button
                size="sm"
                variant={cookListSort === "name_asc" ? "default" : "outline"}
                onClick={() => setCookListSort("name_asc")}
              >
                A-Z
              </Button>
            </div>
          </div>

          {/* Cook List Recipes */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cookListRecipes.map(recipe => (
              <RecipeCard key={recipe.id} recipe={{
                ...recipe,
                title: recipe.name,
                image: recipe.image || "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300",
                ingredients: recipe.ingredients || [],
                instructions: recipe.instructions || [],
                added_at: recipe.added_at,
              }} />
            ))}
          </div>
        </>
      )}
      
      <CreateCooklistDialog 
        open={createCooklistDialogOpen} 
        onOpenChange={setCreateCooklistDialogOpen}
        onCooklistCreated={async () => {
          // Refresh cooklists after creation
          if (currentUser?.id) {
            const updatedCookLists = await getUserCookLists(currentUser.id);
            setUserCookLists(updatedCookLists);
            
            // Also update user stats if available
            const stats = await getUserStats(currentUser.id);
            setUserStats({
              ...stats,
              cookify_level: getCookifyLevelTitle(stats.cookify_level)
            });
          }
        }}
      />
    </>
  );
};

export default Profile;