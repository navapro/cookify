
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

interface CreateCooklistDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CreateCooklistDialog = ({ open, onOpenChange }: CreateCooklistDialogProps) => {
  const [cooklistName, setCooklistName] = useState("");
  const { toast } = useToast();

  const handleCreate = () => {
    if (cooklistName.trim()) {
      console.log(`Creating cooklist: "${cooklistName}"`);
      
      // Show success toast
      toast({
        title: "Cooklist Created Successfully! 📚",
        description: `"${cooklistName}" is ready for your culinary collection!`,
      });
      
      setCooklistName("");
      onOpenChange(false);
    }
  };

  const handleCancel = () => {
    setCooklistName("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-gradient-to-br from-blue-50 to-indigo-50">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-blue-700">
            Create Cooklist
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cooklist-name" className="text-sm font-medium text-blue-800">
              Cooklist Name
            </Label>
            <Input
              id="cooklist-name"
              type="text"
              placeholder="Enter cooklist name..."
              value={cooklistName}
              onChange={(e) => setCooklistName(e.target.value)}
              className="w-full border-blue-200 focus:border-blue-400"
            />
          </div>
          
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={handleCancel}
              className="px-4 py-2 border-blue-200 hover:bg-blue-50"
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={!cooklistName.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              Create
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
