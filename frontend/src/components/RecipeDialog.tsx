
import { Clock, ChefHat, List, BookOpen } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

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

interface RecipeDialogProps {
  recipe: Recipe | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const RecipeDialog = ({ recipe, open, onOpenChange }: RecipeDialogProps) => {
  if (!recipe) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-blue-700">
            {recipe.title}
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Recipe Image */}
          <div className="relative overflow-hidden rounded-lg">
            <img 
              src={recipe.image} 
              alt={recipe.title}
              className="w-full h-64 object-cover"
            />
            <div className="absolute top-2 right-2 flex gap-2">
              {recipe.isMyRecipe && (
                <Badge className="bg-blue-100 text-blue-700 border-blue-200">
                  Mine
                </Badge>
              )}
            </div>
          </div>

          {/* Duration and Cuisine */}
          <div className="flex gap-6">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-blue-700">Duration:</span>
              <span>{recipe.duration} minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <ChefHat className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-blue-700">Cuisine:</span>
              <Badge variant="outline">{recipe.cuisine}</Badge>
            </div>
          </div>

          {/* Ingredients */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <List className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-blue-700">Ingredients</h3>
            </div>
            <ul className="space-y-2">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>{ingredient}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Instructions */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-blue-700">Instructions</h3>
            </div>
            <ol className="space-y-3">
              {recipe.instructions.map((instruction, index) => (
                <li key={index} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </span>
                  <span>{instruction}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
