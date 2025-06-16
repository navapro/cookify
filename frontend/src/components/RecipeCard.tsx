
import { useState } from "react";
import { Clock, ChefHat, Plus } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RecipeDialog } from "./RecipeDialog";
import { CookListDialog } from "./CookListDialog";

interface Recipe {
  id: number;
  title: string;
  image: string;
  duration: number;
  cuisine: string;
  ingredients: string[];
  instructions: string[];
  isMyRecipe?: boolean;
}

interface RecipeCardProps {
  recipe: Recipe;
}

export const RecipeCard = ({ recipe }: RecipeCardProps) => {
  const [recipeDialogOpen, setRecipeDialogOpen] = useState(false);
  const [cookListDialogOpen, setCookListDialogOpen] = useState(false);

  const handleViewRecipe = () => {
    setRecipeDialogOpen(true);
  };

  const handleAddToCookList = () => {
    setCookListDialogOpen(true);
  };

  return (
    <>
      <Card className="group hover:shadow-lg transition-all duration-300 overflow-hidden border-2 hover:border-blue-200">
        <CardHeader className="p-0">
          <div className="relative overflow-hidden rounded-t-lg">
            <img 
              src={recipe.image} 
              alt={recipe.title}
              className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
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
                {recipe.ingredients.slice(0, 3).join(", ")}
                {recipe.ingredients.length > 3 && "..."}
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Instructions:</h4>
              <p className="text-sm text-gray-600 line-clamp-2">
                {recipe.instructions[0]}
              </p>
            </div>
          </div>
        </CardContent>
        
        <CardFooter className="p-4 pt-0 flex gap-2">
          <button 
            onClick={handleViewRecipe}
            className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 py-2 px-4 rounded-lg transition-colors duration-200 font-medium"
          >
            View Recipe
          </button>
          <button 
            onClick={handleAddToCookList}
            className="flex-1 bg-green-50 hover:bg-green-100 text-green-700 py-2 px-4 rounded-lg transition-colors duration-200 font-medium flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add to Cook List
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
