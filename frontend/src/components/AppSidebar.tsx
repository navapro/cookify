
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, BookOpen, User } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { CreateCooklistDialog } from "./CreateCooklistDialog";
import { CreateRecipeDialog } from "./CreateRecipeDialog";

const sidebarItems = [
  {
    title: "Create Recipe",
    icon: Plus,
    action: "create-recipe",
  },
  {
    title: "Create Cooklist",
    icon: BookOpen,
    action: "create-cooklist",
  },
  {
    title: "My Profile",
    icon: User,
    action: "my-profile",
  },
];

export function AppSidebar() {
  const [createCooklistDialogOpen, setCreateCooklistDialogOpen] = useState(false);
  const [createRecipeDialogOpen, setCreateRecipeDialogOpen] = useState(false);
  const navigate = useNavigate();

  const handleAction = (action: string) => {
    console.log(`Action triggered: ${action}`);
    
    if (action === "create-cooklist") {
      setCreateCooklistDialogOpen(true);
    } else if (action === "create-recipe") {
      setCreateRecipeDialogOpen(true);
    } else if (action === "my-profile") {
      navigate("/profile");
    }
  };

  return (
    <>
      <Sidebar side="right" className="border-l border-blue-200 bg-gradient-to-b from-blue-50 to-indigo-50">
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                {sidebarItems.map((item) => (
                  <SidebarMenuItem key={item.action}>
                    <SidebarMenuButton 
                      onClick={() => handleAction(item.action)}
                      className="w-full h-32 hover:bg-blue-100 hover:text-blue-700 transition-colors duration-200 flex-col gap-4 p-6"
                    >
                      <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center hover:bg-blue-200 transition-colors">
                        <item.icon className="w-8 h-8 text-blue-600" />
                      </div>
                      <span className="font-medium text-center text-blue-800">{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>

      <CreateCooklistDialog 
        open={createCooklistDialogOpen} 
        onOpenChange={setCreateCooklistDialogOpen} 
      />

      <CreateRecipeDialog 
        open={createRecipeDialogOpen} 
        onOpenChange={setCreateRecipeDialogOpen} 
      />
    </>
  );
}
