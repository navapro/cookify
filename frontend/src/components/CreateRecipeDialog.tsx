import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, X, Upload } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface CreateRecipeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const cuisines = [
  "Italian", "Mexican", "Chinese", "Indian", "French", 
  "Japanese", "Thai", "Mediterranean", "American", "Korean", "British"
];

const durations = [
  { label: "Quick (15 min)", value: 15 },
  { label: "Short (30 min)", value: 30 },
  { label: "Medium (45 min)", value: 45 },
  { label: "Long (60 min)", value: 60 },
  { label: "Extended (90 min)", value: 90 },
  { label: "All Day (120+ min)", value: 120 },
];

export const CreateRecipeDialog = ({ open, onOpenChange }: CreateRecipeDialogProps) => {
  const [title, setTitle] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [duration, setDuration] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [ingredients, setIngredients] = useState<string[]>([""]);
  const [instructions, setInstructions] = useState<string[]>([""]);
  const { toast } = useToast();

  const handleAddIngredient = () => {
    setIngredients([...ingredients, ""]);
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleIngredientChange = (index: number, value: string) => {
    const updated = ingredients.map((ing, i) => i === index ? value : ing);
    setIngredients(updated);
  };

  const handleAddInstruction = () => {
    setInstructions([...instructions, ""]);
  };

  const handleRemoveInstruction = (index: number) => {
    setInstructions(instructions.filter((_, i) => i !== index));
  };

  const handleInstructionChange = (index: number, value: string) => {
    const updated = instructions.map((inst, i) => i === index ? value : inst);
    setInstructions(updated);
  };

  const handleSubmit = () => {
    console.log("Creating recipe:", {
      title,
      cuisine,
      duration: parseInt(duration),
      imageUrl,
      ingredients: ingredients.filter(ing => ing.trim() !== ""),
      instructions: instructions.filter(inst => inst.trim() !== "")
    });
    
    // Show success toast
    toast({
      title: "Recipe Created Successfully! 🍳",
      description: `"${title}" has been added to your collection. Gordon would be proud!`,
    });
    
    // Reset form
    setTitle("");
    setCuisine("");
    setDuration("");
    setImageUrl("");
    setIngredients([""]);
    setInstructions([""]);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-blue-50 to-indigo-50">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-blue-800 flex items-center gap-2">
            🍳 Create Your Masterpiece
          </DialogTitle>
          <p className="text-blue-600 italic">"Cooking is not about convenience" - Gordon Ramsay</p>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Recipe Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-blue-800 font-medium">Recipe Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Give your dish a name worthy of Gusteau..."
              className="border-blue-200 focus:border-blue-400"
            />
          </div>

          {/* Image Upload */}
          <div className="space-y-2">
            <Label htmlFor="image" className="text-blue-800 font-medium">Recipe Image</Label>
            <div className="flex gap-2">
              <Input
                id="image"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="Enter image URL or upload..."
                className="border-blue-200 focus:border-blue-400"
              />
              <Button variant="outline" className="border-blue-200 hover:bg-blue-50">
                <Upload className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Cuisine and Duration */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-blue-800 font-medium">Cuisine Type</Label>
              <Select value={cuisine} onValueChange={setCuisine}>
                <SelectTrigger className="border-blue-200 focus:border-blue-400">
                  <SelectValue placeholder="Choose cuisine..." />
                </SelectTrigger>
                <SelectContent>
                  {cuisines.map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-blue-800 font-medium">Cooking Duration</Label>
              <Select value={duration} onValueChange={setDuration}>
                <SelectTrigger className="border-blue-200 focus:border-blue-400">
                  <SelectValue placeholder="Select duration..." />
                </SelectTrigger>
                <SelectContent>
                  {durations.map((d) => (
                    <SelectItem key={d.value} value={d.value.toString()}>{d.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Ingredients */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-blue-800 font-medium">Ingredients</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddIngredient}
                className="border-blue-200 hover:bg-blue-50"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Ingredient
              </Button>
            </div>
            <div className="space-y-2">
              {ingredients.map((ingredient, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={ingredient}
                    onChange={(e) => handleIngredientChange(index, e.target.value)}
                    placeholder="Enter ingredient..."
                    className="border-blue-200 focus:border-blue-400"
                  />
                  {ingredients.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => handleRemoveIngredient(index)}
                      className="border-blue-200 hover:bg-red-50"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Instructions */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-blue-800 font-medium">Cooking Instructions</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddInstruction}
                className="border-blue-200 hover:bg-blue-50"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Step
              </Button>
            </div>
            <div className="space-y-2">
              {instructions.map((instruction, index) => (
                <div key={index} className="flex gap-2">
                  <div className="flex-1">
                    <Textarea
                      value={instruction}
                      onChange={(e) => handleInstructionChange(index, e.target.value)}
                      placeholder={`Step ${index + 1}: Describe this cooking step...`}
                      className="border-blue-200 focus:border-blue-400 min-h-[60px]"
                    />
                  </div>
                  {instructions.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => handleRemoveInstruction(index)}
                      className="border-blue-200 hover:bg-red-50 self-start mt-2"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex gap-2 pt-4">
            <Button
              onClick={handleSubmit}
              disabled={!title || !cuisine || !duration}
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              Create Recipe
            </Button>
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-blue-200 hover:bg-blue-50"
            >
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
