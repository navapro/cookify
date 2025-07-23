
import { useState, useEffect } from "react";
import { Clock, ChefHat, Plus, Heart } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RecipeDialog } from "./RecipeDialog";
import { CookListDialog } from "./CookListDialog";
import { useToast } from "@/hooks/use-toast";
import { likeRecipe, unlikeRecipe, checkRecipeLiked } from "@/services/api";
import { useLikedRecipes } from "@/contexts/LikedRecipesContext";

interface Recipe {
  id: number;
  title: string;
  image: string;
  duration: number;
  cuisine: string;
  ingredients: string[];
  instructions: string[];
  isMyRecipe?: boolean;
  added_at?: string; 
}

interface RecipeCardProps {
  recipe: Recipe;
}

export const RecipeCard = ({ recipe }: RecipeCardProps) => {
  const [recipeDialogOpen, setRecipeDialogOpen] = useState(false);
  const [cookListDialogOpen, setCookListDialogOpen] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const { refreshLikedRecipes } = useLikedRecipes();

  // Check if recipe is liked when component mounts
  useEffect(() => {
    const checkLikedStatus = async () => {
      try {
        // Only check liked status if user is logged in
        const token = localStorage.getItem("access_token");
        if (!token) {
          setIsLiked(false);
          return;
        }
        
        const response = await checkRecipeLiked(recipe.id);
        setIsLiked(response.isLiked);
      } catch (error) {
        // If user is not logged in or other error, default to false
        setIsLiked(false);
      }
    };

    checkLikedStatus();
  }, [recipe.id]);

  const handleViewRecipe = () => {
    setRecipeDialogOpen(true);
  };

  const handleAddToCookList = () => {
    setCookListDialogOpen(true);
  };

  const handleLikeRecipe = async () => {
    setIsLoading(true);
    try {
      if (isLiked) {
        await unlikeRecipe(recipe.id);
        setIsLiked(false);
        toast({
          title: "Recipe Unliked! 💔",
          description: `"${recipe.title}" has been removed from your liked recipes`,
        });
      } else {
        await likeRecipe(recipe.id);
        setIsLiked(true);
        toast({
          title: "Recipe Liked! ❤️",
          description: `"${recipe.title}" has been added to your liked recipes`,
        });
      }
      // Trigger refresh of liked recipes in parent components
      refreshLikedRecipes();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update recipe like status",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Card className="group hover:shadow-lg transition-all duration-300 overflow-hidden border-2 hover:border-blue-200">
        <CardHeader className="p-0">
          <div className="relative overflow-hidden rounded-t-lg">
            <img 
              src={recipe.image || "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300"}
              alt={recipe.title}
              className="w-full h-48 object-cover rounded-t-lg transition-transform duration-500 group-hover:scale-105"
              onError={(e) => {
                e.currentTarget.src = "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300";
              }}
            />
            <div className="absolute top-2 right-2 flex gap-2">
              <Badge variant="secondary" className="bg-white/90 text-blue-700">
                <Clock className="w-3 h-3 mr-1" />
                {recipe.duration}min
              </Badge>
              {recipe.isMyRecipe && (
                <Badge className="bg-blue-100 text-blue-700 border-blue-200">
                  Mine
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-4">
          <h3 className="font-semibold text-lg mb-2 group-hover:text-blue-600 transition-colors">
            {recipe.title}
          </h3>
          
          <div className="mb-3">
            <Badge variant="outline" className="text-xs">
              <ChefHat className="w-3 h-3 mr-1" />
              {recipe.cuisine}
            </Badge>
          </div>
          
          <div className="space-y-3">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Ingredients:</h4>
              <p className="text-sm text-gray-600 line-clamp-2">
                {recipe.ingredients && recipe.ingredients.length > 0 
                  ? `${recipe.ingredients.slice(0, 3).join(", ")}${recipe.ingredients.length > 3 ? "..." : ""}`
                  : "No ingredients listed"
                }
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Instructions:</h4>
              <p className="text-sm text-gray-600 line-clamp-2">
                {recipe.instructions && recipe.instructions.length > 0 
                  ? recipe.instructions[0]
                  : "No instructions available"
                }
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Added at:</h4>
              <p className="text-sm text-gray-600 line-clamp-2">
                {recipe.added_at 
                  ? new Date(recipe.added_at).toLocaleString()
                  : "Date not available"
                }
              </p>
            </div> 
          </div>
        </CardContent>
        
        <CardFooter className="p-4 pt-0 flex gap-2">
          <button 
            onClick={handleViewRecipe}
            className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 py-2 px-3 rounded-lg transition-colors duration-200 font-medium text-sm"
          >
            View Recipe
          </button>
          <button 
            onClick={handleAddToCookList}
            className="flex-1 bg-green-50 hover:bg-green-100 text-green-700 py-2 px-3 rounded-lg transition-colors duration-200 font-medium flex items-center justify-center gap-1 text-sm"
          >
            <Plus className="w-3 h-3" />
            Add to Cook List
          </button>
          <button 
            onClick={handleLikeRecipe}
            disabled={isLoading}
            className={`flex-1 py-2 px-3 rounded-lg transition-colors duration-200 font-medium flex items-center justify-center gap-1 text-sm ${
              isLiked 
                ? 'bg-red-50 hover:bg-red-100 text-red-700' 
                : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? (
              <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : (
              <Heart className={`w-3 h-3 ${isLiked ? 'fill-current' : ''}`} />
            )}
            Like Recipe
          </button>
        </CardFooter>
      </Card>

      <RecipeDialog 
        recipe={recipe} 
        open={recipeDialogOpen} 
        onOpenChange={setRecipeDialogOpen} 
      />
      
      <CookListDialog 
        recipe={recipe} 
        open={cookListDialogOpen} 
        onOpenChange={setCookListDialogOpen} 
      />
    </>
  );
};
