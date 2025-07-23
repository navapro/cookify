
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
import { createCookList } from "@/services/api";
import { getUser } from "@/utils/auth";
import { useCookLists } from "@/contexts/CookListsContext";

interface CreateCooklistDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCooklistCreated?: () => void;
}

export const CreateCooklistDialog = ({ open, onOpenChange, onCooklistCreated }: CreateCooklistDialogProps) => {
  const [cooklistName, setCooklistName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const currentUser = getUser();
  const { refreshUserCookLists } = useCookLists();

  const handleCreate = async () => {
    if (cooklistName.trim() && currentUser) {
      setIsLoading(true);
      try {
        await createCookList(cooklistName.trim(), "", currentUser.id);
        
        toast({
          title: "Cooklist Created Successfully! 📚",
          description: `"${cooklistName}" is ready for your culinary collection!`,
        });
        
        // Refresh cooklists to update the list
        await refreshUserCookLists();
        
        setCooklistName("");
        onOpenChange(false);
        onCooklistCreated?.();
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to create cooklist",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
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
              disabled={!cooklistName.trim() || isLoading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? "Creating..." : "Create"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
