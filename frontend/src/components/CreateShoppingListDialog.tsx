import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ShoppingCart, Plus } from "lucide-react";
import { createShoppingList, getCookLists, type CookList } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface CreateShoppingListDialogProps {
  onShoppingListCreated: () => void;
  children?: React.ReactNode;
}

export function CreateShoppingListDialog({
  onShoppingListCreated,
  children,
}: CreateShoppingListDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [selectedCookListId, setSelectedCookListId] = useState<string>('');
  const [cookLists, setCookLists] = useState<CookList[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      fetchCookLists();
    }
  }, [open]);

  const fetchCookLists = async () => {
    try {
      const lists = await getCookLists();
      setCookLists(lists);
    } catch (error) {
      console.error('Failed to fetch cook lists:', error);
      toast({
        title: "Error",
        description: "Failed to load cook lists",
        variant: "destructive",
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast({
        title: "Error",
        description: "Please enter a name for your shopping list",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      const cookListId = selectedCookListId ? parseInt(selectedCookListId) : undefined;
      await createShoppingList(name.trim(), cookListId);
      
      toast({
        title: "Success",
        description: "Shopping list created successfully!",
      });
      
      setName('');
      setSelectedCookListId('');
      setOpen(false);
      onShoppingListCreated();
    } catch (error) {
      console.error('Failed to create shopping list:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create shopping list",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Create Shopping List
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" />
            Create Shopping List
          </DialogTitle>
          <DialogDescription>
            Create a new shopping list. You can link it to a cook list to automatically add all ingredients.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter shopping list name"
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="cooklist">Cook List (Optional)</Label>
            <Select value={selectedCookListId} onValueChange={setSelectedCookListId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a cook list to link" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">None - Create empty list</SelectItem>
                {cookLists.map((cookList) => (
                  <SelectItem key={cookList.id} value={cookList.id.toString()}>
                    {cookList.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Creating..." : "Create Shopping List"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}